"""
Conversations Views - عروض المحادثات والرسائل المباشرة
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib import messages
from services.models import Service

from .models import Conversation, Message


@login_required
def inbox_view(request):
    """عرض صندوق المحادثات لجميع محادثات المستخدم"""
    conversations = Conversation.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).select_related('sender', 'receiver', 'service', 'last_message').order_by('-updated_at')

    return render(request, 'conversations/inbox.html', {
        'conversations': conversations,
    })


@login_required
def chat_detail_view(request, conversation_id):
    """عرض تفاصيل محادثة محددة والرسائل"""
    conversation = get_object_or_404(
        Conversation.objects.filter(Q(sender=request.user) | Q(receiver=request.user)),
        id=conversation_id
    )

    # تحديد الرسائل كمقروءة
    conversation.mark_as_read(request.user)

    messages_list = conversation.messages.all().select_related('sender').order_by('created_at')
    other_user = conversation.get_other_user(request.user)

    return render(request, 'conversations/chat.html', {
        'conversation': conversation,
        'messages_list': messages_list,
        'other_user': other_user,
    })


@login_required
@require_POST
def send_message_view(request, conversation_id):
    """إرسال رسالة داخل محادثة"""
    conversation = get_object_or_404(
        Conversation.objects.filter(Q(sender=request.user) | Q(receiver=request.user)),
        id=conversation_id
    )

    content = request.POST.get('content', '').strip()
    if content:
        msg = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content,
            message_type=Message.MessageType.TEXT
        )

        conversation.last_message = msg
        if request.user == conversation.sender:
            conversation.receiver_unread_count += 1
        else:
            conversation.sender_unread_count += 1
        conversation.save()

    return redirect('conversations:chat_detail', conversation_id=conversation.id)


@login_required
def start_conversation_view(request, recipient_id):
    """بدء محادثة جديدة مع مستخدم أو بائع"""
    recipient = get_object_or_404(User, id=recipient_id)

    if recipient == request.user:
        messages.warning(request, "لا يمكنك بدء محادثة مع نفسك.")
        return redirect('services:service_list')

    service_id = request.GET.get('service_id')
    service = None
    if service_id:
        service = Service.objects.filter(id=service_id, is_active=True).first()

    # البحث عن محادثة سابقة بين الطرفين
    conversation = Conversation.objects.filter(
        (Q(sender=request.user) & Q(receiver=recipient)) |
        (Q(sender=recipient) & Q(receiver=request.user))
    ).first()

    if not conversation:
        conversation = Conversation.objects.create(
            sender=request.user,
            receiver=recipient,
            service=service
        )
    elif service and not conversation.service:
        conversation.service = service
        conversation.save(update_fields=['service'])

    return redirect('conversations:chat_detail', conversation_id=conversation.id)
