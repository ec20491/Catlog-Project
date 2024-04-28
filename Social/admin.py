from django.contrib import admin
from django.core.exceptions import PermissionDenied

# Register your models here
from .models import Post, Comment, Like, Verify, Contact,Item, SaveItem, Offer, ItemImage, Report

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Item)
admin.site.register(SaveItem)
admin.site.register(Offer)
admin.site.register(Report)
admin.site.register(ItemImage)

@admin.register(Verify)
class VerifyAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not request.user.vet_professional:
            raise PermissionDenied("Only vet professionals can verify posts.")

        super().save_model(request, obj, form, change)
admin.site.register(Contact)