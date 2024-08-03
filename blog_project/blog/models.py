from django.db import models
import json

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=100, default='Anonymous')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.CharField(max_length=100, default='Anonymous')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
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
