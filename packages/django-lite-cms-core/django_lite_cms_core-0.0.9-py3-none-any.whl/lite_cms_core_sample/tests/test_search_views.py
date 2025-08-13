from django.test import TestCase
from django.urls import reverse
from faker import Faker

from lite_cms_core.models import BaseEntity
from lite_cms_core_sample.models import ContentItem, SluggedItem


class BaseEntitySearchViewTest(TestCase):

    def setUp(self) -> None:
        self.fake = Faker('de_DE')
        self.search_string = 'ABCDEF'
        self.content_item = ContentItem.objects.create(
            title=' '.join(self.fake.words()),
            content=f'<p>{self.fake.paragraph(nb_sentences=5)}</p>'
        )
        self.content_item = ContentItem.objects.create(
            title=' '.join(self.fake.words()),
            content=(
                f'<p>{self.fake.paragraph(nb_sentences=3)}</p>',
                f'<p>{self.search_string}</p>',
                f'<p>{self.fake.paragraph(nb_sentences=3)}</p>',
            )
        )
        self.slugged_item = SluggedItem.objects.create(
            title=' '.join(self.fake.words()) + self.search_string,
        )

    def test_search_view_all_models(self):
        url = reverse('lite_cms_core:search')
        response = self.client.get(f'{url}?q={self.search_string}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['results']), 2)
        self.assertIsInstance(response.context['results'][0], BaseEntity)
        self.assertQuerySetEqual(
            response.context['results'][1:],
            ContentItem.objects.filter(content__contains=self.search_string),
        )

    def test_search_view_for_model(self):
        url = reverse('lite_cms_core:search')
        response = self.client.get(f'{url}?q={self.search_string}&type=lite_cms_core_sample.ContentItem')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['results']), 1)
        self.assertTemplateUsed('lite_cms_core/search_results.html')
        self.assertQuerySetEqual(
            response.context['results'],
            ContentItem.objects.filter(content__contains=self.search_string),
        )

    def test_search_form_get(self):
        url = reverse('lite_cms_core:extsearch')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('lite_cms_core/ext_search_form.html')
