from datetime import timezone
from django.forms import ValidationError
from django.db.models import Q
from rest_framework import generics, viewsets
from django.core.mail import send_mail
from django.conf import settings 
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, DestroyAPIView
from rest_framework.views import APIView
from .serializers import OfferSerializer, ReportSerializer, UserSerializer, PostSerializer, CommentSerializer, UserRegistrationSerializer, ItemSerializer, VeterinaryProfessionalSerializer
from Social.models import SaveItem, User, Contact, Post ,Comment, Like, Verify, Item, Offer
from Users.models import VeterinaryProfessional
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.utils import timezone
now = timezone.now()



@api_view(['GET'])  
def getRoutes(request):

    routes = [

        {'POST':'api/users/token'},
        {'POST': 'api/users/token/refresh'},
    ]

    return Response(routes)

@api_view(['GET'])
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def getUser(request, id):
    user = User.objects.get(id = id)
    # posts = user.posts.all()
    userSerializer = UserSerializer(user, many=False)
    #postSerializer = PostSerializer(posts, many=True)
    return Response(userSerializer.data)


class ReportPostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = Post.objects.get(id=post_id)
        serializer = ReportSerializer(data={
            'post': post.id,
            'reported_by': request.user.id,
            'reason': request.data.get('reason', 'No reason provided.')
        })
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Post reported successfully.'}, status=201)
        return Response(serializer.errors, status=400)


class GetPostView(APIView):

    def get(self, request, id):
        # Get the post by ID, return 404 if not found
        post = get_object_or_404(Post, pk=id)
        # Serialize the post data
        serializer = PostSerializer(post)
        # Return the serialized data
        return Response(serializer.data)
    
class GetItemView(APIView):
    def get(self, request, id):
        item = get_object_or_404(Item, pk=id)
        serializer = ItemSerializer(item)
        return Response(serializer.data)


@api_view(['GET'])
def get_following_posts(request, id):
    user = User.objects.get(id = id);
    # Get the users that request.user is following
    following_users = Contact.objects.filter(user_from=user).values_list('user_to', flat=True)

    # Get posts from these users
    posts = Post.objects.filter(author__in=following_users).order_by('-created_at')
    serializer = PostSerializer(posts, many=True)
    # return Response(request, 'posts/following_posts.html', {'posts': posts})
    return Response(serializer.data)

@api_view(['GET'])
def get_all_posts(request):
    # Get all posts in the system, ordered by creation date descending
    posts = Post.objects.all().order_by('-created_at')
    # Serialize the posts
    serializer = PostSerializer(posts, many=True)
    # Return the serialized data
    return Response(serializer.data)
    
class CommentCreateView(CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]  # Example permission class

    def perform_create(self, serializer):
        post_id = self.request.data.get('post')  

        # Retrieve the Post instance, or return a 404 if not found
        post = get_object_or_404(Post, pk=post_id)

        # Save the comment with the post and author set
        serializer.save(author=self.request.user, post=post)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        # Call the superclass method to create a new comment
        response = super().create(request, *args, **kwargs)
        return Response(response.data, status=response.status_code)
    
class CommentDeleteView(DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer  # Assuming you have a serializer for Comment
    permission_classes = [IsAuthenticated]

    def get_object(self):
        comment_id = self.kwargs.get('pk')
        comment = get_object_or_404(Comment, pk=comment_id)
        self.check_object_permissions(self.request, comment)  # Check permissions against the comment
        return comment

    
class UserRegistrationView(CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Check if the user was successfully created
        if response.status_code == 201:
            user_instance = response.data  # Assuming the user instance data is directly in the response data
            
            # Assuming 'email' is a field in the serialized data
            email = user_instance.get("email", "")  
            if email:
                # Define your email message and subject
                subject = 'Welcome to Our Platform!'
                message = 'Hi there! Thank you for registering with us. We are excited to have you on board.'
                from_email = 'your-email@example.com'  # The email configured in settings.py
                recipient_list = [email]
                
                # Send the email
                send_mail(subject, message, from_email, recipient_list)

                # Customizing the response message to include email confirmation
                response.data["message"] = "User Created Successfully. A welcome email has been sent to your email address."

            return response

class VerifyCodeView(APIView):
    """
    APIView to verify a code for a veterinary professional.
    """
    def post(self, request, *args, **kwargs):
        user = request.user
        code = request.data.get('verification_code')
        vet_professional = getattr(user, 'veterinaryprofessional', None)

        if vet_professional and vet_professional.verification_code == code:
            if vet_professional.verification_code_expires and vet_professional.verification_code_expires > timezone.now():
                vet_professional.verified = True
                vet_professional.save()
                return Response({'message': 'Verification successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Code expired'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)


class UserEditView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        try:
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        except Exception as e:
            print("Error during serialization or update:", e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        vet_info= serializer.validated_data.get('veterinaryprofessional', {})
        print('vet info availble:', serializer.validated_data)
        vet_professional_info = getattr(request.user, 'veterinaryprofessional', None)
        
        if vet_professional_info and request.session.get('reference_number_validated', False):
                vet_professional_info.generate_verification_code()
                subject = 'Catlog Verification Code'
                message = f'Your verification code is {vet_professional_info.verification_code} , and it expires in 1 hour.'
                from_email = 'your-email@example.com'
                recipient_list = [request.user.email]

                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                del request.session['reference_number_validated']
                # Custom response
                return Response({
                    'message': 'Verification code sent successfully. Check your email.',
                    'verification_code_sent': True
                }, status=status.HTTP_200_OK)

        return super().update(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

class ToggleLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id, format=None):
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        
        like_instance, created = Like.objects.get_or_create(post=post, author=user)
        
        if created:
            # A new like was created
            action = 'liked'
        else:
            # The like already existed, so we remove it
            like_instance.delete()
            action = 'unliked'
        
        return Response({"action": action, "post_id": post_id})


class ToggleSaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id, format=None):
        item = get_object_or_404(Item, pk=item_id)
        user = request.user
        
        save_instance, created = SaveItem.objects.get_or_create(item=item, user=user)
        
        if created:
            # A new save was created
            action = 'saved'
        else:
            # The save already existed, so we remove it
            save_instance.delete()
            action = 'unsaved'
        
        return Response({"action": action, "item_id": item_id})



class ToggleVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id, format=None):
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        
        verify_instance, created = Verify.objects.get_or_create(post=post, author=user)
        
        if created:
            # A new verify was created
            action = 'verified'
        else:
            # The verify already existed, so remove it
            verify_instance.delete()
            action = 'verify'
        
        return Response({"action": action, "post_id": post_id})



class PostUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # Provide a clear error message and optional error code
            return Response(
                {"detail": "Authentication credentials were not provided.", "code": "authentication_required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Include detailed error information from the serializer
            return Response(
                {"errors": serializer.errors, "code": "validation_error"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class PostDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id, format=None):
        try:
            post = Post.objects.get(pk=post_id, author=request.user)  # Ensure only the author can delete
        except Post.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        post.delete()
        return Response({"detail": "Post deleted."}, status=status.HTTP_204_NO_CONTENT)
    
class PostUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, post_id, format=None):
        try:
            post = Post.objects.get(pk=post_id, author=request.user)  # Ensure only the author can update
        except Post.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(post, data=request.data, partial=True)  
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ItemCreateView(generics.CreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]  

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user) 

class ItemUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, item_id, format=None):
        # Attempt to retrieve the item ensuring only the seller can update it
        try:
            item = Item.objects.get(pk=item_id, seller=request.user)
        except Item.DoesNotExist:
            return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

        # Deserialize data over the existing item instance
        serializer = ItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ItemDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id, format=None):
        try:
            item = Item.objects.get(pk=item_id, seller=request.user)  # Ensure only the author can delete
        except Item.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response({"detail": "Item deleted."}, status=status.HTTP_204_NO_CONTENT)
      

class FollowToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        # Get the target user by username
        target_user = get_object_or_404(User, id = id)
        # Prevent a user from following themselves
        if request.user == target_user:
            return Response({'detail': 'You cannot follow yourself.'}, status=400)

        # Check if the current user already follows the target user
        contact, created = Contact.objects.get_or_create(user_from=request.user, user_to=target_user)

        if created:
            # If the contact was newly created, it means the user has successfully followed the target user
            action = 'following'
        else:
            # If the contact already exists, delete it to unfollow the target user
            contact.delete()
            action = 'follow'

        return Response({'status': action, 'user_to': target_user.username}, status=200)
    

@api_view(['GET'])
def getItems(request):
    items = Item.objects.filter(status__in=[Item.Status.AVAILABLE, Item.Status.PENDING]).order_by('-updated_at')
    serializer = ItemSerializer(items, many=True)
    return Response(serializer.data)

class SearchView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')
        if query:
            words = query.split()
            q_objects = Q()
            for word in words:
                q_objects |= Q(title__icontains=word)
                q_objects |= Q(content__icontains=word)
                q_objects |= Q(comments__text__icontains=word)
            posts = Post.objects.filter(q_objects).distinct()
            serializer = PostSerializer(posts, many=True, context={'request': request})  
            serialized_data = serializer.data
            sorted_posts = sorted(serialized_data, key=lambda x: (-x['total_verifies'], -x.get('total_likes', 0)))
            print(sorted_posts)
            return Response(sorted_posts)
        return Response({"message": "No query provided"}, status=status.HTTP_400_BAD_REQUEST)

class SearchItemView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')
        if query:
            words = query.split()
            q_objects = Q()
            for word in words:
                q_objects |= Q(title__icontains=word)
                q_objects |= Q(description__icontains=word)
            items = Item.objects.filter(q_objects).distinct()
            serializer = ItemSerializer(items, many=True)
            return Response(serializer.data)
        return Response({"message": "No query provided"}, status=status.HTTP_400_BAD_REQUEST)

class CreateOfferView(generics.CreateAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Ensure the serializer has the request context to access the user
        serializer.save(buyer=self.request.user)