# -*- coding: utf-8 -*-
"""Django Lite CMS Managers."""
from functools import reduce
from operator import ior, iand
from string import punctuation

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Manager, QuerySet, Q, CharField, TextField
from django.db.models.manager import ManagerDescriptor
from django.utils.timezone import now


class PublishedManager(Manager):
    """For non-staff users, return items with a published status."""

    def published(self, for_user=None):
        """
        Return a QuerySet of published items.

        An item is published if it has the status CONTENT_STATUS_PUBLISHED and
        the pusblish_date is lower or equal to *now* and the expiry_date is
        grater or equal to *now*. If the publish_date or the expiry_date is None,
        they will be ignored.

        Not published items will only be returned for staff users.
        """
        if for_user is not None and for_user.is_staff:
            return self.all()
        return self.filter(
            Q(publish_date__lte=now()) | Q(publish_date__isnull=True),
            Q(expiry_date__gte=now()) | Q(expiry_date__isnull=True),
            # due to circular imports use the "2" instead of CONTENT_STATUS_PUBLISHED
            status=2
        )

    def get_by_natural_key(self, slug):
        """Return item by natural key."""
        return self.get(slug=slug)


STOP_WORDS = (
    "a", "about", "above", "above", "across", "after",
    "afterwards", "again", "against", "all", "almost", "alone",
    "along", "already", "also", "although", "always", "am",
    "among", "amongst", "amoungst", "amount", "an", "and",
    "another", "any", "anyhow", "anyone", "anything", "anyway",
    "anywhere", "are", "around", "as", "at", "back", "be",
    "became", "because", "become", "becomes", "becoming", "been",
    "before", "beforehand", "behind", "being", "below", "beside",
    "besides", "between", "beyond", "bill", "both", "bottom",
    "but", "by", "call", "can", "cannot", "cant", "co", "con",
    "could", "couldnt", "cry", "de", "describe", "detail", "do",
    "done", "down", "due", "during", "each", "eg", "eight",
    "either", "eleven", "else", "elsewhere", "empty", "enough",
    "etc", "even", "ever", "every", "everyone", "everything",
    "everywhere", "except", "few", "fifteen", "fifty", "fill",
    "find", "fire", "first", "five", "for", "former", "formerly",
    "forty", "found", "four", "from", "front", "full", "further",
    "get", "give", "go", "had", "has", "hasnt", "have", "he",
    "hence", "her", "here", "hereafter", "hereby", "herein",
    "hereupon", "hers", "herself", "him", "himself", "his",
    "how", "however", "hundred", "ie", "if", "in", "inc",
    "indeed", "interest", "into", "is", "it", "its", "itself",
    "keep", "last", "latter", "latterly", "least", "less", "ltd",
    "made", "many", "may", "me", "meanwhile", "might", "mill",
    "mine", "more", "moreover", "most", "mostly", "move", "much",
    "must", "my", "myself", "name", "namely", "neither", "never",
    "nevertheless", "next", "nine", "no", "nobody", "none",
    "noone", "nor", "not", "nothing", "now", "nowhere", "of",
    "off", "often", "on", "once", "one", "only", "onto", "or",
    "other", "others", "otherwise", "our", "ours", "ourselves",
    "out", "over", "own", "part", "per", "perhaps", "please",
    "put", "rather", "re", "same", "see", "seem", "seemed",
    "seeming", "seems", "serious", "several", "she", "should",
    "show", "side", "since", "sincere", "six", "sixty", "so",
    "some", "somehow", "someone", "something", "sometime",
    "sometimes", "somewhere", "still", "such", "system", "take",
    "ten", "than", "that", "the", "their", "them", "themselves",
    "then", "thence", "there", "thereafter", "thereby",
    "therefore", "therein", "thereupon", "these", "they",
    "thickv", "thin", "third", "this", "those", "though",
    "three", "through", "throughout", "thru", "thus", "to",
    "together", "too", "top", "toward", "towards", "twelve",
    "twenty", "two", "un", "under", "until", "up", "upon", "us",
    "very", "via", "was", "we", "well", "were", "what", "whatever",
    "when", "whence", "whenever", "where", "whereafter", "whereas",
    "whereby", "wherein", "whereupon", "wherever", "whether",
    "which", "while", "whither", "who", "whoever", "whole", "whom",
    "whose", "why", "will", "with", "within", "without", "would",
    "yet", "you", "your", "yours", "yourself", "yourselves", "the",
)


def search_fields_to_dict(fields):
    """
    Convert search fields to a dictionary.

    In ``SearchableQuerySet`` and ``SearchableManager``, search fields
    can either be a sequence, or a dict of fields mapped to weights.
    This function converts sequences to a dict mapped to even weights,
    so that we're consistently dealing with a dict of fields mapped to
    weights, eg: ("title", "content") -> {"title": 1, "content": 1}
    """
    if not fields:
        return {}
    try:
        int(next(iter(dict(fields).values())))
    except (TypeError, ValueError):
        fields = dict(zip(fields, [1] * len(fields)))
    return fields


class SearchableQuerySet(QuerySet):
    """QuerySet providing main search functionality for ``SearchableManager``."""

    def __init__(self, *args, **kwargs):
        """Init SearchableQuerySet."""
        self._search_ordered = False
        self._search_terms = set()
        self._search_fields = kwargs.pop("search_fields", {})
        super().__init__(*args, **kwargs)

    def search(self, query, search_fields=None):
        """
        Do the search on SearchableQuerySet.

        Build a queryset matching words in the given search query,
        treating quoted terms as exact phrases and taking into
        account + and - symbols as modifiers controlling which terms
        to require and exclude.
        """
        # ### DETERMINE FIELDS TO SEARCH ###

        # Use search_fields arg if given, otherwise use search_fields
        # initially configured by the manager class.
        if search_fields:
            self._search_fields = search_fields_to_dict(search_fields)
        if not self._search_fields:
            return self.none()

        # ### BUILD LIST OF TERMS TO SEARCH FOR ###

        # Remove extra spaces, put modifiers inside quoted terms.
        terms = " ".join(query.split()).replace("+ ", "+")     \
                                       .replace('+"', '"+')    \
                                       .replace("- ", "-")     \
                                       .replace('-"', '"-')    \
                                       .split('"')
        # Strip punctuation other than modifiers from terms and create
        # terms list, first from quoted terms and then remaining words.
        terms = [("" if t[0:1] not in "+-" else t[0:1]) + t.strip(punctuation)
            for t in terms[1::2] + "".join(terms[::2]).split()]
        # Remove stop words from terms that aren't quoted or use
        # modifiers, since words with these are an explicit part of
        # the search query. If doing so ends up with an empty term
        # list, then keep the stop words.
        terms_no_stopwords = [t for t in terms if t.lower() not in STOP_WORDS]
        # pylint: disable=unnecessary-lambda-assignment
        def get_positive_terms(terms):
            return [t.lower().strip(punctuation) for t in terms if t[0:1] != "-"]
        positive_terms = get_positive_terms(terms_no_stopwords)
        if positive_terms:
            terms = terms_no_stopwords
        else:
            positive_terms = get_positive_terms(terms)
        # Append positive terms (those without the negative modifier)
        # to the internal list for sorting when results are iterated.
        if not positive_terms:
            return self.none()

        self._search_terms.update(positive_terms)

        # ### BUILD QUERYSET FILTER ###

        # Create the queryset combining each set of terms.
        # pylint: disable=consider-using-f-string
        excluded = [reduce(iand, [~Q(**{"%s__icontains" % f: t[1:]}) for f in
            self._search_fields.keys()]) for t in terms if t[0:1] == "-"]
        required = [reduce(ior, [Q(**{"%s__icontains" % f: t[1:]}) for f in
            self._search_fields.keys()]) for t in terms if t[0:1] == "+"]
        optional = [reduce(ior, [Q(**{"%s__icontains" % f: t}) for f in
            self._search_fields.keys()]) for t in terms if t[0:1] not in "+-"]
        queryset = self
        if excluded:
            queryset = queryset.filter(reduce(iand, excluded))
        if required:
            queryset = queryset.filter(reduce(iand, required))
        # Optional terms aren't relevant to the filter if there are
        # terms that are explicitly required.
        elif optional:
            queryset = queryset.filter(reduce(ior, optional))
        return queryset.distinct()

    def _clone(self):
        """Ensure attributes are copied to subsequent queries."""
        clone = super()._clone()
        clone._search_terms = self._search_terms
        clone._search_fields = self._search_fields
        clone._search_ordered = self._search_ordered
        return clone

    def order_by(self, *field_names):
        """Mark the filter as being ordered if search has occurred."""
        if not self._search_ordered:
            self._search_ordered = len(self._search_terms) > 0
        return super().order_by(*field_names)

    def annotate_scores(self):
        """
        Annotate SearchableQuerySet with scores.

        If search has occurred and no ordering has occurred, decorate
        each result with the number of search terms so that it can be
        sorted by the number of occurrence of terms.

        In the case of search fields that span model relationships, we
        cannot accurately match occurrences without some very
        complicated traversal code, which we won't attempt. So in this
        case, namely when there are no matches for a result (count=0),
        and search fields contain relationships (double underscores),
        we assume one match for one of the fields, and use the average
        weight of all search fields with relationships.
        """
        results = super().iterator()
        if self._search_terms and not self._search_ordered:
            results = list(results)
            for result in results:
                count = 0
                related_weights = []
                for (field, weight) in self._search_fields.items():
                    if "__" in field:
                        related_weights.append(weight)
                    for term in self._search_terms:
                        field_value = getattr(result, field, None)
                        if field_value:
                            count += field_value.lower().count(term) * weight
                if not count and related_weights:
                    count = int(sum(related_weights) / len(related_weights))

                result.result_count = count
            return iter(results)
        return results


class SearchableManager(Manager):
    """
    Manager providing a chainable queryset.

    Adapted from http://www.djangosnippets.org/snippets/562/
    search method supports spanning across models that subclass the
    model being used to search.
    """

    def __init__(self, *args, **kwargs):
        """Init SearchableManager."""
        self._search_fields = kwargs.pop("search_fields", {})
        super().__init__(*args, **kwargs)

    def get_search_fields(self):
        """
        Returns the search field names mapped to weights as a dict.

        Used in ``get_queryset`` below to tell ``SearchableQuerySet``
        which search fields to use.

        Search fields can be populated via
        ``SearchableManager.__init__``, which then get stored in
        ``SearchableManager._search_fields``, which serves as an
        approach for defining an explicit set of fields to be used.

        Alternatively and more commonly, ``search_fields`` can be
        defined on models themselves. In this case, we look at the
        model and all its base classes, and build up the search
        fields from all of those, so the search fields are implicitly
        built up from the inheritence chain.

        Finally if no search fields have been defined at all, we
        fall back to any fields that are ``CharField`` or ``TextField``
        instances.
        """
        search_fields = self._search_fields.copy()
        if not search_fields:
            for cls in reversed(self.model.__mro__):
                super_fields = getattr(cls, "search_fields", {})
                search_fields.update(search_fields_to_dict(super_fields))
        if not search_fields:
            search_fields = []
            for field in self.model._meta.get_fields():
                if isinstance(field, (CharField, TextField)):
                    search_fields.append(field.name)
            search_fields = search_fields_to_dict(search_fields)
        return search_fields

    def get_queryset(self):
        """Get searchable queryset."""
        search_fields = self.get_search_fields()
        return SearchableQuerySet(self.model, search_fields=search_fields)

    def contribute_to_class(self, model, name):
        """
        Reinstate class.

        Newer versions of Django explicitly prevent managers being
        accessed from abstract classes, which is behaviour the search
        API has always relied on. Here we reinstate it.
        """
        super().contribute_to_class(model, name)
        setattr(model, name, ManagerDescriptor(self))

    def search(self, *args, **kwargs):
        """
        Proxy to queryset's search method for the manager's model.

        Also for any models that subclass from this manager's model if the model is abstract.
        """
        if not settings.SEARCH_MODEL_CHOICES:
            # No choices defined - build a list of leaf models (those
            # without subclasses) that inherit from Displayable.
            models = [m for m in apps.get_models()
                      if issubclass(m, self.model)]
            parents = reduce(ior, [set(m._meta.get_parent_list())
                                   for m in models])
            models = [m for m in models if m not in parents]
        elif getattr(self.model._meta, "abstract", False):
            # When we're combining model subclasses for an abstract
            # model, we only want to use models that
            # are represented by the ``SEARCH_MODEL_CHOICES`` setting.
            # Now this setting won't contain an exact list of models
            # we should use, since it can define superclass models such
            # as ``Page``, so we check the parent class list of each
            # model when determining whether a model falls within the
            # ``SEARCH_MODEL_CHOICES`` setting.
            search_choices = set()
            models = set()
            parents = set()
            errors = []
            for name in settings.SEARCH_MODEL_CHOICES:
                try:
                    model = apps.get_model(*name.split(".", 1))
                except LookupError:
                    errors.append(name)
                else:
                    search_choices.add(model)
            if errors:
                msg = "Could not load the model(s) {', '.join(errors)} defined in the 'SEARCH_MODEL_CHOICES' setting."
                raise ImproperlyConfigured(
                    msg
                )

            for model in apps.get_models():
                # Model is actually a subclasses of what we're
                # searching (eg Displayabale)
                is_subclass = issubclass(model, self.model)
                # Model satisfies the search choices list - either
                # there are no search choices, model is directly in
                # search choices, or its parent is.
                this_parents = set(model._meta.get_parent_list())
                in_choices = not search_choices or model in search_choices
                in_choices = in_choices or this_parents & search_choices
                if is_subclass and (in_choices or not search_choices):
                    # Add to models we'll seach. Also maintain a parent
                    # set, used below for further refinement of models
                    # list to search.
                    models.add(model)
                    parents.update(this_parents)
            # Strip out any models that are superclasses of models,
            # specifically the Page model which will generally be the
            # superclass for all custom content types, since if we
            # query the Page model as well, we will get duplicate
            # results.
            models -= parents
        else:
            models = [self.model]
        all_results = []
        user = kwargs.pop("for_user", None)
        for model in models:
            try:
                queryset = model.objects.published(for_user=user)
            except AttributeError:
                queryset = model.objects.get_queryset()
            all_results.extend(
                queryset.search(*args, **kwargs).annotate_scores())
        return sorted(all_results, key=lambda r: r.result_count, reverse=True)


class BaseEntityManager(PublishedManager, SearchableManager):
    """Manually combines ``PublishedManager`` and ``SearchableManager`` for the ``BaseEntity`` model."""
