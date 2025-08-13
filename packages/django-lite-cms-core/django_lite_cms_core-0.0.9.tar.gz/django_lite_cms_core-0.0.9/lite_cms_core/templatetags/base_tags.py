"""Django Lite CMS base template tags."""
from django import template
from django.apps import apps
from django.urls import reverse
from django.conf import settings

register = template.Library()


@register.inclusion_tag('lite_cms_core/includes/edit_toolbar.html')
def edit_toolbar(model_instance=None, permission=False):
    """Shows the editable toolbar and adds an admin edit link, if model instance is not None."""
    admin_edit_link = None
    if model_instance and permission:
        edit_link_name = f'admin:{model_instance._meta.app_label}_{model_instance._meta.model_name}_change'
        admin_edit_link = reverse(edit_link_name, args=[model_instance.pk])
    return {'admin_edit_link': admin_edit_link}


@register.inclusion_tag("lite_cms_core/includes/search_form.html", takes_context=True)
def search_form(context, search_model_names=None):
    """
    Includes the search form with a list of models to use as choices for filtering the search by.

    Models should be a string with models
    in the format ``app_label.model_name`` separated by spaces. The
    string ``all`` can also be used, in which case the models defined
    by the ``SEARCH_MODEL_CHOICES`` setting will be used.
    """
    template_vars = {
        "request": context["request"],
    }
    if not search_model_names or not settings.SEARCH_MODEL_CHOICES:
        search_model_names = []
    elif search_model_names == "all":
        search_model_names = list(settings.SEARCH_MODEL_CHOICES)
    else:
        search_model_names = search_model_names.split(" ")
    search_model_choices = []
    for model_name in search_model_names:
        try:
            model = apps.get_model(*model_name.split(".", 1))
        except LookupError:
            pass
        else:
            verbose_name = model._meta.verbose_name_plural.capitalize()
            search_model_choices.append((verbose_name, model_name))
    template_vars["search_model_choices"] = sorted(search_model_choices)
    return template_vars


@register.filter
def get_search_type(instance):
    """Get the content type for a model instance."""
    from django.contrib.contenttypes.models import ContentType  # noqa: PLC0415
    typus = ContentType.objects.get_for_model(instance)
    return typus.name
