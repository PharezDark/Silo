from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from .models import Post
import redis

# Create your views here.

r = redis.Redis(host='127.0.0.1', port=6379, db=1)

class HomeTimelineView(LoginRequiredMixin, ListView):
    template_name = 'posts/timeline.html'
    context_object_name = 'posts'
    paginate_by = 30

    def get_queryset(self):
        tech = int(self.request.GET.get('tech', 50))
        art = int(self.request.GET.get('art', 50))
        queryset = Post.objects.filter(author__followers=self.request.user)

        if tech < 20: queryset = queryset.exclude(category='tech')
        if art < 20: queryset = queryset.exclude(category='art')

        if tech > art:
            return queryset.filter(category__in=['tech', 'general']).order_by('-created_at')
        elif art > tech:
            return queryset.filter(category__in=['art', 'general']).order_by('-created_at')

        return queryset.order_by('-created_at')


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['category', 'content_markdown', 'canvas_image']
    template_name = 'posts/create_post.html'
    success_url = reverse_lazy('posts:timeline')

    def form_valid(self, form):
        # Automatically bind the post author to the logged-in user session
        form.instance.author = self.request.user
        return super().form_valid(form)