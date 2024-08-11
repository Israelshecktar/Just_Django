from django.db import models
import json
from django.contrib.auth.models import AbstractUser, Group, Permission

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=100, default='Anonymous')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, related_name='posts', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.CharField(max_length=100, default='Anonymous')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    reactions = models.TextField(default='{}')  # Store reactions as a JSON string

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'

    def get_reactions(self):
        return json.loads(self.reactions)

    def add_reaction(self, emoji):
        reactions = self.get_reactions()
        if emoji in reactions:
            reactions[emoji] += 1
        else:
            reactions[emoji] = 1
        self.reactions = json.dumps(reactions)
        self.save()

    def get_replies(self):
        return self.replies.all()  # Removed is_approved=True

class Reaction(models.Model):
    comment = models.ForeignKey(Comment, related_name='reaction_set', on_delete=models.CASCADE)
    emoji = models.CharField(max_length=10)
    count = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.emoji} - {self.count}'

class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True, default='default_profile.png')

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Add related_name to avoid clash
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',  # Add related_name to avoid clash
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
class ThemeConfiguration(models.Model):
    THEME_CHOICES = [
        ('dark', 'Dark'),
        ('light', 'Light'),
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    theme = models.CharField(max_length=5, choices=THEME_CHOICES, default='light')