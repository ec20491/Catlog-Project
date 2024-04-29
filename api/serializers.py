from typing import OrderedDict
from rest_framework import serializers
from Social.models import Report, User, Post, Contact,Comment,Like,Verify,Item, SaveItem
from Social.models import Offer
from Users.models import VeterinaryProfessional
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone 
from django.conf import settings
import pandas as pd 
from django.db.models import Q




class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = [
            'id', 'item', 'buyer', 'offer_amount', 'message', 
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'buyer', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Assuming you want to set the buyer as the current user and status to pending by default
        user = self.context['request'].user
        validated_data['buyer'] = user
        validated_data['status'] = 'pending'
        return super().create(validated_data)



def get_total_comment_count(post):
    # Get all top-level comments for the post
    top_level_comments = post.comments.filter(parent=None)
    total_count = top_level_comments.count()

    # Function to recursively count replies
    def count_replies(comments):
        nonlocal total_count
        for comment in comments:
            replies = comment.replies.all()  # Correctly using 'replies' here
            total_count += replies.count()
            count_replies(replies)

    # Start counting replies from the top-level comments
    count_replies(top_level_comments)
    return total_count




class ItemSerializer(serializers.ModelSerializer):
    seller = serializers.SerializerMethodField()
    save_count = serializers.SerializerMethodField()
    saves_list = serializers.SerializerMethodField()
    class Meta:
        model = Item
        fields = ['id','title', 'seller','description','media', 'price', 'status', 'condition','location', 'longitude','latitude', 'save_count', 'saves_list']
        read_only_fields = ('seller',)
    def get_seller(self,obj):
        user = obj.seller
        verified = user.is_verified() if hasattr(user, 'is_verified') else False
        return {
            'id': user.id,
            'username': user.username,
            'profile_image': user.profile_image.url if user.profile_image else None,
            'verified': verified
        }
    def get_save_count(self, obj):
        return SaveItem.objects.filter(item=obj).count()
    

    def get_saves_list(self, obj):
        saves = SaveItem.objects.filter(item=obj).select_related('user')
        user_saves = [
            {
                "id": save.user.id,
                "username": save.user.username,
                "profile_image": save.user.profile_image.url if save.user.profile_image else None,
                "verified": save.user.veterinaryprofessional.verified if hasattr(save.user, 'veterinaryprofessional') else False,
            }
            for save in saves
        ]
        return user_saves



class UserCommentSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    verified = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id','username', 'profile_image', 'verified']

    def get_verified(self,obj):
        verified = obj.veterinaryprofessional.verified if hasattr(obj, 'veterinaryprofessional') else False
        return verified


    def get_profile_image(self, obj):
        if obj.profile_image:
            request = self.context.get('request')
            profile_image_url = obj.profile_image.url
            return request.build_absolute_uri(profile_image_url) if request else profile_image_url
        return None

class CommentSerializer(serializers.ModelSerializer):
    author = UserCommentSerializer(read_only=True) 
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id','post','author','parent', 'text', 'created_at', 'replies']

    def get_replies(self, obj):
        # Recursively serialize replies
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

class VerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = Verify
        fields = ['post', 'user']

    def validate(self, data):
        user = self.context['request'].user
        if not user.vet_professional:
            raise serializers.ValidationError("Only vet professionals can verify posts.")
        
        # Check if the user has already verified this post
        post = data.get('post')
        verification_exists = Verify.objects.filter(post=post, user=user).exists()
        if verification_exists:
            raise serializers.ValidationError("This post has already been verified by the user.")

        return data

    def create(self, validated_data):
        # Additional logic to create the Verify instance
        verify_instance = Verify.objects.create(**validated_data)
        return verify_instance

class PostSerializer(serializers.ModelSerializer):
    total_likes = serializers.SerializerMethodField()
    user_likes_list = serializers.SerializerMethodField() 
    total_verifies = serializers.SerializerMethodField()
    user_verifies_list = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    author = serializers.CharField(source='author.username', read_only=True)
    author_profile_image = serializers.SerializerMethodField()
    author_verified = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ['id','author','author_id','author_verified','author_profile_image','title','content','media' ,'created_at', 'updated_at', 
                  'total_verifies','user_verifies_list','total_likes',
                  'user_likes_list','total_comments', 'comments'];
    
    
    def get_author_verified(self,obj):
        verified = obj.author.veterinaryprofessional.verified if hasattr(obj.author, 'veterinaryprofessional') else False
        return verified
        

    def get_total_likes(self, obj):
        return Like.objects.filter(post=obj).count()
    

    def get_user_likes_list(self, obj):
        likes = Like.objects.filter(post=obj).select_related('author')
        user_likes = [
            {
                "id": like.author.id,
                "username": like.author.username,
                "profile_image": like.author.profile_image.url if like.author.profile_image else None,
                "verified": like.author.veterinaryprofessional.verified if hasattr(like.author, 'veterinaryprofessional') else False,
            }
            for like in likes
        ]
        return user_likes
    

    def get_total_verifies(self,obj):
        return Verify.objects.filter(post=obj).count()
    
    def get_user_verifies_list(self,obj):
        verifies = Verify.objects.filter(post=obj).select_related('author')
        user_verifies = [
            {
                "id": verify.author.id,
                "username": verify.author.username,
                "profile_image": verify.author.profile_image.url if verify.author.profile_image else None,
                "verified": verify.author.veterinaryprofessional.verified if hasattr(verify.author, 'veterinaryprofessional') else False,
            }
            for verify in verifies
        ]
        return user_verifies

    def get_total_comments(self, obj):
        # Pass the Post instance to the count function
        return get_total_comment_count(obj)
    
    def get_comments(self, obj):
        top_level_comments = Comment.objects.filter(post=obj, parent=None)
        # Ensure to pass the request context to the CommentSerializer if needed
        context = {'request': self.context.get('request')} if self.context.get('request') else {}
        return CommentSerializer(top_level_comments, many=True, context=context).data
    
    def get_author_profile_image(self, obj):
        request = self.context.get('request')
        if obj.author.profile_image and hasattr(obj.author.profile_image, 'url'):
            profile_image_url = obj.author.profile_image.url
            return request.build_absolute_uri(profile_image_url) if request else profile_image_url
        return None

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'post', 'reported_by', 'created_at', 'reason', 'reviewed']

    
class FollowerSerializer(serializers.ModelSerializer):
    #follower = serializers.CharField(source='user_from.username')
    userId = serializers.ReadOnlyField(source='user_from.id')
    username = serializers.ReadOnlyField(source='user_from.username')
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = ['userId', 'username', 'profile_image']

    def get_profile_image(self, obj):
        if obj.user_from.profile_image and hasattr(obj.user_from.profile_image, 'url'):
            request = self.context.get('request')
            profile_image_url = obj.user_from.profile_image.url
            return request.build_absolute_uri(profile_image_url) if request else profile_image_url
        return None
    

class FollowingSerializer(serializers.ModelSerializer):
    userId = serializers.ReadOnlyField(source='user_to.id')
    username = serializers.ReadOnlyField(source='user_to.username')
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = ['userId', 'username', 'profile_image']

    def get_profile_image(self, obj):
        if obj.user_to.profile_image and hasattr(obj.user_to.profile_image, 'url'):
            request = self.context.get('request')
            profile_image_url = obj.user_to.profile_image.url
            return request.build_absolute_uri(profile_image_url) if request else profile_image_url
        return None

class VeterinaryProfessionalSerializer(serializers.ModelSerializer):
    print("AM I HERE")
    class Meta:
        model = VeterinaryProfessional
        fields = ['verified','reference_number','rcvs_email', 'registration_date','location','field_of_work']


    def validate_rcvs_email(self, value):
        if value and not value.endswith('@rcvs.org.uk'):
            raise serializers.ValidationError("Email must end with @rcvs.org.uk")
        return value

    def validate_reference_number(self, value):
        if value:
            if not value.isdigit() or len(value) != 7:
                raise serializers.ValidationError("Reference number must be 7 digits.")
            df = pd.read_csv(settings.REFERENCE_CSV_FILE_PATH, delimiter=';', skipinitialspace=True)
            matched_rows = df[df['Reference Number'].astype(str).str.strip() == str(value).strip()]
            if matched_rows.empty:
                raise serializers.ValidationError("Reference number not found.")
            self.context['request'].session['reference_number_validated'] = True
        return value

    def validate_registration_date(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("The registration date cannot be in the future.")
        return value
    
    def validate(self, data):
        return data
    
    def create(self, validated_data):
        instance = super().create(validated_data)
        if instance.reference_number:  # Assuming the reference number is valid and matched
            instance.generate_verification_code()  # Generate and set the verification code and expiry
            self.send_verification_email(instance)
        return instance

class SaveItemSerializer(serializers.ModelSerializer):
    item = serializers.SerializerMethodField()
    class Meta:
        model = SaveItem
        fields = ['user', 'item', 'saved_at']

    def get_item(self, obj):
        serializer = ItemSerializer(obj.item) 
        return serializer.data


class UserSerializer(serializers.ModelSerializer):
    vet_professional_info = VeterinaryProfessionalSerializer(source='veterinaryprofessional', required=False)
    num_posts = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()
    num_followers = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    num_following = serializers.SerializerMethodField() 
    followings = serializers.SerializerMethodField()
    num_saves = serializers.SerializerMethodField()
    saves_list = serializers.SerializerMethodField()
    num_items = serializers.SerializerMethodField()
    items_list =serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'bio', 'vet_professional', 'vet_professional_info','profile_image', 'date_of_birth', 'num_posts', 'posts', 'num_items','items_list','num_saves','saves_list','num_followers', 'followers', 'num_following', 'followings']
    print('HERERE')
    def create(self, validated_data):
        vet_professional_info_data = validated_data.pop('vet_professional_info', {})
        print("HERE", vet_professional_info_data)
        user = User.objects.create(**validated_data)

        # Determine vet_professional status based on provided info
        if vet_professional_info_data.get('rcvs_email') and vet_professional_info_data.get('reference_number'):
            user.vet_professional = True
            VeterinaryProfessional.objects.create(user=user, **vet_professional_info_data)
        else:
            user.vet_professional = False
        user.save()

        return user
    
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.bio = validated_data.get('bio', instance.bio)
        # instance.vet_professional = validated_data.get('vet_professional', instance.vet_professional)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
    
        # Handle profile_image separately
        profile_image = validated_data.pop('profile_image', None)
        if profile_image is not None:
            instance.profile_image.save(profile_image.name, profile_image)
        
        # Update or create VeterinaryProfessional information if provided
        
        
        vet_prof_data = validated_data.pop('veterinaryprofessional', None)
        vet_professional = validated_data.pop('vet_professional', None)
        print('calidated data', validated_data)
        print('vet_data', vet_prof_data)
        print("test:" , vet_professional)

        if vet_professional is False:
            instance.vet_professional = False
            VeterinaryProfessional.objects.filter(user=instance).delete()

        elif vet_professional is True:
           
            if vet_prof_data:  
                print('Yes, data exists')
                VeterinaryProfessional.objects.update_or_create(
                    user=instance, 
                    defaults=vet_prof_data
                )
                instance.vet_professional = True
            else:
                print("No vet data found")
        instance.save()
        return instance

    def get_num_posts(self, obj):
        return obj.posts.count()
    
    def get_posts(self, obj):
        posts = obj.posts.all()
        serializer = PostSerializer(posts, many=True)
        return serializer.data
    
    def get_num_saves(self,obj):
        return obj.saved_items.count()
    
    def get_saves_list(self,obj):
        saves = obj.saved_items.all()
        serializer = SaveItemSerializer(saves, many=True)
        return serializer.data
    
    def get_num_items(self,obj):
        return obj.items_for_sale.count()
    
    def get_items_list(self,obj):
        items = obj.items_for_sale.all()
        serializer = ItemSerializer(items, many=True)
        return serializer.data
    
    def get_num_followers(self, obj):
        # Assuming you have a reverse relation set up from User to Follow for followers
        return obj.rel_to_set.count()
    
    def get_followers(self, obj):
        followers = obj.rel_to_set.all()
        serializer = FollowerSerializer(followers, many=True)
        return serializer.data
    
    def get_num_following(self, obj):
        # Assuming you have a reverse relation set up from User to Follow for followings
        return obj.rel_from_set.count()
    
    def get_followings(self, obj):
        followings = obj.rel_from_set.all()
        serializer = FollowingSerializer(followings, many=True)
        return serializer.data
    
    

class UserRegistrationSerializer(serializers.ModelSerializer):
        password_confirmation = serializers.CharField(style={'input_type': 'password'}, write_only=True)

        class Meta:
            model = User
            fields = ['username', 'email', 'password', 'password_confirmation']
            extra_kwargs = {
                'password': {'write_only': True},
                'password_confirmation': {'write_only': True},
            }
        def validate_password(self, value):
            try:
                validate_password(value)
            except DjangoValidationError as e:
                # This converts Django's ValidationError into DRF's ValidationError
                raise serializers.ValidationError(list(e.messages))
            return value
        
        

        def validate(self, data):
            if data['password'] != data['password_confirmation']:
                raise serializers.ValidationError("Passwords must match.")
            return data

        def create(self, validated_data):
            # Remove password_confirmation from the validated data
            validated_data.pop('password_confirmation', None)
            
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
            )
            user.set_password(validated_data['password'])
            user.save()

            return user
        
