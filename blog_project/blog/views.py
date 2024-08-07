from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import Post, Comment, Reaction
from .forms import PostForm, CommentForm, SignUpForm
from django.db.models import Q, Count, Sum, F
from django.core.paginator import Paginator
from django.http import JsonResponse
import json

def post_list(request):
    query = request.GET.get('q')
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__icontains=query)
        ).order_by('-created_at')
    else:
        posts = Post.objects.all().order_by('-created_at')
    
    paginator = Paginator(posts, 5)  # Show 5 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Fetch top 10 most interactive blogs
    trending_posts = Post.objects.annotate(
        comment_count=Count('comments'),
        reaction_count=Sum('comments__reaction_set__count')
    ).annotate(
        interaction_count=F('comment_count') + F('reaction_count')
    ).order_by('-interaction_count')[:10]

    context = {
        'page_obj': page_obj,
        'query': query,
        'trending_posts': trending_posts,
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.filter(parent__isnull=True)  # Removed is_approved=True
    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = json.loads(request.body)
            comment_id = data.get('comment_id')
            emoji = data.get('emoji')
            comment = get_object_or_404(Comment, id=comment_id)
            reaction, created = Reaction.objects.get_or_create(comment=comment, emoji=emoji)
            reaction.count += 1
            reaction.save()
            return JsonResponse({'status': 'success'})
        else:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user.username if request.user.is_authenticated else 'Anonymous'
                parent_id = request.POST.get('parent_id')
                if parent_id:
                    comment.parent = Comment.objects.get(id=parent_id)
                comment.save()
                return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments, 'form': form})

@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('post_list')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def profile(request):
    return render(request, 'registration/profile.html')
