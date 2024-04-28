from django.test import SimpleTestCase
from django.urls import reverse, resolve
from api import views


class TestUrls(SimpleTestCase):
    def test_register_url_resolves(self):
        url = reverse('register')
        self.assertEquals(resolve(url).func.view_class, views.UserRegistrationView)

    def test_get_users_url_resolves(self):
        url = reverse('get-users')
        self.assertEquals(resolve(url).func, views.getUsers)
    
    def test_get_user_url_resolves(self):
        url = reverse('get-user', args=[1])
        self.assertEquals(resolve(url).func, views.getUser)

    def test_get_following_posts_url_resolves(self):
        url = reverse('get-fyp', args=[1])
        self.assertEquals(resolve(url).func, views.get_following_posts)

    def test_get_post_url_resolves(self):
        url = reverse('get-post', args=[1])
        self.assertEquals(resolve(url).func.view_class, views.GetPostView)
    
    def test_explore_resolves(self):
        url = reverse('get-all-posts')
        self.assertEquals(resolve(url).func, views.get_all_posts)

    def test_create_comment_url(self):
        url = reverse('create-comment')
        self.assertEqual(resolve(url).func.view_class, views.CommentCreateView)

    def test_comment_delete_url(self):
        url = reverse('comment-delete', args=[1])  # Assuming an example comment ID
        self.assertEqual(resolve(url).func.view_class, views.CommentDeleteView)

    def test_edit_profile_url(self):
        url = reverse('edit-profile')
        self.assertEqual(resolve(url).func.view_class, views.UserEditView)

    def test_toggle_like_url(self):
        url = reverse('toggle-like', args=[1])  # Assuming an example post ID
        self.assertEqual(resolve(url).func.view_class, views.ToggleLikeView)

    def test_toggle_save_url(self):
        url = reverse('toggle-save', args=[1])  # Assuming an example item ID
        self.assertEqual(resolve(url).func.view_class, views.ToggleSaveView)

    def test_toggle_verify_url(self):
        url = reverse('toggle-verify', args=[1])  # Assuming an example post ID
        self.assertEqual(resolve(url).func.view_class, views.ToggleVerifyView)

    def test_post_upload_url(self):
        url = reverse('post-upload')
        self.assertEqual(resolve(url).func.view_class, views.PostUploadView)

    def test_follow_toggle_url(self):
        url = reverse('follow_toggle', args=[1])  # Assuming an example user ID
        self.assertEqual(resolve(url).func.view_class, views.FollowToggleView)

    def test_item_upload_url(self):
        url = reverse('item-upload')
        self.assertEqual(resolve(url).func.view_class, views.ItemCreateView)

    def test_item_list_url(self):
        url = reverse('item-list')
        self.assertEqual(resolve(url).func, views.getItems)

    def test_post_delete_url(self):
        url = reverse('post-delete', args=[1])  
        self.assertEqual(resolve(url).func.view_class, views.PostDeleteView)

    def test_post_update_url(self):
        url = reverse('post-update', args=[1])  
        self.assertEqual(resolve(url).func.view_class, views.PostUpdateView)

    def test_item_delete_url(self):
        url = reverse('item-delete', args=[1])  
        self.assertEqual(resolve(url).func.view_class, views.ItemDeleteView)

    def test_item_update_url(self):
        url = reverse('item-update', args=[1])  
        self.assertEqual(resolve(url).func.view_class, views.ItemUpdateView)

    def test_search_url(self):
        url = reverse('search')
        self.assertEqual(resolve(url).func.view_class, views.SearchView)

    def test_search_item_url(self):
        url = reverse('search-item')
        self.assertEqual(resolve(url).func.view_class, views.SearchItemView)

    def test_create_offer_url(self):
        url = reverse('create-offer')
        self.assertEqual(resolve(url).func.view_class, views.CreateOfferView)

    def test_verify_email_url(self):
        url = reverse('verify-code')
        self.assertEqual(resolve(url).func.view_class, views.VerifyCodeView)