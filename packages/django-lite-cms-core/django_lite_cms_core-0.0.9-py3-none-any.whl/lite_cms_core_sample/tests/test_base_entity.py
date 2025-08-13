from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from faker import Faker

from lite_cms_core.models import CONTENT_STATUS_DRAFT
from lite_cms_core_sample.models import BaseItem


class BaseEntityTest(TestCase):

    def setUp(self) -> None:
        self.fake = Faker('de_DE')
        self.base_item = BaseItem.objects.create(
            title=' '.join(self.fake.words()),
        )

    def test_base_item_str(self):
        self.assertEqual(self.base_item.__str__(), self.base_item.title)

    def test_base_item_save_sets_publish_date(self):
        td = now() - self.base_item.publish_date
        # 1 minute ago counts as equal here...
        self.assertTrue(td < timedelta(minutes=1))

    def test_base_item_has_status(self):
        self.assertTrue(hasattr(self.base_item, 'status'))

    def test_base_item_is_published(self):
        # Status default for BaseEntity is CONTENT_STATUS_PUBLISHED
        self.assertTrue(self.base_item.published)

    def test_base_item_not_published_by_status(self):
        self.base_item.status = CONTENT_STATUS_DRAFT
        self.base_item.save()
        self.assertFalse(self.base_item.published)

    def test_base_item_has_date_fields(self):
        self.assertTrue(hasattr(self.base_item, 'publish_date'))
        self.assertTrue(hasattr(self.base_item, 'expiry_date'))

    def test_base_item_not_published_by_publish_date(self):
        self.base_item.publish_date = now() + timedelta(days=1)
        self.base_item.save()
        self.assertFalse(self.base_item.published)

    def test_base_item_not_published_by_expiry_date(self):
        self.base_item.expiry_date = now() - timedelta(days=1)
        self.base_item.save()
        self.assertFalse(self.base_item.published)

    def test_base_item_get_next_by_publish_date(self):
        self.base_item.publish_date = now() - timedelta(days=2)
        self.base_item.save()
        newer_base_item = BaseItem.objects.create(
            title=' '.join(self.fake.words()),
            publish_date=now() - timedelta(days=1),
        )
        self.assertEqual(
            self.base_item.get_next_by_publish_date(),
            newer_base_item,
        )

    def test_base_item_get_previous_by_expiry_date(self):
        self.base_item.publish_date = now() - timedelta(days=1)
        self.base_item.save()
        older_base_item = BaseItem.objects.create(
            title=' '.join(self.fake.words()),
            publish_date=now() - timedelta(days=2),
        )
        self.assertEqual(
            self.base_item.get_previous_by_publish_date(),
            older_base_item,
        )

    def test_base_item_get_absolute_url(self):
        self.assertEqual(
            self.base_item.get_absolute_url(),
            reverse('base-item-detail', kwargs={'pk': self.base_item.pk})
        )


class BaseEntityManagerTest(TestCase):

    def setUp(self) -> None:
        self.fake = Faker('de_DE')
        for _ in range(5):
            BaseItem.objects.create(
                title=' '.join(self.fake.words()),
            )
        self.base_item = BaseItem.objects.create(
            title='This is a text for testing',
        )

    def test_base_item_search(self):
        self.assertEqual(
            BaseItem.objects.search('testing'),
            [self.base_item],
        )

    def test_base_item_search_with_search_fields(self):
        self.assertEqual(
            BaseItem.objects.search('testing', search_fields=['title']),
            [self.base_item],
        )
