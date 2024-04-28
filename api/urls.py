from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    path('users/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', views.getRoutes),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('users/', views.getUsers, name='get-users'),
    path('users/<int:id>/', views.getUser, name='get-user'),
    path('fyp/<int:id>',views.get_following_posts, name='get-fyp'),
    path('get-post/<int:id>/', views.GetPostView.as_view(), name='get-post'),
    path('get-item/<int:id>/', views.GetItemView.as_view(), name='get-item'),
    path('explore/',views.get_all_posts, name='get-all-posts'),
    path('comments/create/', views.CommentCreateView.as_view(), name='create-comment'),
    path('comments/delete/<int:pk>/', views.CommentDeleteView.as_view(), name='comment-delete'),
    path('edit-profile/', views.UserEditView.as_view(), name='edit-profile'),
    path('toggle-like/<int:post_id>/', views.ToggleLikeView.as_view(), name='toggle-like'),
    path('toggle-save/<int:item_id>/', views.ToggleSaveView.as_view(), name='toggle-save'),
    path('toggle-verify/<int:post_id>/', views.ToggleVerifyView.as_view(), name='toggle-verify'),
    path('upload/', views.PostUploadView.as_view(), name='post-upload'),
    path('follow/<int:id>/', views.FollowToggleView.as_view(), name='follow_toggle'),
    path('create-listing/', views.ItemCreateView.as_view(), name='item-upload'),
    path('items/', views.getItems, name='item-list'),
    path('delete-post/<int:post_id>/', views.PostDeleteView.as_view(), name='post-delete'),
    path('update-post/<int:post_id>/', views.PostUpdateView.as_view(), name='post-update'),
    path('delete-item/<int:item_id>/', views.ItemDeleteView.as_view(), name='item-delete'),
    path('update-item/<int:item_id>/', views.ItemUpdateView.as_view(), name='item-update'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('search-item/', views.SearchItemView.as_view(), name='search-item'),
    path('create-offer/', views.CreateOfferView.as_view(), name='create-offer'),
    path('verify-email/', views.VerifyCodeView.as_view(), name='verify-code'),
    path('report-post/<int:post_id>/', views.ReportPostView.as_view(), name='report-post'),

    ]
