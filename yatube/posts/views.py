from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

NUMBER_OF_POSTS: int = 10


def index(request):
    template = 'posts/index.html'
    posts_list = Post.objects.all()
    paginator = Paginator(posts_list, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    paginator = Paginator(posts_list, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    user = request.user
    posts_count = profile_user.posts.count()
    posts_list_username = profile_user.posts.all()
    paginator = Paginator(posts_list_username, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if user.is_authenticated:
        if profile_user != user:
            if profile_user.following.exists():
                following = True
            else:
                following = False
        else:
            following = None
    else:
        following = False
    context = {
        'user': user,
        'following': following,
        'profile_user': profile_user,
        'page_obj': page_obj,
        'posts_count': posts_count,
    }
    return render(request, 'posts/profile.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id)


def post_detail(request, post_id):
    post_user = get_object_or_404(Post, id=post_id)
    posts_count = post_user.author.posts.count()
    comments = post_user.comments.filter(post_id=post_id)
    form_comments = CommentForm(request.POST or None)
    context = {
        'post_user': post_user,
        'posts_count': posts_count,
        'comments': comments,
        'form_comments': form_comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post.id)

    is_edit = post.text
    context = {
        'is_edit': is_edit,
        'form': form,
        'post': post,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def follow_index(request):
    author_ids = Follow.objects.filter(user=request.user).values_list(
        'author_id',
        flat=True
    )
    posts_list = Post.objects.filter(author_id__in=author_ids)
    paginator = Paginator(posts_list, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
        return redirect('posts:profile', author.username)
    else:
        return redirect('posts:profile', author.username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', author.username)
