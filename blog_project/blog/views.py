from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .models import Post, Comment, Reaction, Category, ThemeConfiguration
from .forms import PostForm, CommentForm, CustomUserCreationForm, CustomUserChangeForm
from django.db.models import Q, Count, Sum, F
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST
from django.http import JsonResponse


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

    # Fetch top 5 most interactive blogs
    trending_posts = Post.objects.annotate(
        comment_count=Count('comments'),
        reaction_count=Sum('comments__reaction_set__count')
    ).annotate(
        interaction_count=F('comment_count') + F('reaction_count')
    ).order_by('-interaction_count')[:5]

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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('post_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def profile(request):
    return render(request, 'registration/profile.html')

@login_required
def profile_update(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'registration/profile_update.html', {'form': form})

def community(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'blog/community.html', context)

def user_profile(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    return render(request, 'registration/user_profile.html', {'profile_user': user})

@require_POST
def set_theme(request):
    if request.user.is_authenticated:
        data = json.loads(request.body)
        theme = data.get('theme')
        ThemeConfiguration.objects.update_or_create(user=request.user, defaults={'theme': theme})
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
