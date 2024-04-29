from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from datetime import timedelta
from django.utils import timezone

# Create your models here.
class UserProfile(AbstractUser):
    email = models.EmailField(unique=True);
    bio = models.TextField(blank=True, null=True);
    vet_professional = models.BooleanField(null=True, default=False);
    profile_image = models.ImageField(null=True, blank=True, default="default.png");
    date_of_birth = models.DateField(null=True, blank=True)
    # created = models.DateTimeField(auto_now_add=True); 
    
    def __str__(self):
        return self.username;

class VeterinaryProfessional(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    reference_number = models.CharField(max_length=100)
    rcvs_email = models.EmailField()
    registration_date = models.DateField(null=True, blank=True)
    location = models.TextField(blank=True, null=True)
    field_of_work = models.TextField(blank=True, null=True)
    verified = models.BooleanField(default=False)  # Could be used to track verification status
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_code_expires = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.user.username} - {self.reference_number}"

    def generate_verification_code(self):
        self.verification_code = uuid.uuid4().hex[:6]  # Generate a random 6 character code
        self.verification_code_expires = timezone.now() + timedelta(hours=1)  # Set expiration time to 1 hour from now
        self.save()
    