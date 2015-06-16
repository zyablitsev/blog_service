from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from .models import User, Post, PostRead, Subscription


class UserListView(ListView):
    model = User
    template_name = 'list_users.html'


class BlogView(ListView):
    model = Post
    template_name = 'list_posts_with_buttons.html'

    def get_queryset(self):
        return Post.objects.filter(user_id=self.kwargs['user_id'])

    def get_context_data(self, **kwargs):
        context = super(BlogView, self).get_context_data(**kwargs)
        context['subscription'] = Subscription.objects.filter(
            subscriber=self.request.user,
            subscription=self.kwargs['user_id']).first()
        context['blog_id'] = int(self.kwargs['user_id'])
        return context


class FeedView(ListView):
    model = Post
    template_name = 'list_posts.html'

    def get_queryset(self):
        return self.request.user.feed()


class SubscriptionCreateView(CreateView):
    model = Subscription
    success_url = reverse_lazy('index')
    fields = ()

    def form_valid(self, form):
        subscription_user = User.objects.get(pk=self.kwargs['user_id'])
        form.instance.subscriber = self.request.user
        form.instance.subscription = subscription_user
        return super(SubscriptionCreateView, self).form_valid(form)


class SubscriptionDeleteView(DeleteView):
    model = Subscription
    success_url = reverse_lazy('index')
    fields = ()

    def form_valid(self, form):
        subscription_user = User.objects.get(pk=self.kwargs['user_id'])
        form.instance.subscriber = self.request.user
        form.instance.subscription = subscription_user
        return super(SubscriptionCreateView, self).form_valid(form)


class PostReadCreateView(CreateView):
    model = PostRead
    success_url = reverse_lazy('index')
    fields = ()

    def form_valid(self, form):
        post = Post.objects.get(pk=self.kwargs['pk'])
        subscription_user = post.user
        subscription = Subscription.objects.get(
            subscriber = self.request.user,
            subscription = subscription_user)
        form.instance.blog_post = post
        form.instance.subscription = subscription
        return super(PostReadCreateView, self).form_valid(form)


class PostView(DetailView):
    model = Post
    template_name = 'post.html'

    def get_context_data(self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)
        subscription = Subscription.objects.filter(
            subscriber=self.request.user,
            subscription=self.get_object().user).first()
        context['subscription'] = bool(subscription)
        context['readed'] = bool(PostRead.objects.filter(
            blog_post=self.get_object(), subscription=subscription).first())
        return context


class PostCreateView(CreateView):
    model = Post
    template_name = 'add.html'
    fields = ['title', 'text']
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(PostCreateView, self).form_valid(form)
