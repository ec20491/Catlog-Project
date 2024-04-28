from django.db import models
from django.contrib.auth import get_user_model
from Users.models import VeterinaryProfessional

User = get_user_model()


class Contact(models.Model):
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rel_from_set')
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name ='rel_to_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_from', 'user_to')  # Ensures a user can only follow a user once

    def __str__(self):
        # Return a string representation of the Contact object
        return f'{self.user_from.username} -> {self.user_to.username}'
User.add_to_class('following', models.ManyToManyField('self',through=Contact, related_name='followers', symmetrical=False))




# Create your models here.
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.TextField(default="This is the title")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    media = models.ImageField(null=True, blank=True, default="default.png");

    def __str__(self):
        # Return a string representation of the Contact object
        return f'{self.author.username} : {self.content}'

    
class Report(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    reason = models.TextField()

    def __str__(self):
        return f"Report {self.id} on Post {self.post.id}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id}: Comment by {self.author.username} on {self.post.id} with parent {self.parent}'

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'author')  # Ensures a user can only like a post once

    def __str__(self):
        return f'Liked by {self.author.username} on {self.post.content} by {self.post.author.username}'

class Verify(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='verifies')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('post', 'author')  # Ensures a user can only verify a post once

    def __str__(self):
        return f'{self.author.username} verify post {self.post.id} by {self.post.author.username}'

class Item(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'AV', 'Available'
        PENDING = 'PE', 'Pending'
        SOLD = 'SO', 'Sold'
    class Condition(models.TextChoices):
        NEW = 'NEW' , 'New'
        USED_NEW = 'ULN', 'Used - Like New'
        USED_GOOD = 'UG', 'Used - Good'
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    media = models.ImageField(null=True, blank=True, default="default.png")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items_for_sale')
    location = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=30, decimal_places=20, blank=True, null=True)
    longitude = models.DecimalField(max_digits=30, decimal_places=20, blank=True, null=True)
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )
    condition = models.CharField(
        max_length=3,
        choices=Condition.choices,
        default=Condition.USED_NEW,
    )

    def __str__(self):
        return self.title
    
class Offer(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='offers')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers_made')
    offer_amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending',
    )

    def __str__(self):
        return f"{self.buyer.username}'s offer for {self.item.title}"
    
    
    
class ItemImage(models.Model):
    item = models.ForeignKey(Item, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True, default="default.png")
    
    def __str__(self):
        return f"Image for {self.item.title}"
    
class SaveItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'item') 

    def __str__(self):
        return f"{self.user.username} saved {self.item.title}"

