from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
# from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Group, Post, User
from .settings import POSTS_PER_PAGE


# @cache_page(20)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {
        'group': group,
        'page': page,
    })


@login_required
def new_post(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if not form.is_valid():
        return render(request, 'new.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('index')


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {
        'page': page,
        'author': author,
    })


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
    comments = post.comments.filter(post=post)
    form = CommentForm()
    return render(request, 'post.html', {
        'post': post,
        'author': post.author,
        'comments': comments,
        'form': form,
    })


def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect('post', username, post_id)
    post = get_object_or_404(Post, author=request.user, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if not form.is_valid():
        return render(request, 'new.html', {
            'form': form,
            'post': post,
        })
    form.save()
    return redirect('post', username, post_id)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm(request.POST or None)
    # if request.method == 'POST' and request.user.is_authenticated:
    #     form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    # form = CommentForm()
    return redirect('post', username, post_id)


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {
        'path': request.path
    }, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
