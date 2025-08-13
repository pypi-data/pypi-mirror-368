"""Django Lite CMS Views."""
from operator import itemgetter

from django.apps import apps
from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


def search(request, template="lite_cms_core/search_results.html", extra_context=None):
    """
    Display search results.

    Takes an optional "contenttype" GET parameter in the form "app-name.ModelName"
    to limit search results to a single model.
    """
    query = request.GET.get("q", "")
    try:
        parts = request.GET.get("type", "").split(".", 1)
        search_model = apps.get_model(*parts)
    except (ValueError, TypeError, LookupError, AttributeError):
        search_types = settings.SEARCH_MODEL_CHOICES
        results = []
        for search_type in search_types:
            parts = search_type.split(".", 1)
            search_model = apps.get_model(*parts)
            results += search_model.objects.search(query, for_user=request.user)
        search_type = _("Everything")
    else:
        search_type = search_model._meta.verbose_name_plural.capitalize()
        results = search_model.objects.search(query, for_user=request.user)

    paginator = Paginator(results, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {"query": query, "results": page_obj,
               "search_type": search_type, 'total': len(results)}
    context.update(extra_context or {})
    return render(request, template, context)


def ext_search_form(request):
    """
    Extended search form.

    The extended search form lets users select a model to search on.
    """
    choices = set()
    for name in settings.SEARCH_MODEL_CHOICES:
        try:
            model = apps.get_model(*name.split(".", 1))
            model_name = model._meta.verbose_name.title()
        except LookupError:
            pass
        else:
            choices.add((model_name, name))
    search_choices = list(choices)
    # sort by localized name
    search_choices.sort(key=itemgetter(0))
    return render(request, 'lite_cms_core/ext_search_form.html', {
        'search_model_choices': search_choices
    })
