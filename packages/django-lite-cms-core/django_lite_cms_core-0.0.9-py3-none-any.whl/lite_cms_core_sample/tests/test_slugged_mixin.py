from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify
from faker import Faker

from lite_cms_core_sample.models import SluggedItem, SluggedItemFromName


class SluggedMixinTest(TestCase):

    def setUp(self) -> None:
        self.fake = Faker('de_DE')
        self.slugged_item = SluggedItem.objects.create(
            title=' '.join(self.fake.words()),
        )
        self.slugged_item_same_title = SluggedItem.objects.create(
            title=self.slugged_item.title,
        )
        self.slugged_item_name = SluggedItemFromName.objects.create(
            title=' '.join(self.fake.words()),
            name=' '.join(self.fake.words())[:100],
        )

    def test_slugged_item_has_status(self):
        self.assertTrue(hasattr(self.slugged_item, 'slug'))

    def test_slugged_item_has_title(self):
        self.assertTrue(hasattr(self.slugged_item, 'title'))

    def test_slugged_item_get_slug(self):
        self.assertEqual(self.slugged_item.get_slug(), self.slugged_item.slug)

    def test_slugged_item_colliding_title(self):
        self.assertEqual(
            f'{self.slugged_item.slug}-1',
            self.slugged_item_same_title.slug
        )

    def test_slugged_item_slug_from_default(self):
        # Default field for creating the slug is 'title'
        self.assertEqual(self.slugged_item.slug, slugify(self.slugged_item.title))

    def test_slugged_item_slug_from_name(self):
        self.assertEqual(self.slugged_item_name.slug, slugify(self.slugged_item_name.name))

    def test_slugged_item_get_absolute_url(self):
        self.assertEqual(
            self.slugged_item.get_absolute_url(),
            reverse(
                'slugged-item-detail',
                kwargs={'slug': self.slugged_item.slug}
            )
        )

    def test_slugged_item_admin_link(self):
        self.assertEqual(
            self.slugged_item.admin_link(),
            f"<a href='/slugged/{self.slugged_item.slug}/'>View on site</a>"
        )
