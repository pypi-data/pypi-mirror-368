from django.contrib.auth.models import User
from django.template import Context
from django.test import TestCase, RequestFactory
from django.urls import reverse
from faker import Faker

from lite_cms_core.templatetags import base_tags
from lite_cms_core_sample.models import SluggedItem


class TemplateTagTest(TestCase):

    def setUp(self) -> None:
        self.fake = Faker('de_DE')

        self.user = User.objects.create_user(
            username=self.fake.user_name(),
        )

        factory = RequestFactory()
        self.request = factory.get(reverse('home'))
        self.context = Context()
        self.request.user = self.user
        self.context['request'] = self.request

        self.slugged_item = SluggedItem.objects.create(
            title=' '.join(self.fake.words()),
        )

    def test_edit_toolar_tag_no_params(self):
        self.assertIsNone(base_tags.edit_toolbar()['admin_edit_link'])

    def test_edit_toolar_tag_model_instance(self):
        result = base_tags.edit_toolbar(
            model_instance=self.slugged_item,
            permission=True
        )
        self.assertEqual(
            result['admin_edit_link'],
            f'/admin/lite_cms_core_sample/sluggeditem/{self.slugged_item.pk}/change/'
        )

    def test_search_form_tag_model_none(self):
        response = base_tags.search_form(self.context)
        self.assertEqual(len(response['search_model_choices']), 0)
        self.assertQuerySetEqual(
            response['search_model_choices'],
            []
        )

    def test_search_form_tag_all_models(self):
        response = base_tags.search_form(self.context, search_model_names='all')
        self.assertEqual(len(response['search_model_choices']), 2)
        self.assertQuerySetEqual(
            response['search_model_choices'],
            [
                ('Base items', 'lite_cms_core_sample.BaseItem'),
                ('Content items', 'lite_cms_core_sample.ContentItem')
            ]
        )

    def test_search_form_tag_one_model(self):
        response = base_tags.search_form(self.context, search_model_names='lite_cms_core_sample.ContentItem')
        self.assertEqual(len(response['search_model_choices']), 1)
        self.assertQuerySetEqual(
            response['search_model_choices'],
            [('Content items', 'lite_cms_core_sample.ContentItem')]
        )
