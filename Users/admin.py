from django.contrib import admin
from .models import UserProfile, VeterinaryProfessional

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(VeterinaryProfessional)