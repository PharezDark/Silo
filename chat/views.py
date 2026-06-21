from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Thread, ChatMessage

User = get_user_model()

# ================= CLASS-BASED INBOX VIEW (RECOMMENDED) =================

class InboxView(LoginRequiredMixin, ListView):
    """Class-based dashboard view displaying all conversations involving the logged-in user."""
    model = Thread
    template_name = 'chat/inbox.html'
    context_object_name = 'threads'

    def get_queryset(self):
        return Thread.objects.filter(
            Q(first_user=self.request.user) | Q(second_user=self.request.user)
        ).order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_thread'] = None  # None on the landing dashboard screen
        return context


# ================= FUNCTION-BASED INBOX VIEW (ALTERNATIVE) =================

@login_required
def inbox_view(request):
    """Function-based dashboard view displaying all conversations involving the logged-in user."""
    # Fetch all threads where the current user is a participant
    threads = Thread.objects.filter(
        Q(first_user=request.user) | Q(second_user=request.user)
    ).order_by('-updated_at')

    context = {
        'threads': threads,
        'active_thread': None, # None on the landing dashboard screen
    }
    return render(request, 'chat/inbox.html', context)


# ================= UTILITY CHAT ROUTE =================

def start_chat_view(request, username):
    """Quick utility view to start a chat with someone from their profile or explore page."""
    other_user = get_object_or_404(User, username=username)
    if other_user == request.user:
        return redirect('chat:inbox')

    # Ensure first_user always has the lower ID to keep the unique combination consistent
    user1, user2 = sorted([request.user, other_user], key=lambda u: u.id)

    thread, created = Thread.objects.get_or_create(first_user=user1, second_user=user2)
    return redirect('chat:room', thread_id=thread.id)