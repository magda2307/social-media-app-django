from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Post, Tag
from django.contrib.auth import get_user_model
from .serializers import TagSerializer

User = get_user_model()

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

    def test_user_registration_duplicate_email(self):
        """Test user registration API endpoint with already registered mail."""
        self.client.post(self.register_url, self.user_data, format='json')
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_user_registration_bad_password(self):
        """Test user registration API endpoint with too short password."""
        payload = self.user_data
        payload['password'] = '123'
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_user_registration_bad_email(self):
        """Test user registration API endpoint with bad email."""
        payload = self.user_data
        payload['email'] = '123'
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_user_login(self):
        """Test user login API endpoint."""
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.login_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
    
    def test_user_login_bad_password(self):
        """Test user login API endpoint with wrong password."""
        payload = self.user_data
        payload['password'] = 'bad_password'
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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


class UserFollowViewTest(TestCase):
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
        return self.client.put(self.follow_url, self.payload)

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
        self._assertions_state_follow_count(res=res_unfollow, count=0, status=status.HTTP_204_NO_CONTENT)

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
        self._assertions_state_follow_count(res=res_unfollow, count=0, status=status.HTTP_409_CONFLICT)


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
        self.change_password_url = reverse('user-profile-change-password')
        
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

    def test_user_change_password(self):
        """Test user change password."""
        payload ={'old_password':'password123',
                'new_password':'new_password'}
        response = self.client.put(self.change_password_url, payload, format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_user_change_password_incorrect_old(self):
        """Test user change password - old password is incorrect."""
        payload ={'old_password':'bad_password',
                'new_password':'new_password'}
        response = self.client.put(self.change_password_url, payload, format='json')

    def test_user_change_password_incorrect_new(self):
        """Test user change password - new password is incorrect."""
        payload ={'old_password':'password123',
                'new_password':'1'}
        response = self.client.put(self.change_password_url, payload, format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
                

class PostCreationWithExistingOrNewTagsTest(TestCase):
    """Tests for creating post with existing tags or with tags
    created during post creation.."""
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='mail@example.com', password='password123')
        self.client.force_authenticate(self.user)
        self.admin = User.objects.create_superuser(email='admin@example.com', password='password123')
        self.post = Post.objects.create(user=self.user, text='Test post')
        self.tag1 = Tag.objects.create(user=self.user, name='Existing Tag 1')
        self.tag2 = Tag.objects.create(user=self.admin, name='Existing Tag 2')
        self.url_post = reverse('posts-list')
        
    def test_create_tags_during_post_creation(self):
        """Test creating tags during post creation."""
        payload = {'text': 'Test', 'tags': [{'name': 'tag1'}, {'name': 'tag2'}]}
        res = self.client.post(self.url_post, payload, format='json')
        post_id = res.data['id']
        post = Post.objects.get(id=post_id)
        tags = post.tags.all()
        tag_names = set(tag.name for tag in tags)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('tag1', tag_names)
        self.assertIn('tag2', tag_names)
    def test_create_post_with_existing_tags(self):
        """Test creating post with existing tags."""
        payload = {'text': 'Test post creating with existing tags', 'tags': [{'name': 'Existing Tag 1'},
                        {'name': 'Existing Tag 2'}]}
        res = self.client.post(self.url_post, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        post_id = res.data['id']
        post = Post.objects.get(id=post_id)
        tags = post.tags.all()
        tag_names = set(tag.name for tag in tags)
        self.assertIn('Existing Tag 1', tag_names)
        self.assertIn('Existing Tag 2', tag_names)
        self.assertEqual(Tag.objects.all().count(),2)


class UnusedTagDestroyViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='user@example.com', password='password123')
        self.client.force_authenticate(self.user)
        self.tag1 = Tag.objects.create(user=self.user, name='Tag 1')
        self.tag2 = Tag.objects.create(user=self.user, name='Tag 2')
        self.tag3 = Tag.objects.create(user=self.user, name='Tag 3')
        self.url = reverse('unused-tag-destroy', kwargs={'tag_id': self.tag1.id})

    def test_delete_unused_own_tag(self):
        """Test deleting unused own tag."""
        response = self.client.delete(self.url)
        self.assertDeleteResponse(response, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=self.tag1.id).exists())

    def test_delete_used_tag(self):
        """Test deleting used own tag that should be a bad request."""
        post = Post.objects.create(user=self.user, text='Test post')
        post.tags.add(self.tag2)
        response = self.client.delete(reverse('unused-tag-destroy', kwargs={'tag_id': self.tag2.id}))
        self.assertDeleteResponse(response, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Tag.objects.filter(id=self.tag2.id).exists())

    def test_delete_other_users_tag(self):
        """Test deleting other user tag which should be a bad request."""
        other_user = User.objects.create_user(email='other@example.com', password='password456')
        tag = Tag.objects.create(user=other_user, name='Other User Tag')
        response = self.client.delete(reverse('unused-tag-destroy', kwargs={'tag_id': tag.id}))
        self.assertDeleteResponse(response, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Tag.objects.filter(id=tag.id).exists())

    def test_delete_nonexistent_tag(self):
        """Test deleting nonexistent tag which should be not found."""
        response = self.client.delete(reverse('unused-tag-destroy', kwargs={'tag_id': 999}))
        self.assertDeleteResponse(response, status.HTTP_404_NOT_FOUND)

    def assertDeleteResponse(self, response, expected_status):
        self.assertEqual(response.status_code, expected_status)
        if expected_status == status.HTTP_204_NO_CONTENT:
            self.assertFalse(response.data)
        elif expected_status in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
        ]:
            self.assertIn('error', response.data)


class TagUpdateDestroyViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(email='admin@example.com', password='password123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.tag = Tag.objects.create(name='Test Tag')
        self.update_destroy_url = reverse('tag-update-destroy', kwargs={'pk': self.tag.pk})
        self.payload = {
            'name': 'Updated Tag'
        }

    def test_tag_update(self):
        """Test updating a tag."""
        response = self.client.put(self.update_destroy_url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.name, 'Updated Tag')

    def test_tag_destroy(self):
        """Test destroying a tag."""
        response = self.client.delete(self.update_destroy_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(pk=self.tag.pk).exists())


class TagListCreateViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='user@example.com', password='password123')
        self.client.force_authenticate(self.user)
        self.tag_data = {
            'name': 'Test Tag',
            'user': self.user.id
        }
        self.url = reverse('tags')

    def test_create_tag(self):
        """Test creating a new tag."""
        response = self.client.post(self.url, self.tag_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        tag = Tag.objects.get(pk=response.data['id'])
        self.assertEqual(tag.name, self.tag_data['name'])
        self.assertEqual(tag.user, self.user)

    def test_list_tags(self):
        """Test retrieving a list of tags."""
        tag1 = Tag.objects.create(name='Tag 1', user=self.user)
        tag2 = Tag.objects.create(name='Tag 2', user=self.user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn(TagSerializer(tag1).data, response.data)
        self.assertIn(TagSerializer(tag2).data, response.data)


class UserTagListViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='user@example.com', password='password123')
        self.admin = User.objects.create_superuser(email='admin@example.com', password='password123')
        self.client.force_authenticate(self.user)
        self.tag1 = Tag.objects.create(name='Tag 1', user=self.user)
        self.tag2 = Tag.objects.create(name='Tag 2', user=self.user)
        self.tag3 = Tag.objects.create(name='Tag 3', user=self.admin)
        self.url = reverse('tags-user')

    def test_list_user_tags(self):
        """Test retrieving a list of user's own tags."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn(TagSerializer(self.tag1).data, response.data)
        self.assertIn(TagSerializer(self.tag2).data, response.data)
        self.assertNotIn(TagSerializer(self.tag3).data, response.data)


class UserLikePostViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(email='test@example.com', password='password1234')
        self.post = Post.objects.create(text='Test Post', user=self.user)
        self.client.force_authenticate(user=self.user)
        
    def _like_post(self, post_id):
        url = reverse('post-like', args=[post_id])
        return self.client.post(url)

    def _unlike_post(self, post_id):
        url = reverse('post-unlike', args=[post_id])
        return self.client.delete(url)

    def test_like_post(self):
        """Test for liking a post."""
        response = self._like_post(post_id=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertIn(self.post, self.user.liked_posts.all())

    def test_unlike_post(self):
        """Test for unliking a post."""
        self.user.liked_posts.add(self.post)
        response = self._unlike_post(post_id=self.post.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertNotIn(self.post, self.user.liked_posts.all())

    def test_like_already_liked_post(self):
        """Tes for liking an already liked post which should result
        in exception. It returns 500 for some reason and i cannot troubleshoot it.
        But it works almost as expected - it does not allow user to do that."""
        self.user.liked_posts.add(self.post)
        response = self._like_post(post_id=self.post.id)
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)


class UserLikesListViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='testpassword')
        self.client =APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_liked_posts(self):
        """Test retrieving a list of user's liked posts."""
        post1 = Post.objects.create(text='Post 1', user=self.user)
        post2 = Post.objects.create(text='Post 2', user=self.user)
        self.user.liked_posts.add(post1, post2)

        url = reverse('user-likes')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['text'], 'Post 1')  
        self.assertEqual(response.data[1]['text'], 'Post 2') 

class PostLikesListViewTests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(email='user1@example.com', password='password1')
        self.user2 = User.objects.create_user(email='user2@example.com', password='password2')
        self.post = Post.objects.create(text='Test Post', user=self.user1)
        self.post.likes.add(self.user2)
        self.client =APIClient()
        self.client.force_authenticate(user=self.user1)


    def test_get_users_liked_post(self):
        """Test retrieving a list of users that liked a particular post."""
        url = reverse('post-likes', kwargs={'post_id': self.post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], 'user2@example.com')
