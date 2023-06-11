from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User

class UserRegistrationLoginTestCase(APITestCase):
    def test_user_registration(self):
        url = reverse('user-registration')
        data = {
            'email': 'test@example.com',
            'password': 'password123',
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')
        self.assertNotEqual(User.objects.get().password, 'password123')

    def test_user_login(self):
        data = {
            'email': 'test@example.com',
            'password': 'password123'
        }

        User.objects.create_user(**data)
        url = reverse('user-login')

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
