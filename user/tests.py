from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User


class UserRegistrationLoginTestCase(TestCase):
    def setUp(self):
        self.register_url = reverse('user-registration')
        self.login_url = reverse('user-login')
        self.user_data = {
            'email': 'test@example.com',
            'password': 'password123',
        }
        self.client = APIClient()

    def test_user_registration(self):
        """Test user registration API endpoint."""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'test@example.com')
        self.assertNotEqual(User.objects.get().password, 'password123')

    def test_user_login(self):
        """Test user login API endpoint."""
        data = self.user_data
        User.objects.create_user(**data)
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)


class UserProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password123')
        self.profile_url = reverse('user-profile', kwargs={'id': self.user.id})
        self.edit_url = reverse('user-profile-edit')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_user_profile_retrieval(self):
        """Test user profile retrieval API endpoint."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_other_user_profile_retrieval(self):
        """Test other than user logged profile retrieval API endpoint."""
        other_user = User.objects.create_user(email='other_user@example.com', password='password123')
        response = self.client.get(reverse('user-profile', kwargs={'id': other_user.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'other_user@example.com')

    def test_user_profile_edit(self):
        """Test user profile edit API endpoint."""
        data = {
            'email': 'updated@example.com',
            'password': 'newpassword123'
        }
        response = self.client.put(self.edit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertNotEqual(self.user.password, 'newpassword123')
        

class UserFollowUnfollowViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.user_to_follow = User.objects.create_user(email='user_to_follow@example.com', password='testpassword')
        self.follow_url = reverse('user-follow')
        self.unfollow_url = reverse('user-unfollow')
        
    def test_user_follow(self):
        """Test following another user."""
        url = self.follow_url
        user_id = self.user_to_follow.id
        payload = {'user_id':user_id}
        res = self.client.post(url,payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.following.count(), 1)
        self.assertEqual(self.user_to_follow.followers.count(), 1)
    
    def test_user_unfollow(self):
        """Test unfollowing another user."""
        url_follow = self.follow_url
        url_unfollow = self.unfollow_url
        
        user_id = self.user_to_follow.id
        
        payload = {'user_id':user_id}
        res_follow = self.client.post(url_follow,payload)
        res_unfollow = self.client.delete(url_unfollow, payload)
        
        self.assertEqual(res_unfollow.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.following.count(), 0)
        self.assertEqual(self.user_to_follow.followers.count(), 0)