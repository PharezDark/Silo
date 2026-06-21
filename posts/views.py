import redis
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from .models import Post

# Create your views here.

r = redis.Redis(host='127.0.0.1', port=6379, db=1)


class WelcomePageView(TemplateView):
    template_name = 'pages/welcome.html'

    def dispatch(self, request, *args, **kwargs):
        # If the user is already logged in, skip the welcome page and send them straight to the feed
        if request.user.is_authenticated:
            return redirect('posts:timeline')
        return super().dispatch(request, *args, **kwargs)


class HomeTimelineView(ListView):
    template_name = 'posts/timeline.html'
    context_object_name = 'posts'
    paginate_by = 30

    def get_queryset(self):
        # 1. Get the baseline content curation weights from the slider parameters
        tech = int(self.request.GET.get('tech', 50))
        art = int(self.request.GET.get('art', 50))

        # 2. Check if the user session is authenticated before running parameters
        if self.request.user.is_authenticated:
            # Filter posts: Must be from a user they follow OR written by them
            queryset = Post.objects.filter(
                Q(author__followers=self.request.user) | Q(author=self.request.user)
            ).distinct()
        else:
            # Fallback for anonymous guests viewing the open portal
            queryset = Post.objects.all()

        # 3. Apply the layout range matrix filtering sliders
        if tech < 20:
            queryset = queryset.exclude(category='tech')
        if art < 20:
            queryset = queryset.exclude(category='art')

        # 4. Return newest posts first
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Keep track of the slider states so the frontend inputs retain their positions
        context['tech_weight'] = self.request.GET.get('tech', 50)
        context['art_weight'] = self.request.GET.get('art', 50)
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['content_markdown', 'category', 'canvas_image']
    template_name = 'posts/create_post.html'
    success_url = reverse_lazy('posts:timeline')

    def form_valid(self, form):
        # Tie the logged-in user session to the post author field
        form.instance.author = self.request.user
        return super().form_valid(form)


class ToggleLikeView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        # Fetches the post by its UUID string
        post = get_object_or_404(Post, id=post_id)

        # Check if the user has already liked the post
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            is_liked = False
        else:
            post.likes.add(request.user)
            is_liked = True

        return JsonResponse({
            "success": True,
            "is_liked": is_liked,
            "like_count": post.likes.count()
        })