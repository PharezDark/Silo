from django.db.models import Q
from django.urls import path
from .views import InboxView, start_chat_view
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Thread


# Inline detail view shortcut to load messages inside the template shell
@login_required
def chat_room_view(request, thread_id):
    threads = Thread.objects.filter(Q(first_user=request.user) | Q(second_user=request.user)).order_by('-updated_at')
    active_thread = get_object_or_404(Thread, id=thread_id)
    messages = active_thread.messages.all()

    # Identify who you are talking to
    other_user = active_thread.second_user if request.user == active_thread.first_user else active_thread.first_user

    return render(request, 'chat/inbox.html', {
        'threads': threads,
        'active_thread': active_thread,
        'messages': messages,
        'other_user': other_user
    })


app_name = 'chat'

urlpatterns = [
    path('', InboxView.as_view(), name='inbox'),
    path('<int:thread_id>/', chat_room_view, name='room'),
    path('initiate/<str:username>/', start_chat_view, name='start_chat'),
]