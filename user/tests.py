from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User, Post


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
        self.payload = {'user_id': self.user_to_follow.id}
        self.non_existent_user_id = 9999  # ID of a non-existent user

    def _follow_user(self):
        return self.client.post(self.follow_url, self.payload)

    def _assertions_state_follow_count(self, res, count, status=status.HTTP_200_OK):
        self.assertEqual(res.status_code, status)
        self.assertEqual(self.user.following.count(), count)
        self.assertEqual(self.user_to_follow.followers.count(), count)

    def test_user_follow(self):
        """Test following another user."""
        res = self._follow_user()
        self._assertions_state_follow_count(res=res, count=1, status=status.HTTP_200_OK)

    def test_user_unfollow(self):
        """Test unfollowing another user."""
        res_follow = self._follow_user()
        res_unfollow = self.client.delete(self.unfollow_url, self.payload)
        self._assertions_state_follow_count(res=res_unfollow, count=0, status=status.HTTP_200_OK)

    def test_follow_nonexistent_user(self):
        """Test following a non-existent user."""
        self.payload['user_id'] = self.non_existent_user_id
        res = self._follow_user()
        self._assertions_state_follow_count(res, 0, status.HTTP_404_NOT_FOUND)

    def test_unfollow_nonexistent_user(self):
        """Test unfollowing a non-existent user."""
        non_existent_user_id = 9999  # ID of a non-existent user
        self.payload['user_id'] = self.non_existent_user_id
        res_unfollow = self.client.delete(self.unfollow_url, self.payload)
        self._assertions_state_follow_count(res=res_unfollow, count=0, status=status.HTTP_404_NOT_FOUND)

    def test_unfollow_user_not_followed(self):
        """Test unfollowing a user that is not being followed."""
        user_to_unfollow = User.objects.create_user(email='user_to_unfollow@example.com', password='testpassword')
        payload = {'user_id': user_to_unfollow.id}
        res_unfollow = self.client.delete(self.unfollow_url, payload)
        self._assertions_state_follow_count(res=res_unfollow, count=0, status=status.HTTP_400_BAD_REQUEST)


class UserCRUDPostTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@example.com', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.user2 = User.objects.create_user(email='user2@example.com', password='testpassword')
        self.url = reverse('posts-list')
        self.payload = {'text': 'Test'}

    def _create_a_post(self):
        return self.client.post(self.url, self.payload)

    def test_user_create_a_post_no_image(self):
        """Test for a post by authenticated user without an image."""
        res = self._create_a_post()
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user.posts.count(), 1)
        
class UserProfileEditTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password123')
        self.edit_url = reverse('user-profile-edit')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.payload = {
            'bio': 'New bio'
        }
        self.posts_url = reverse('posts-list')
        
    def test_user_profile_edit_bio(self):
        """Test user profile edit API endpoint for updating the bio field."""
        response = self.client.patch(self.edit_url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.bio, 'New bio')
    def test_user_profile_with_posts_edit_bio(self):
        """Test user profile edit API endpoint for updating the bio field."""
        self.client.post(self.posts_url, {'text':'post1'})
        self.client.post(self.posts_url, {'text':'post2'})
        response = self.client.patch(self.edit_url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.bio, 'New bio')
        # Assert the user's posts
        posts = self.user.posts.order_by('id')
        self.assertEqual(posts.count(), 2)
        self.assertEqual(posts[0].text, 'post1')
        self.assertEqual(posts[1].text, 'post2')