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
    
    def setUp(self):
        self.register_url = reverse('user-registration')
        self.login_url = reverse('user-login')
        self.user_data = {
            'email': 'test@example.com',
            'password': 'password123',
        }
    def test_user_registration(self):

        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')
        self.assertNotEqual(User.objects.get().password, 'password123')

    def test_user_login(self):
        data = self.user_data
        User.objects.create_user(**data)
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
