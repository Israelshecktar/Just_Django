from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Post, Comment, CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('profile_picture',)}),
    )

class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at')  # Removed 'is_approved'
    list_filter = ('created_at',)  # Removed 'is_approved'
    search_fields = ('author', 'content')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approve selected comments"

admin.site.register(Post)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
