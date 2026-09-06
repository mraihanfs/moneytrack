from django.test import TestCase
from django.urls import reverse
from rest_framework_api_key.models import APIKey

from .models import Category


class CategoryViewTests(TestCase):
	def setUp(self):
		Category.objects.create(name='Food', is_active=True)
		Category.objects.create(name='Archived', is_active=False)

	def test_category_list_returns_only_active_categories(self):
		response = self.client.get(reverse('category-list'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json(), [
			{'id': Category.objects.get(name='Food').id, 'name': 'Food'},
		])


class TransactionViewTests(TestCase):
	def setUp(self):
		self.api_key, self.raw_api_key = APIKey.objects.create_key(
			name='test-client'
		)
		self.url = reverse('transaction-list')

	def test_transaction_list_requires_an_api_key(self):
		response = self.client.get(self.url)

		self.assertEqual(response.status_code, 403)

	def test_transaction_list_requires_data_range(self):
		response = self.client.get(
			self.url,
			HTTP_AUTHORIZATION=f'Api-Key {self.raw_api_key}',
		)

		self.assertEqual(response.status_code, 400)
		self.assertEqual(
			response.json(),
			{'message': 'Please input a valid query param'},
		)
