
"""Django Lite CMS base classes."""
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import Http404
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from tinymce.models import HTMLField

from lite_cms_core.managers import BaseEntityManager


CONTENT_STATUS_DRAFT = 1
CONTENT_STATUS_PUBLISHED = 2
CONTENT_STATUS_CHOICES = (
    (CONTENT_STATUS_DRAFT, _("Draft")),
    (CONTENT_STATUS_PUBLISHED, _("Published")),
)


def wrapped_manager(klass):
    """Combine Manager with MultilungualManager."""
    if getattr(settings, "USE_MODELTRANSLATION", False):
        from modeltranslation.manager import MultilingualManager  # noqa: PLC0415
        class Mgr(MultilingualManager, klass):
            pass
        return Mgr()
    return klass()


def _base_concrete_model(abstract, klass):
    for kls in reversed(klass.__mro__):
        if issubclass(kls, abstract) and not kls._meta.abstract:
            return kls
    return None


def base_concrete_model(abstract, model):
    """
    Get super-most concrete class.

    Used in methods of abstract models to find the super-most concrete
    (non abstract) model in the inheritance chain that inherits from the
    given abstract model. This is so the methods in the abstract model can
    query data consistently across the correct concrete model.

    Consider the following::

        class Abstract(models.Model)

            class Meta:
                abstract = True

            def concrete(self):
                return base_concrete_model(Abstract, self)

        class Super(Abstract):
            pass

        class Sub(Super):
            pass

        sub = Sub.objects.create()
        sub.concrete() # returns Super

    """
    if hasattr(model, 'objects'):
        # "model" is a model class
        return (model if model._meta.abstract else
                _base_concrete_model(abstract, model))
    # "model" is a model instance
    return (
        _base_concrete_model(abstract, model.__class__) or
        model.__class__
    )


def unique_slug(queryset, slug_field, slug):
    """
    Calculate a unique slug from string field.

    Ensures a slug is unique for the given queryset, appending
    an integer to its end until the slug is unique.
    """
    i = 0
    while True:
        if i > 0:
            if i > 1:
                slug = slug.rsplit("-", 1)[0]
            slug = f"{slug}-{i}"
        try:
            queryset.get(**{slug_field: slug})
        except ObjectDoesNotExist:
            break
        i += 1
    return slug


class BaseEntity(models.Model):
    """Abstract base model for basic cms funcionality."""

    class Meta:
        abstract = True

    def __str__(self):
        """Get string representation of instance."""
        return self.title

    #: Title of the entity, string with a maxlen of 200.
    title = models.CharField(
        max_length=200, verbose_name=_("Title")
    )
    #: The status of the entity, one of CONTENT_STATUS_DRAFT or CONTENT_STATUS_PUBLISHED
    status = models.IntegerField(
        verbose_name=_("Status"),
        choices=CONTENT_STATUS_CHOICES, default=CONTENT_STATUS_PUBLISHED,
        help_text=_("With Draft chosen, will only be shown for admin users on the site.")
    )
    #: Time and date when the entity is or will be published.
    publish_date = models.DateTimeField(
        _("Published from"),
        help_text=_("With Published chosen, won't be shown until this time"),
        blank=True, null=True, db_index=True
    )
    #: Time and date when the entity is expired, so will not be seen by users anymore.
    expiry_date = models.DateTimeField(
        _("Expires on"),
        help_text=_("With Published chosen, won't be shown after this time"),
        blank=True, null=True
    )

    objects = wrapped_manager(BaseEntityManager)

    @property
    def published(self):
        """
        Get only *published* instances.

        For non-staff users, return True when status is published and
        the publish and expiry dates fall before and after the
        current date when specified.
        """
        return (self.status == CONTENT_STATUS_PUBLISHED and
                (self.publish_date is None or self.publish_date <= now()) and
                (self.expiry_date is None or self.expiry_date >= now()))

    def _get_next_or_previous_by_publish_date(self, is_next, **kwargs):
        """
        Navigate through instances by pubish date.

        Retrieves next or previous object by publish date. We implement
        our own version instead of Django's so we can hook into the
        published manager and concrete subclasses.
        """
        arg = "publish_date__gt" if is_next else "publish_date__lt"
        order = "publish_date" if is_next else "-publish_date"
        lookup = {arg: self.publish_date}
        concrete_model = base_concrete_model(BaseEntity, self)
        try:
            queryset = concrete_model.objects.published
        except AttributeError:
            queryset = concrete_model.objects.all
        try:
            return queryset(**kwargs).filter(**lookup).order_by(order)[0]
        except IndexError:
            pass
        return None

    def get_next_by_publish_date(self, **kwargs):
        """Retrieves next object by publish date."""
        return self._get_next_or_previous_by_publish_date(True, **kwargs)

    def get_previous_by_publish_date(self, **kwargs):
        """Retrieves previous object by publish date."""
        return self._get_next_or_previous_by_publish_date(False, **kwargs)

    def get_absolute_url(self):
        """
        Get the absolute url for this object.

        Raise an error if called on a subclass without
        ``get_absolute_url`` defined, to ensure all search results
        contains a URL.
        """
        name = self.__class__.__name__
        msg = f"The model {name} does not have get_absolute_url defined"
        raise NotImplementedError(
            msg
        )

    def save(self, *args, **kwargs):
        """
        Save instance of base class.

        If no ``publish_date`` is provided set it to *now*.
        """
        if not self.publish_date:
            self.publish_date = now()
        super().save(*args, **kwargs)


class SluggedMixin(models.Model):
    """
    Abstract model that handles auto-generating slugs.

    In default the slug is generated from the title attribute. You can
    specify a different attribute by overriding the ``get_slug()`` method.
    if you want to get the slug from a ``name`` attribute, add this to your class::

            def get_slug(self, attr=None):
                return super().get_slug(attr="name")

    If any instance has the same title as another instance, a
    unique slug is automatically generated by adding a dash and a number.
    """

    slug = models.SlugField(
        max_length=200, blank=True, unique=True,
        help_text=_('Is generated if no value has been specified')
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """If no slug is provided, generates one before saving."""
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)

    def generate_unique_slug(self):
        """
        Create a unique slug for colliding sources.

        Create a unique slug by passing the result of get_slug() to
        utils.urls.unique_slug, which appends an index if necessary.
        """
        concrete_model = base_concrete_model(SluggedMixin, self)
        slug_qs = concrete_model.objects.exclude(id=self.id)
        return unique_slug(slug_qs, "slug", self.get_slug())

    def get_slug(self, attr=None):
        """
        Get a unique slug.

        Allows subclasses to implement their own slug creation logic.
        In default a model 'title' field is required
        """
        if attr is None:
            attr = "title"
        if settings.USE_MODELTRANSLATION:
            # pylint: disable=import-error, import-outside-toplevel
            from modeltranslation.utils import build_localized_fieldname  # noqa: PLC0415
            attr = build_localized_fieldname(attr, settings.LANGUAGE_CODE)
        return slugify(getattr(self, attr, None) or self.title)

    def admin_link(self):
        """Provides a "view on site" link for the admin site."""
        return mark_safe(
            f"<a href='{self.get_absolute_url()}'>{_('View on site')}</a>"
        )
    admin_link.short_description = ""


class TimeStampedMixin(models.Model):
    """
    Provides timestamps for ``created`` and ``modified`` fields.

    Both fields are read-only.
    """

    class Meta:
        abstract = True

    #: Time and date when the instance was created.
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Created'))
    #: Time and date of the latest change of the instance.
    changed = models.DateTimeField(auto_now=True, verbose_name=_('Changed'))


class ContentFieldMixin(models.Model):
    """Get a HTML edit field in model."""

    class Meta:
        abstract = True

    content = HTMLField(verbose_name=_("Content"), null=True, blank=True)


class AdminOrderMixin(models.Model):
    """
    Let the user order the model instances in admin.

    The mixin adds a sort_order positive integer field to the class,
    which is a prerequisite for the django-admin-sortable2 module.

    Since inner classes are not inherited, it would make no
    sense to set the ordering here. So it's up to you to set the
    ordering to ``ordering = ['sort_order']``.

    In the admin please inherit from ``SortableAdminMixin`` as described
    in the docs of django-admin-sortable2.
    """

    class Meta:
        abstract = True

    sort_order = models.PositiveIntegerField(default=0)


class PreventUnpublishedAccessDetailView(DetailView):
    """
    Prenvet non staff usere form accessing draft items in ``DetailView``.

    In default an admin user will be shown model instances in both status,
    ``draft`` and ``published``. Non staff users will not be shown any
    draft items in the admin ui or in any lists that use the .published method.

    The normal ``DetailView`` will not refer to the ``published`` method but more to
    the ``get_absolute_url`` method. If you want to hide the *draft* items from
    non-staff users, you can use this subclass of the Django ``DetailView``.
    """

    def dispatch(self, request, *args, **kwargs):
        """Show HTTP 404 for not published items."""
        if not request.user.is_staff:
            if not self.get_object().published:
                raise Http404
        return super().dispatch(request, *args, **kwargs)
