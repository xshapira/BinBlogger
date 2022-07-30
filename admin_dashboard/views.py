from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, DeleteView, ListView, UpdateView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from posts.models import Post, Category
from user_dashboard.views import get_posts_cats_tags

User = get_user_model()
users = User.objects.all()
posts = Post.objects.all().order_by('-created_on')
categories = Category.objects.all()

# view for admin Dashboard home page
class AdminDbView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return bool(self.request.user.is_superuser)

    def get(self, request, *args, **kargs):
        global users
        users = users.order_by('date_joined')
        lead_admin = users.filter(is_superuser=True).order_by('date_joined')[0]

        posts, _, tag_tup_list = get_posts_cats_tags(request, tag_count=15)
        if featured_posts := posts.filter(featured=True).order_by('-updated_on'):
            featured_post = featured_posts[0]
        else:
            featured_post = None

        context = {
            'users': users,
            'posts': posts,
            'categories': categories,
            'tag_tup_list': tag_tup_list,
            'featured_post': featured_post,
            'lead_admin': lead_admin,
        }

        return render(request, 'admin_dashboard/admin_site.html', context)

#  admin dashboard all categories view
class ADashAllCategoryView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Category
    template_name = "admin_dashboard/admin_posts_cats_tags_users.html"
    context_object_name = 'categories'

    def test_func(self):
        return bool(self.request.user.is_superuser)

#  admin dashboard all tags view
class ADashAllTagView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return bool(self.request.user.is_superuser)

    def get(self, request, *args, **kargs):
        posts, cat_tup_list, tag_tup_list = get_posts_cats_tags(request, tag_count=15)

        context = {
            'tag_tup_list': tag_tup_list,
        }
        return render(request, 'admin_dashboard/admin_posts_cats_tags_users.html', context)

 #  admin dashboard all user view
class ADashAllUserView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = "admin_dashboard/admin_posts_cats_tags_users.html"
    context_object_name = 'users'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_users = users.order_by('date_joined')
        lead_admin = all_users.filter(is_superuser=True).order_by('date_joined')[0]

        context["lead_admin"] = lead_admin
        return context

    def test_func(self):
        return bool(self.request.user.is_superuser)

#  admin dashboard all posts view
class ADashAllPostsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Post
    template_name = "admin_dashboard/admin_posts_cats_tags_users.html"
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if featured_posts := Post.objects.filter(featured=True).order_by(
            '-updated_on'
        ):
            featured_post = featured_posts[0]
        else:
            featured_post = None

        context["featured_post"] = featured_post
        return context

    def test_func(self):
        return bool(self.request.user.is_superuser)

# post that will be deleted from admin dashboard -view
class DeletePostbyAdminView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'admin_dashboard/confirm-delete.html'
    success_url = '/binblogger-admin/dashboard/'
    success_message = 'Successfully deleted.'

    def test_func(self):
        return bool(self.request.user.is_superuser)


# category that will be deleted from admin dashboard - view
class DeleteCategorybyAdmin(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Category
    template_name = 'admin_dashboard/confirm-delete.html'
    success_url = '/binblogger-admin/dashboard/'
    success_message = 'Successfully Deleted. '

    def test_func(self):
        return bool(self.request.user.is_superuser)

# category update view on admin dashboard - view
class UpdateCategorybyAdmin(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Category
    fields = ['category']
    template_name = 'admin_dashboard/update-category.html'
    success_url = '/binblogger-admin/dashboard/'
    success_message = 'Updated Successfully.'

    def test_func(self):
        return bool(self.request.user.is_superuser)

# super user check fucntion for restricting user -funtion for @user_passes_test decorator
def super_user_check(user):
    return bool(user.is_superuser)

# admin's power to make a post to featured post
@login_required
@user_passes_test(super_user_check)
def make_the_post_featured(request, pk):
    if post := get_object_or_404(Post, pk=pk):
        post.featured = True
        post.save()
        messages.success(request, 'Featured successfully ')
        return redirect('admin-dashboard')

#  admin dashboard selected categories's posts view
@login_required
@user_passes_test(super_user_check)
def admin_dashboard_filter_category_posts_view(request, pk):
    global users
    users = users.order_by('date_joined')
    posts, _, tag_tup_list = get_posts_cats_tags(request, tag_count=10)
    category = get_object_or_404(Category, pk=pk)
    cat_posts = category.post_set.all()

    if len(cat_posts) > 0:
        if featured_posts := cat_posts.filter(featured=True).order_by(
            '-updated_on'
        ):
            featured_post = featured_posts[0]
        else:
            featured_post = None
    else:
        posts = None
        featured_post = None

    context = {
        'posts': cat_posts,
        'featured_post': featured_post,
        'category': category,
        'users': users,
        'categories': categories,
        'tag_tup_list': tag_tup_list,
    }

    return render(request, 'admin_dashboard/admin_site.html', context)

#  admin dashboard selected tag's posts view
@login_required
@user_passes_test(super_user_check)
def admin_dashboard_filter_tag_posts_view(request, tag):
    global users
    posts = Post.objects.filter(tags__icontains=tag).all()
    users = users.order_by('date_joined')
    _, cat_tup_list, tag_tup_list = get_posts_cats_tags(request, tag_count=10)

    if featured_posts := posts.filter(featured=True).order_by('-updated_on'):
        featured_post = featured_posts[0]
    else:
        featured_post = None

    context = {
        'posts': posts,
        'featured_post': featured_post,
        'tag_tup_list': tag_tup_list,
        'users': users,
        'categories': categories,
        'tag': tag,
    }

    return render(request, 'admin_dashboard/admin_site.html', context)

#  admin dashboard selected user's posts view
@login_required
@user_passes_test(super_user_check)
def admin_dashboard_filter_user_posts_view(request, username):
    posts = Post.objects.filter(author__username=username)
    global users
    users = users.order_by('date_joined')
    _, cat_tup_list, tag_tup_list = get_posts_cats_tags(request, tag_count=10)
    if featured_posts := posts.filter(featured=True).order_by('-updated_on'):
        featured_post = featured_posts[0]
    else:
        featured_post = None

    context = {
        'posts': posts,
        'featured_post': featured_post,
        'user': username,
        'users': users,
        'categories': categories,
        'tag_tup_list': tag_tup_list,
    }

    return render(request, 'admin_dashboard/admin_site.html', context)

# make user as admin view
@login_required
@user_passes_test(super_user_check)
def make_user_as_admin(request, username):
    user = get_object_or_404(User, username=username)

    if not user.is_superuser:
        user.is_stuff = True
        user.is_superuser = True
        user.save()
        messages.success(request, f'{user.username} is now admin')

    else:
        messages.error(request, 'Error occured !')

    return redirect('admin-dashboard')

# remove user as admin view
@login_required
@user_passes_test(super_user_check)
def remove_user_admin_as_admin(request, username):
    global users
    admins = users.filter(is_superuser=True).order_by('date_joined')
    lead_admin = admins[0]
    user = get_object_or_404(User, username=username)

    if user.is_superuser and user != lead_admin and user != request.user:
        user.is_superuser = False
        user.is_stuff = False
        user.save()
        messages.success(request, f'{user.username} is removed as admin')
    else:
        messages.error(request, 'Error occured !')

    return redirect('admin-dashboard')

# remove user from database view
@login_required
@user_passes_test(super_user_check)
def remove_user_from_db(request, pk):
    global users
    admins = users.filter(is_superuser=True).order_by('date_joined')
    lead_admin = admins[0]

    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        if user not in [lead_admin, request.user]:
            user.delete()
            messages.success(request, f'{user.username} removed successfully')
        else:
            messages.error(request, 'Error occured !')
        return redirect('admin-dashboard')
    return render(request, 'admin_dashboard/confirm-delete.html')
