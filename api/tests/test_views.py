from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.urls import reverse
from Users.models import UserProfile
from Social.models import VeterinaryProfessional, Like, Post, Verify, Item, SaveItem, Contact, Comment 
from django.core.mail import send_mail
from unittest.mock import patch
from api.serializers import UserSerializer
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image
from api.serializers import PostSerializer , ItemSerializer


class CommentDeleteViewTestCase(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.post = Post.objects.create(content='Test content', media='test.png', author=self.user)
        self.comment = Comment.objects.create(text='Test comment',post=self.post, author=self.user)

    def test_delete_comment_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('comment-delete', kwargs={'pk': self.comment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(pk=self.comment.id).exists())

    def test_delete_comment_unauthenticated(self):
        url = reverse('comment-delete', kwargs={'pk': self.comment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Comment.objects.filter(pk=self.comment.id).exists())

class CommentCreateViewTestCase(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create(username="testuser")
        self.post = Post.objects.create(content='Test content', media='test.png', author=self.user)
        self.comment = Comment.objects.create(text='Test comment',post=self.post, author=self.user)


    def test_create_comment_authenticated(self):
        url = reverse('create-comment')
        data = {
            'post': self.post.id,
            'text': 'This is a test comment.'
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_comment_unauthenticated(self):
        url = reverse('create-comment')
        data = {
            'post': self.post.id,
            'text': 'This is a test comment.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_comment_invalid_post_id(self):
        url = reverse('create-comment')
        data = {
            'post': 9999,  # Invalid post ID
            'text': 'This is a test comment.'
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SearchItemViewTestCase(APITestCase):
    def setUp(self):
        # Create test data
        self.user1 = UserProfile.objects.create_user(username='testuser', password='testpassword', email='test@gmail.com')
        self.user2 = UserProfile.objects.create_user(username='testuser2', password='testpassword2', email='test2@gmail.com')
        self.item1 = Item.objects.create(
            title='Test Item 1',
            seller=self.user1,
            description='Test content 1',
            price=10.00,
            status='AV',
            condition='NEW',
            location='Test Location'
        )
        self.item2 = Item.objects.create(
            title='Test Item 2',
            seller=self.user2,
            description='Test content 2',
            price=10.00,
            status='AV',
            condition='NEW',
            location='Test Location'
        )
        self.client.force_authenticate(user=self.user1)
        self.client.force_authenticate(user=self.user2)

    def test_search_with_query(self):
        query = 'Test content'
        # Make a GET request to the search endpoint with the query parameter
        url = f"{reverse('search-item')}?query={query}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = ItemSerializer([self.item1, self.item2], many=True).data
        self.assertEqual(response.data, expected_data)

    def test_search_with_empty_query(self):
        url = reverse('search-item')
        response = self.client.get(url)
        # Check if the response status code is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_with_nonexistent_query(self):
        query = 'Nonexistent query'
        url = f"{reverse('search-item')}?query={query}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class SearchViewTestCase(APITestCase):
    def setUp(self):
        # Create test data
        self.user1 = UserProfile.objects.create_user(username='testuser', password='testpassword', email='test@gmail.com')
        self.user2 = UserProfile.objects.create_user(username='testuser2', password='testpassword2', email='test2@gmail.com')
        self.post1 = Post.objects.create(content='Test content 1', media='test.png', author=self.user1)
        self.post2 = Post.objects.create(content='Test content 1', media='test.png', author=self.user2)
        self.client.force_authenticate(user=self.user1)
        self.client.force_authenticate(user=self.user2)

    def test_search_with_query(self):
        query = 'content Test '
        url = f"{reverse('search')}?query={query}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = PostSerializer([self.post1, self.post2], many=True).data
        self.assertEqual(response.data, expected_data)

    def test_search_with_empty_query(self):
        url = reverse('search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_with_nonexistent_query(self):
        query = 'Nonexistent query'
        url = f"{reverse('search')}?query={query}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)



class ItemDeleteViewTestCase(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(username='testuser', email='test@example.com', password='password')
        # Create an item
        self.item = Item.objects.create(
            title='Test Item',
            seller=self.user,
            description='Description of the test item',
            price=10.00,
            status='Active',
            condition='New',
            location='Test Location'
        )
        self.client.force_authenticate(user=self.user)

    def test_delete_item(self):
        url = reverse('item-delete', kwargs={'item_id': self.item.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Item.objects.filter(pk=self.item.id).exists())

    def test_delete_item_unauthorized(self):
        other_user = UserProfile.objects.create_user(username='otheruser', email='other@example.com', password='password')
        self.client.force_authenticate(user=other_user)
        url = reverse('item-delete', kwargs={'item_id': self.item.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_item_delete(self):
        url = reverse('item-delete', kwargs={'item_id': 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)




class ItemUpdateViewTestCase(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(username='testuser', email='test@example.com', password='password')
        
        # Create an item
        self.item = Item.objects.create(
            title='Test Item',
            seller=self.user,
            description='Description of the test item',
            price=10.00,
            status='Active',
            condition='New',
            location='Test Location'
        )

    def test_update_item_authenticated(self):
        self.client.force_authenticate(user=self.user)
        updated_data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'price': 20.00
        }

        url = reverse('item-update', kwargs={'item_id': self.item.id})
        response = self.client.put(url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_item = Item.objects.get(id=self.item.id)

        self.assertEqual(updated_item.title, updated_data['title'])
        self.assertEqual(updated_item.description, updated_data['description'])
        self.assertEqual(updated_item.price, updated_data['price'])

    def test_update_item_unauthenticated(self):
        updated_data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'price': 20.00
        }

        url = reverse('item-update', kwargs={'item_id': self.item.id})
        response = self.client.put(url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        unchanged_item = Item.objects.get(id=self.item.id)
        self.assertEqual(unchanged_item.title, self.item.title)
        self.assertEqual(unchanged_item.description, self.item.description)
        self.assertEqual(unchanged_item.price, self.item.price)


class ItemCreateViewTestCase(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(username='testuser', email='test@example.com', password='password')
        image = Image.new('RGB', (100, 100))
        image_content = BytesIO()
        image.save(image_content, format='PNG')
        image_content.seek(0)
        mock_image = SimpleUploadedFile("image.png", image_content.read(), content_type="image/png")

        self.data = {
            'title': 'Test Item',
            'description': 'Test description',
            'media': mock_image,
            'price': 10.0,
            'status': 'AV',
            'condition': 'NEW',
            'location': 'Test Location'
        }

    def test_create_item_authenticated(self):
        url = reverse('item-upload')
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, self.data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Item.objects.filter(title='Test Item', seller=self.user).exists())

    def test_create_item_unauthenticated(self):
        url = reverse('item-upload')
        response = self.client.post(url, self.data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class PostUploadViewTestCase(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(username='testuser', email='test@example.com', password='password')
        
    def test_upload_post_authenticated(self):
        url = reverse('post-upload')
        image = Image.new('RGB', (100, 100))
        image_content1 = BytesIO()
        image.save(image_content1, format='PNG')
        image_content1.seek(0)
        mock_image = SimpleUploadedFile("image.png", image_content1.read(), content_type="image/png")
        data = {
            'content': 'Test content',
            'media': mock_image
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Post.objects.filter(content='Test content', author=self.user).exists())

    def test_upload_post_unauthenticated(self):
        client = APIClient()
        
        url = reverse('post-upload')
        data = {
            'content': 'Test content',
            'media' : 'image.png'
        }
        response = client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class PostDeleteViewTestCase(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.post = Post.objects.create(content='Test content', media='test.png', author=self.user)
        self.client.force_authenticate(user=self.user)

    def test_delete_post(self):
        url = reverse('post-delete', kwargs={'post_id': self.post.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(pk=self.post.id).exists())

    def test_delete_post_unauthorized(self):
        other_user = UserProfile.objects.create_user(username='otheruser', email='other@example.com', password='password')
        self.client.force_authenticate(user=other_user)
        url = reverse('post-delete', kwargs={'post_id': self.post.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_post_delete(self):
        url = reverse('post-delete', kwargs={'post_id': 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PostUpdateViewTestCase(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.post = Post.objects.create(content='Test content', media='test.png', author=self.user)
        self.client.force_authenticate(user=self.user)
        
    def test_update_post(self):
        url = reverse('post-update', kwargs={'post_id': self.post.id})
        updated_data = {'content': 'Updated content'}
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_post = Post.objects.get(pk=self.post.id)
        self.assertEqual(updated_post.content, 'Updated content')

    def test_update_post_unauthorized(self):
        other_user = UserProfile.objects.create_user(username='otheruser', email='other@example.com', password='password')
        self.client.force_authenticate(user=other_user)
        url = reverse('post-update', kwargs={'post_id': self.post.id})
        updated_data = { 'content': 'Updated content'}
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_post_update(self):
        url = reverse('post-update', kwargs={'post_id': 9999})
        updated_data = {'content': 'Updated content'}
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class FollowToggleViewTestCase(APITestCase):
    def setUp(self):
        self.user1 = UserProfile.objects.create_user(username='user1', email='user1@example.com', password='password1')
        self.user2 = UserProfile.objects.create_user(username='user2', email='user2@example.com', password='password2')
        self.client.force_authenticate(user=self.user1)
        
    def test_follow_user(self):
        url = reverse('follow_toggle', kwargs={'id': self.user2.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'following')
        self.assertTrue(Contact.objects.filter(user_from=self.user1, user_to=self.user2).exists())

    def test_unfollow_user(self):
        Contact.objects.create(user_from=self.user1, user_to=self.user2)
        url = reverse('follow_toggle', kwargs={'id': self.user2.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'follow')
        self.assertFalse(Contact.objects.filter(user_from=self.user1, user_to=self.user2).exists())

    def test_follow_self(self):
        url = reverse('follow_toggle', kwargs={'id': self.user1.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ToggleSaveViewTestCase(APITestCase):
    def setUp(self):
        # Create a user
        self.user = UserProfile.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        # Create an item
        self.item = Item.objects.create(title='Test Item', description='Test description', price=10, seller=self.user)

    def test_save_item(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.user)
        # Generate the URL for the 'toggle-save' named URL pattern with the item ID
        url = reverse('toggle-save', kwargs={'item_id': self.item.id})
        # Make a POST request to save the item using the generated URL
        response = self.client.post(url)
        # Check if the response status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the action is 'saved'
        self.assertEqual(response.data['action'], 'saved')
        # Check if a save instance was created
        self.assertTrue(SaveItem.objects.filter(item=self.item, user=self.user).exists())

    def test_unsave_item(self):
        # Create a save instance for the item
        SaveItem.objects.create(item=self.item, user=self.user)
        # Authenticate the user
        self.client.force_authenticate(user=self.user)
        # Generate the URL for the 'toggle-save' named URL pattern with the item ID
        url = reverse('toggle-save', kwargs={'item_id': self.item.id})
        # Make a POST request to unsave the item using the generated URL
        response = self.client.post(url)
        # Check if the response status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the action is 'unsaved'
        self.assertEqual(response.data['action'], 'unsaved')
        # Check if the save instance was deleted
        self.assertFalse(SaveItem.objects.filter(item=self.item, user=self.user).exists())

    def test_invalid_item_id(self):
        # Authenticate the user
        self.client.force_authenticate(user=self.user)
        # Generate the URL for the 'toggle-save' named URL pattern with an invalid item ID
        url = reverse('toggle-save', kwargs={'item_id': 9999})  # Using an invalid item ID
        # Make a POST request with the generated URL
        response = self.client.post(url)
        # Check if the response status code is 404 (Not Found)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ToggleVerifyViewTestCase(APITestCase):
    def setUp(self):
        # Create a user
        self.user = UserProfile.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.post = Post.objects.create(content='Test content', media='test.png', author=self.user)
        self.client.force_authenticate(user=self.user)

    def test_verify_post(self):
        url = reverse('toggle-verify', kwargs={'post_id': self.post.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'verified')
        self.assertTrue(Verify.objects.filter(post=self.post, author=self.user).exists())

    def test_unverify_post(self):
        Verify.objects.create(post=self.post, author=self.user)
        url = reverse('toggle-verify', kwargs={'post_id': self.post.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'verify')
        self.assertFalse(Verify.objects.filter(post=self.post, author=self.user).exists())

    def test_invalid_post_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('toggle-verify', kwargs={'post_id': 9999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ToggleLikeViewTestCase(APITestCase):
    def setUp(self):
        self.user = UserProfile.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.post = Post.objects.create(content='Test content', media='test.png', author=self.user)
        self.client.force_authenticate(user=self.user)

    def test_like_post(self):        
        url = reverse('toggle-like', kwargs={'post_id': self.post.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'liked')
        self.assertTrue(Like.objects.filter(post=self.post, author=self.user).exists())

    def test_unlike_post(self):
        Like.objects.create(post=self.post, author=self.user)
        url = reverse('toggle-like', kwargs={'post_id': self.post.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'unliked')
        self.assertFalse(Like.objects.filter(post=self.post, author=self.user).exists())

    def test_invalid_post_id(self):
        url = reverse('toggle-like', kwargs={'post_id': 9999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



class JWTTokenTests(TestCase):
    def setUp(self):
        # Setup run before every test method.
        self.client = APIClient()
        self.user = UserProfile.objects.create_user(username='testuser', password='testpass123', email='testuser@email.com')
        self.token_obtain_url = reverse('token_obtain_pair')
        self.token_refresh_url = reverse('token_refresh')
       

    def test_token_obtain(self):
        response = self.client.post(self.token_obtain_url, {'username': 'testuser', 'password': 'testpass123'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)

    def test_token_refresh(self):
        response = self.client.post(self.token_obtain_url, {'username': 'testuser', 'password': 'testpass123'}, format='json')
        refresh_token = response.data['refresh']
        
        response = self.client.post(self.token_refresh_url, {'refresh': refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)

    def test_token_refresh_with_invalid_token(self):

        response = self.client.post(self.token_refresh_url, {'refresh': 'invalidtoken'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class UpdateViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserProfile.objects.create_user(username='user', email='user@example.com', password='password')
        self.vet_professional = VeterinaryProfessional.objects.create(user=self.user, reference_number='1234567')
        self.url = reverse('edit-profile')
        self.data = {  
            "username": "testtest",
            "email": "test@outlook.com",
            "profile_image": "/images/test.png", 
      }
        self.client.force_authenticate(user=self.user)

    @patch('api.views.send_mail')
    def test_user_update_with_verification(self, mock_send_mail):
        session = self.client.session
        session['reference_number_validated'] = True
        session.save()

        # Test data with a valid reference number
        data = {
            'username': 'testuser',
            'email': 'newemail@example.com',
            'veterinaryprofessional': {'reference_number': '1234567', 'rcvs_email':'m@rcvs.org.uk'}
        }

        response = self.client.patch(self.url, data, format='json')

        self.assertTrue(mock_send_mail.called, "Email not sent")
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.user.delete()
        self.vet_professional.delete() 
