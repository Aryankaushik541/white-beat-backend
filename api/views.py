from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User, Group as DjangoGroup
from django.contrib.auth import authenticate
from django.db.models import Count, Sum, Q, Max, Prefetch
from django.utils import timezone
from datetime import timedelta
import traceback
import time
import uuid

from .models import (
    UserProfile, Conversation, Message, MessageReaction,
    Call, Status, StatusView, Contact, Group, GroupMembership,
    APILog, SystemStats
)

def log_api_request(request, endpoint, status_code, response_time):
    """Helper function to log API requests"""
    try:
        user = request.user if request.user.is_authenticated else None
        ip = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        APILog.objects.create(
            endpoint=endpoint,
            method=request.method,
            user=user,
            status_code=status_code,
            response_time=response_time,
            ip_address=ip,
            user_agent=user_agent
        )
    except Exception as e:
        print(f"Error logging API request: {e}")

def is_user_admin(user):
    """Check if user is in Admin group"""
    return user.groups.filter(name='Admin').exists()

def get_or_create_conversation(user1, user2):
    """Get or create a conversation between two users"""
    # Ensure consistent ordering to avoid duplicates
    if user1.id > user2.id:
        user1, user2 = user2, user1
    
    conversation, created = Conversation.objects.get_or_create(
        user1=user1,
        user2=user2
    )
    return conversation

# ============= AUTHENTICATION ENDPOINTS =============

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """User signup - creates regular user account"""
    start_time = time.time()
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', f'{username}@whitebeat.com')
    phone_number = request.data.get('phone_number', '')
    
    if not username or not password:
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/signup/', 400, response_time)
        return Response(
            {'error': 'Username and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if username already exists
    if User.objects.filter(username=username).exists():
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/signup/', 400, response_time)
        return Response(
            {'error': 'Username already exists'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if email already exists
    if User.objects.filter(email=email).exists():
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/signup/', 400, response_time)
        return Response(
            {'error': 'Email already exists'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Create new regular user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            is_staff=False,
            is_superuser=False
        )
        
        # Create user profile
        profile = UserProfile.objects.create(
            user=user,
            role='user',
            is_active_session=True,
            phone_number=phone_number,
            is_online=True
        )
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/signup/', 201, response_time)
        
        return Response({
            'success': True,
            'role': 'user',
            'username': username,
            'email': email,
            'user_id': user.id,
            'message': 'Account created successfully! You can now login.'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/signup/', 500, response_time)
        return Response(
            {'error': f'Failed to create account: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Handle user/admin login with Django authentication"""
    start_time = time.time()
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/login/', 400, response_time)
        return Response(
            {'error': 'Username and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Authenticate with Django
    user = authenticate(username=username, password=password)
    
    if user is not None:
        # Check if user is in Admin group
        is_admin = is_user_admin(user)
        
        # Update profile
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': 'admin' if is_admin else 'user'}
        )
        profile.role = 'admin' if is_admin else 'user'
        profile.is_active_session = True
        profile.is_online = True
        profile.last_seen = timezone.now()
        profile.save()
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/login/', 200, response_time)
        
        return Response({
            'role': 'admin' if is_admin else 'user',
            'username': username,
            'email': user.email,
            'message': f'{"Admin" if is_admin else "User"} login successful',
            'user_id': user.id,
            'is_admin_group': is_admin,
            'profile': {
                'avatar': profile.avatar,
                'status': profile.status,
                'phone_number': profile.phone_number,
                'bio': profile.bio
            }
        })
    else:
        # Invalid credentials
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/login/', 401, response_time)
        return Response(
            {'error': 'Invalid username or password'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    """Handle user logout"""
    start_time = time.time()
    username = request.data.get('username')
    
    if not username:
        return Response({'error': 'Username required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(username=username)
        profile = user.profile
        profile.is_online = False
        profile.is_active_session = False
        profile.last_seen = timezone.now()
        profile.save()
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/logout/', 200, response_time)
        
        return Response({'success': True, 'message': 'Logged out successfully'})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# ============= USER MANAGEMENT ENDPOINTS =============

@api_view(['GET'])
@permission_classes([AllowAny])
def get_users(request):
    """Get list of all users for chat"""
    start_time = time.time()
    current_username = request.GET.get('username')
    search = request.GET.get('search', '')
    
    if not current_username:
        return Response({'error': 'Username required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        current_user = User.objects.get(username=current_username)
        
        # Get all users except current user
        users = User.objects.exclude(id=current_user.id).select_related('profile')
        
        # Apply search filter
        if search:
            users = users.filter(
                Q(username__icontains=search) | 
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        users_list = []
        for user in users:
            profile = getattr(user, 'profile', None)
            users_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.get_full_name() or user.username,
                'avatar': profile.avatar if profile else None,
                'status': profile.status if profile else 'Hey there! I am using White Beat',
                'bio': profile.bio if profile else '',
                'is_online': profile.is_online if profile else False,
                'last_seen': profile.last_seen.isoformat() if profile and profile.last_seen else None,
                'phone_number': profile.phone_number if profile else None
            })
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/users/', 200, response_time)
        
        return Response({
            'success': True,
            'users': users_list,
            'count': len(users_list)
        })
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_profile(request):
    """Get user profile details"""
    start_time = time.time()
    username = request.GET.get('username')
    
    if not username:
        return Response({'error': 'Username required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(username=username)
        profile = user.profile
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/user-profile/', 200, response_time)
        
        return Response({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.get_full_name() or user.username,
                'avatar': profile.avatar,
                'status': profile.status,
                'bio': profile.bio,
                'phone_number': profile.phone_number,
                'is_online': profile.is_online,
                'last_seen': profile.last_seen.isoformat() if profile.last_seen else None,
                'joined_date': profile.joined_date.isoformat(),
                'total_messages': profile.total_messages,
                'privacy': {
                    'profile_photo': profile.profile_photo_privacy,
                    'status': profile.status_privacy,
                    'last_seen': profile.last_seen_privacy
                }
            }
        })
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def update_user_profile(request):
    """Update user profile"""
    start_time = time.time()
    username = request.data.get('username')
    
    if not username:
        return Response({'error': 'Username required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(username=username)
        profile = user.profile
        
        # Update fields
        if 'avatar' in request.data:
            profile.avatar = request.data['avatar']
        if 'status' in request.data:
            profile.status = request.data['status']
        if 'bio' in request.data:
            profile.bio = request.data['bio']
        if 'phone_number' in request.data:
            profile.phone_number = request.data['phone_number']
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
        
        # Update privacy settings
        if 'profile_photo_privacy' in request.data:
            profile.profile_photo_privacy = request.data['profile_photo_privacy']
        if 'status_privacy' in request.data:
            profile.status_privacy = request.data['status_privacy']
        if 'last_seen_privacy' in request.data:
            profile.last_seen_privacy = request.data['last_seen_privacy']
        
        user.save()
        profile.save()
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/update-profile/', 200, response_time)
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'profile': {
                'avatar': profile.avatar,
                'status': profile.status,
                'bio': profile.bio,
                'phone_number': profile.phone_number
            }
        })
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# ============= MESSAGING ENDPOINTS =============

@api_view(['GET'])
@permission_classes([AllowAny])
def get_conversations(request):
    """Get all conversations for a user"""
    start_time = time.time()
    username = request.GET.get('username')
    
    if not username:
        return Response({'error': 'Username required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(username=username)
        
        # Get all conversations where user is participant
        conversations = Conversation.objects.filter(
            Q(user1=user) | Q(user2=user)
        ).select_related('user1__profile', 'user2__profile').prefetch_related('messages')
        
        conversations_list = []
        for conv in conversations:
            other_user = conv.get_other_user(user)
            other_profile = getattr(other_user, 'profile', None)
            
            # Get last message
            last_message = conv.messages.filter(deleted_for_everyone=False).last()
            
            # Count unread messages
            unread_count = conv.messages.filter(
                receiver=user,
                is_read=False,
                deleted_for_everyone=False
            ).count()
            
            # Check if archived or muted
            is_archived = conv.is_archived_by_user1 if conv.user1 == user else conv.is_archived_by_user2
            is_muted = conv.is_muted_by_user1 if conv.user1 == user else conv.is_muted_by_user2
            
            conversations_list.append({
                'id': conv.id,
                'other_user': {
                    'id': other_user.id,
                    'username': other_user.username,
                    'email': other_user.email,
                    'full_name': other_user.get_full_name() or other_user.username,
                    'avatar': other_profile.avatar if other_profile else None,
                    'status': other_profile.status if other_profile else '',
                    'is_online': other_profile.is_online if other_profile else False,
                    'last_seen': other_profile.last_seen.isoformat() if other_profile and other_profile.last_seen else None
                },
                'last_message': {
                    'content': last_message.content if last_message and last_message.message_type == 'text' else f'[{last_message.message_type}]' if last_message else '',
                    'created_at': last_message.created_at.isoformat() if last_message else None,
                    'sender': last_message.sender.username if last_message else None,
                    'is_read': last_message.is_read if last_message else False
                } if last_message else None,
                'unread_count': unread_count,
                'is_archived': is_archived,
                'is_muted': is_muted,
                'updated_at': conv.updated_at.isoformat()
            })
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/conversations/', 200, response_time)
        
        return Response({
            'success': True,
            'conversations': conversations_list,
            'count': len(conversations_list)
        })
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_messages(request):
    """Get all messages in a conversation"""
    start_time = time.time()
    username = request.GET.get('username')
    other_username = request.GET.get('other_username')
    limit = int(request.GET.get('limit', 50))
    offset = int(request.GET.get('offset', 0))
    
    if not username or not other_username:
        return Response(
            {'error': 'Both username and other_username required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(username=username)
        other_user = User.objects.get(username=other_username)
        
        # Get or create conversation
        conversation = get_or_create_conversation(user, other_user)
        
        # Get messages with pagination
        messages = conversation.messages.filter(
            deleted_for_everyone=False
        ).select_related('sender', 'receiver', 'reply_to').prefetch_related('reactions')[offset:offset+limit]
        
        messages_list = []
        for msg in messages:
            # Get reactions
            reactions = []
            for reaction in msg.reactions.all():
                reactions.append({
                    'user': reaction.user.username,
                    'type': reaction.reaction_type,
                    'emoji': reaction.get_reaction_type_display()
                })
            
            messages_list.append({
                'id': msg.id,
                'sender': msg.sender.username,
                'receiver': msg.receiver.username,
                'message_type': msg.message_type,
                'content': msg.content,
                'media_url': msg.media_url,
                'thumbnail_url': msg.thumbnail_url,
                'is_read': msg.is_read,
                'is_forwarded': msg.is_forwarded,
                'reply_to': {
                    'id': msg.reply_to.id,
                    'content': msg.reply_to.content,
                    'sender': msg.reply_to.sender.username
                } if msg.reply_to else None,
                'reactions': reactions,
                'created_at': msg.created_at.isoformat(),
                'edited_at': msg.edited_at.isoformat() if msg.edited_at else None,
                'is_mine': msg.sender == user
            })
        
        # Mark messages as read
        conversation.messages.filter(receiver=user, is_read=False).update(is_read=True)
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/messages/', 200, response_time)
        
        return Response({
            'success': True,
            'conversation_id': conversation.id,
            'messages': messages_list,
            'count': len(messages_list),
            'has_more': conversation.messages.count() > offset + limit
        })
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_message(request):
    """Send a message to another user or group"""
    start_time = time.time()
    sender_username = request.data.get('sender')
    receiver_username = request.data.get('receiver')
    group_id = request.data.get('group_id')
    content = request.data.get('content')
    message_type = request.data.get('message_type', 'text')
    media_url = request.data.get('media_url')
    thumbnail_url = request.data.get('thumbnail_url')
    reply_to_id = request.data.get('reply_to')
    
    if not sender_username:
        return Response({'error': 'Sender required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not receiver_username and not group_id:
        return Response({'error': 'Either receiver or group_id required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not content and not media_url:
        return Response({'error': 'Either content or media_url required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        sender = User.objects.get(username=sender_username)
        
        # Handle group message
        if group_id:
            group = Group.objects.get(id=group_id)
            
            # Check if sender is member
            if not group.members.filter(id=sender.id).exists():
                return Response({'error': 'You are not a member of this group'}, status=status.HTTP_403_FORBIDDEN)
            
            # Check if only admins can send
            if group.only_admins_can_send and not group.admins.filter(id=sender.id).exists():
                return Response({'error': 'Only admins can send messages in this group'}, status=status.HTTP_403_FORBIDDEN)
            
            # Create message
            message = Message.objects.create(
                group=group,
                sender=sender,
                message_type=message_type,
                content=content,
                media_url=media_url,
                thumbnail_url=thumbnail_url,
                reply_to_id=reply_to_id
            )
            
            # Update sender profile
            sender_profile, _ = UserProfile.objects.get_or_create(user=sender)
            sender_profile.total_messages += 1
            sender_profile.save()
            
            response_time = (time.time() - start_time) * 1000
            log_api_request(request, '/api/send-message/', 201, response_time)
            
            return Response({
                'success': True,
                'message': {
                    'id': message.id,
                    'sender': sender.username,
                    'group_id': group.id,
                    'group_name': group.name,
                    'message_type': message.message_type,
                    'content': message.content,
                    'media_url': message.media_url,
                    'created_at': message.created_at.isoformat()
                }
            }, status=status.HTTP_201_CREATED)
        
        # Handle direct message
        else:
            receiver = User.objects.get(username=receiver_username)
            
            # Get or create conversation
            conversation = get_or_create_conversation(sender, receiver)
            
            # Create message
            message = Message.objects.create(
                conversation=conversation,
                sender=sender,
                receiver=receiver,
                message_type=message_type,
                content=content,
                media_url=media_url,
                thumbnail_url=thumbnail_url,
                reply_to_id=reply_to_id
            )
            
            # Update sender profile
            sender_profile, _ = UserProfile.objects.get_or_create(user=sender)
            sender_profile.total_messages += 1
            sender_profile.save()
            
            response_time = (time.time() - start_time) * 1000
            log_api_request(request, '/api/send-message/', 201, response_time)
            
            return Response({
                'success': True,
                'message': {
                    'id': message.id,
                    'sender': sender.username,
                    'receiver': receiver.username,
                    'message_type': message.message_type,
                    'content': message.content,
                    'media_url': message.media_url,
                    'created_at': message.created_at.isoformat(),
                    'is_read': message.is_read
                }
            }, status=status.HTTP_201_CREATED)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Group.DoesNotExist:
        return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def delete_message(request):
    """Delete a message"""
    start_time = time.time()
    message_id = request.data.get('message_id')
    username = request.data.get('username')
    delete_for_everyone = request.data.get('delete_for_everyone', False)
    
    if not message_id or not username:
        return Response({'error': 'message_id and username required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(username=username)
        message = Message.objects.get(id=message_id)
        
        # Check if user is sender
        if message.sender != user:
            return Response({'error': 'You can only delete your own messages'}, status=status.HTTP_403_FORBIDDEN)
        
        if delete_for_everyone:
            message.deleted_for_everyone = True
        message.is_deleted = True
        message.save()
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/delete-message/', 200, response_time)
        
        return Response({'success': True, 'message': 'Message deleted'})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Message.DoesNotExist:
        return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def edit_message(request):
    """Edit a message"""
    start_time = time.time()
    message_id = request.data.get('message_id')
    username = request.data.get('username')
    new_content = request.data.get('content')
    
    if not all([message_id, username, new_content]):
        return Response({'error': 'message_id, username, and content required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(username=username)
        message = Message.objects.get(id=message_id)
        
        # Check if user is sender
        if message.sender != user:
            return Response({'error': 'You can only edit your own messages'}, status=status.HTTP_403_FORBIDDEN)
        
        message.content = new_content
        message.edited_at = timezone.now()
        message.save()
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/edit-message/', 200, response_time)
        
        return Response({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'edited_at': message.edited_at.isoformat()
            }
        })
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Message.DoesNotExist:
        return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def react_to_message(request):
    """Add or update reaction to a message"""
    start_time = time.time()
    message_id = request.data.get('message_id')
    username = request.data.get('username')
    reaction_type = request.data.get('reaction_type')
    
    if not all([message_id, username, reaction_type]):
        return Response({'error': 'message_id, username, and reaction_type required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(username=username)
        message = Message.objects.get(id=message_id)
        
        # Create or update reaction
        reaction, created = MessageReaction.objects.update_or_create(
            message=message,
            user=user,
            defaults={'reaction_type': reaction_type}
        )
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/react-message/', 200, response_time)
        
        return Response({
            'success': True,
            'reaction': {
                'user': user.username,
                'type': reaction.reaction_type,
                'emoji': reaction.get_reaction_type_display()
            }
        })
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Message.DoesNotExist:
        return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def mark_as_read(request):
    """Mark messages as read"""
    start_time = time.time()
    username = request.data.get('username')
    conversation_id = request.data.get('conversation_id')
    
    if not username or not conversation_id:
        return Response(
            {'error': 'username and conversation_id required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(username=username)
        conversation = Conversation.objects.get(id=conversation_id)
        
        # Mark all messages from other user as read
        updated = conversation.messages.filter(
            receiver=user,
            is_read=False
        ).update(is_read=True)
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/mark-as-read/', 200, response_time)
        
        return Response({
            'success': True,
            'marked_read': updated
        })
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Conversation.DoesNotExist:
        return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)

# ============= GROUP ENDPOINTS =============

@api_view(['POST'])
@permission_classes([AllowAny])
def create_group(request):
    """Create a new group"""
    start_time = time.time()
    creator_username = request.data.get('creator')
    name = request.data.get('name')
    description = request.data.get('description', '')
    avatar = request.data.get('avatar', '')
    member_usernames = request.data.get('members', [])
    
    if not creator_username or not name:
        return Response({'error': 'creator and name required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        creator = User.objects.get(username=creator_username)
        
        # Create group
        group = Group.objects.create(
            name=name,
            description=description,
            avatar=avatar,
            created_by=creator
        )
        
        # Add creator as admin and member
        group.admins.add(creator)
        GroupMembership.objects.create(group=group, user=creator, is_admin=True)
        
        # Add other members
        for username in member_usernames:
            try:
                member = User.objects.get(username=username)
                GroupMembership.objects.create(group=group, user=member, is_admin=False)
            except User.DoesNotExist:
                pass
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/create-group/', 201, response_time)
        
        return Response({
            'success': True,
            'group': {
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'avatar': group.avatar,
                'created_by': creator.username,
                'member_count': group.members.count(),
                'created_at': group.created_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)
        
    except User.DoesNotExist:
        return Response({'error': 'Creator not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_groups(request):
    """Get all groups for a user"""
    start_time = time.time()
    username = request.GET.get('username')
    
    if not username:
        return Response({'error': 'Username required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(username=username)
        
        # Get all groups where user is a member
        groups = Group.objects.filter(members=user).prefetch_related('members', 'admins', 'messages')
        
        groups_list = []
        for group in groups:
            # Get last message
            last_message = group.messages.filter(deleted_for_everyone=False).last()
            
            # Count unread messages
            unread_count = group.messages.filter(
                deleted_for_everyone=False
            ).exclude(sender=user).exclude(read_by=user).count()
            
            # Check if user is admin
            is_admin = group.admins.filter(id=user.id).exists()
            
            groups_list.append({
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'avatar': group.avatar,
                'created_by': group.created_by.username if group.created_by else None,
                'member_count': group.members.count(),
                'is_admin': is_admin,
                'last_message': {
                    'content': last_message.content if last_message and last_message.message_type == 'text' else f'[{last_message.message_type}]' if last_message else '',
                    'sender': last_message.sender.username if last_message else None,
                    'created_at': last_message.created_at.isoformat() if last_message else None
                } if last_message else None,
                'unread_count': unread_count,
                'updated_at': group.updated_at.isoformat()
            })
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/groups/', 200, response_time)
        
        return Response({
            'success': True,
            'groups': groups_list,
            'count': len(groups_list)
        })
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_group_messages(request):
    """Get messages in a group"""
    start_time = time.time()
    group_id = request.GET.get('group_id')
    limit = int(request.GET.get('limit', 50))
    offset = int(request.GET.get('offset', 0))
    
    if not group_id:
        return Response({'error': 'group_id required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        group = Group.objects.get(id=group_id)
        
        # Get messages with pagination
        messages = group.messages.filter(
            deleted_for_everyone=False
        ).select_related('sender', 'reply_to').prefetch_related('reactions')[offset:offset+limit]
        
        messages_list = []
        for msg in messages:
            # Get reactions
            reactions = []
            for reaction in msg.reactions.all():
                reactions.append({
                    'user': reaction.user.username,
                    'type': reaction.reaction_type,
                    'emoji': reaction.get_reaction_type_display()
                })
            
            messages_list.append({
                'id': msg.id,
                'sender': {
                    'username': msg.sender.username,
                    'avatar': msg.sender.profile.avatar if hasattr(msg.sender, 'profile') else None
                },
                'message_type': msg.message_type,
                'content': msg.content,
                'media_url': msg.media_url,
                'thumbnail_url': msg.thumbnail_url,
                'is_forwarded': msg.is_forwarded,
                'reply_to': {
                    'id': msg.reply_to.id,
                    'content': msg.reply_to.content,
                    'sender': msg.reply_to.sender.username
                } if msg.reply_to else None,
                'reactions': reactions,
                'created_at': msg.created_at.isoformat(),
                'edited_at': msg.edited_at.isoformat() if msg.edited_at else None
            })
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/group-messages/', 200, response_time)
        
        return Response({
            'success': True,
            'group_id': group.id,
            'group_name': group.name,
            'messages': messages_list,
            'count': len(messages_list),
            'has_more': group.messages.count() > offset + limit
        })
        
    except Group.DoesNotExist:
        return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def add_group_member(request):
    """Add member to group"""
    start_time = time.time()
    group_id = request.data.get('group_id')
    admin_username = request.data.get('admin')
    member_username = request.data.get('member')
    
    if not all([group_id, admin_username, member_username]):
        return Response({'error': 'group_id, admin, and member required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        group = Group.objects.get(id=group_id)
        admin = User.objects.get(username=admin_username)
        member = User.objects.get(username=member_username)
        
        # Check if admin has permission
        if not group.admins.filter(id=admin.id).exists():
            return Response({'error': 'Only admins can add members'}, status=status.HTTP_403_FORBIDDEN)
        
        # Add member
        GroupMembership.objects.get_or_create(group=group, user=member, defaults={'is_admin': False})
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/add-group-member/', 200, response_time)
        
        return Response({
            'success': True,
            'message': f'{member_username} added to group',
            'member_count': group.members.count()
        })
        
    except Group.DoesNotExist:
        return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def remove_group_member(request):
    """Remove member from group"""
    start_time = time.time()
    group_id = request.data.get('group_id')
    admin_username = request.data.get('admin')
    member_username = request.data.get('member')
    
    if not all([group_id, admin_username, member_username]):
        return Response({'error': 'group_id, admin, and member required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        group = Group.objects.get(id=group_id)
        admin = User.objects.get(username=admin_username)
        member = User.objects.get(username=member_username)
        
        # Check if admin has permission
        if not group.admins.filter(id=admin.id).exists():
            return Response({'error': 'Only admins can remove members'}, status=status.HTTP_403_FORBIDDEN)
        
        # Remove member
        GroupMembership.objects.filter(group=group, user=member).delete()
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/remove-group-member/', 200, response_time)
        
        return Response({
            'success': True,
            'message': f'{member_username} removed from group',
            'member_count': group.members.count()
        })
        
    except Group.DoesNotExist:
        return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# ============= CALL ENDPOINTS =============

@api_view(['POST'])
@permission_classes([AllowAny])
def initiate_call(request):
    """Initiate a voice or video call"""
    start_time = time.time()
    caller_username = request.data.get('caller')
    receiver_username = request.data.get('receiver')
    group_id = request.data.get('group_id')
    call_type = request.data.get('call_type', 'audio')
    
    if not caller_username:
        return Response({'error': 'Caller required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not receiver_username and not group_id:
        return Response({'error': 'Either receiver or group_id required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        caller = User.objects.get(username=caller_username)
        
        # Generate unique room ID
        room_id = str(uuid.uuid4())
        
        if group_id:
            group = Group.objects.get(id=group_id)
            call = Call.objects.create(
                caller=caller,
                group=group,
                call_type=call_type,
                status='initiated',
                room_id=room_id
            )
        else:
            receiver = User.objects.get(username=receiver_username)
            call = Call.objects.create(
                caller=caller,
                receiver=receiver,
                call_type=call_type,
                status='initiated',
                room_id=room_id
            )
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/initiate-call/', 201, response_time)
        
        return Response({
            'success': True,
            'call': {
                'id': call.id,
                'room_id': call.room_id,
                'call_type': call.call_type,
                'status': call.status,
                'started_at': call.started_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Group.DoesNotExist:
        return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def update_call_status(request):
    """Update call status (answer, reject, end)"""
    start_time = time.time()
    call_id = request.data.get('call_id')
    new_status = request.data.get('status')
    
    if not call_id or not new_status:
        return Response({'error': 'call_id and status required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        call = Call.objects.get(id=call_id)
        
        call.status = new_status
        
        if new_status == 'ongoing' and not call.answered_at:
            call.answered_at = timezone.now()
        elif new_status in ['completed', 'rejected', 'failed', 'missed']:
            call.ended_at = timezone.now()
            if call.answered_at:
                call.duration = int((call.ended_at - call.answered_at).total_seconds())
        
        call.save()
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/update-call-status/', 200, response_time)
        
        return Response({
            'success': True,
            'call': {
                'id': call.id,
                'status': call.status,
                'duration': call.duration,
                'ended_at': call.ended_at.isoformat() if call.ended_at else None
            }
        })
        
    except Call.DoesNotExist:
        return Response({'error': 'Call not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_call_history(request):
    """Get call history for a user"""
    start_time = time.time()
    username = request.GET.get('username')
    
    if not username:
        return Response({'error': 'Username required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(username=username)
        
        # Get all calls where user is caller or receiver
        calls = Call.objects.filter(
            Q(caller=user) | Q(receiver=user)
        ).select_related('caller', 'receiver', 'group').order_by('-started_at')[:50]
        
        calls_list = []
        for call in calls:
            calls_list.append({
                'id': call.id,
                'call_type': call.call_type,
                'status': call.status,
                'caller': call.caller.username,
                'receiver': call.receiver.username if call.receiver else None,
                'group': {
                    'id': call.group.id,
                    'name': call.group.name
                } if call.group else None,
                'duration': call.duration,
                'started_at': call.started_at.isoformat(),
                'ended_at': call.ended_at.isoformat() if call.ended_at else None,
                'is_incoming': call.receiver == user if call.receiver else False
            })
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/call-history/', 200, response_time)
        
        return Response({
            'success': True,
            'calls': calls_list,
            'count': len(calls_list)
        })
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# ============= STATUS ENDPOINTS =============

@api_view(['POST'])
@permission_classes([AllowAny])
def create_status(request):
    """Create a new status update"""
    start_time = time.time()
    username = request.data.get('username')
    status_type = request.data.get('status_type', 'text')
    content = request.data.get('content')
    media_url = request.data.get('media_url')
    background_color = request.data.get('background_color', '#000000')
    privacy = request.data.get('privacy', 'everyone')
    
    if not username:
        return Response({'error': 'Username required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not content and not media_url:
        return Response({'error': 'Either content or media_url required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(username=username)
        
        # Create status
        status_obj = Status.objects.create(
            user=user,
            status_type=status_type,
            content=content,
            media_url=media_url,
            background_color=background_color,
            privacy=privacy
        )
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/create-status/', 201, response_time)
        
        return Response({
            'success': True,
            'status': {
                'id': status_obj.id,
                'status_type': status_obj.status_type,
                'content': status_obj.content,
                'media_url': status_obj.media_url,
                'created_at': status_obj.created_at.isoformat(),
                'expires_at': status_obj.expires_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_statuses(request):
    """Get active statuses from contacts"""
    start_time = time.time()
    username = request.GET.get('username')
    
    if not username:
        return Response({'error': 'Username required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(username=username)
        
        # Get active statuses (not expired)
        now = timezone.now()
        statuses = Status.objects.filter(
            expires_at__gt=now
        ).exclude(user=user).select_related('user__profile').prefetch_related('viewed_by')
        
        # Group by user
        statuses_by_user = {}
        for status_obj in statuses:
            user_key = status_obj.user.username
            if user_key not in statuses_by_user:
                statuses_by_user[user_key] = {
                    'user': {
                        'username': status_obj.user.username,
                        'avatar': status_obj.user.profile.avatar if hasattr(status_obj.user, 'profile') else None
                    },
                    'statuses': []
                }
            
            # Check if current user has viewed
            has_viewed = status_obj.viewed_by.filter(id=user.id).exists()
            
            statuses_by_user[user_key]['statuses'].append({
                'id': status_obj.id,
                'status_type': status_obj.status_type,
                'content': status_obj.content,
                'media_url': status_obj.media_url,
                'background_color': status_obj.background_color,
                'created_at': status_obj.created_at.isoformat(),
                'expires_at': status_obj.expires_at.isoformat(),
                'has_viewed': has_viewed,
                'view_count': status_obj.viewed_by.count()
            })
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/statuses/', 200, response_time)
        
        return Response({
            'success': True,
            'statuses': list(statuses_by_user.values()),
            'count': len(statuses_by_user)
        })
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def view_status(request):
    """Mark status as viewed"""
    start_time = time.time()
    status_id = request.data.get('status_id')
    username = request.data.get('username')
    
    if not status_id or not username:
        return Response({'error': 'status_id and username required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(username=username)
        status_obj = Status.objects.get(id=status_id)
        
        # Create view record
        StatusView.objects.get_or_create(status=status_obj, user=user)
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/view-status/', 200, response_time)
        
        return Response({
            'success': True,
            'view_count': status_obj.viewed_by.count()
        })
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Status.DoesNotExist:
        return Response({'error': 'Status not found'}, status=status.HTTP_404_NOT_FOUND)

# ============= CONTACT ENDPOINTS =============

@api_view(['POST'])
@permission_classes([AllowAny])
def add_contact(request):
    """Add a user to contacts"""
    start_time = time.time()
    username = request.data.get('username')
    contact_username = request.data.get('contact')
    nickname = request.data.get('nickname', '')
    
    if not username or not contact_username:
        return Response({'error': 'username and contact required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(username=username)
        contact = User.objects.get(username=contact_username)
        
        # Create contact
        contact_obj, created = Contact.objects.get_or_create(
            user=user,
            contact=contact,
            defaults={'nickname': nickname}
        )
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/add-contact/', 201 if created else 200, response_time)
        
        return Response({
            'success': True,
            'message': 'Contact added' if created else 'Contact already exists',
            'contact': {
                'username': contact.username,
                'nickname': contact_obj.nickname
            }
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_contacts(request):
    """Get user's contacts"""
    start_time = time.time()
    username = request.GET.get('username')
    
    if not username:
        return Response({'error': 'Username required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(username=username)
        
        # Get all contacts
        contacts = Contact.objects.filter(user=user).select_related('contact__profile')
        
        contacts_list = []
        for contact_obj in contacts:
            contact_user = contact_obj.contact
            profile = getattr(contact_user, 'profile', None)
            
            contacts_list.append({
                'username': contact_user.username,
                'nickname': contact_obj.nickname,
                'email': contact_user.email,
                'avatar': profile.avatar if profile else None,
                'status': profile.status if profile else '',
                'is_online': profile.is_online if profile else False,
                'is_blocked': contact_obj.is_blocked,
                'is_favorite': contact_obj.is_favorite,
                'added_at': contact_obj.added_at.isoformat()
            })
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/contacts/', 200, response_time)
        
        return Response({
            'success': True,
            'contacts': contacts_list,
            'count': len(contacts_list)
        })
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# ============= ADMIN ENDPOINTS =============

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_admin(request):
    """Verify if user is admin (in Admin group)"""
    start_time = time.time()
    username = request.data.get('username')
    
    if not username:
        return Response({'is_admin': False, 'error': 'Username required'})
    
    try:
        user = User.objects.get(username=username)
        is_admin = is_user_admin(user)
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/verify-admin/', 200, response_time)
        
        return Response({
            'is_admin': is_admin,
            'is_admin_group': is_admin,
            'username': username,
            'groups': list(user.groups.values_list('name', flat=True))
        })
    except User.DoesNotExist:
        return Response({'is_admin': False, 'error': 'User not found'})

@api_view(['POST'])
@permission_classes([AllowAny])
def make_admin(request):
    """Add user to Admin group"""
    start_time = time.time()
    admin_username = request.data.get('admin_username')
    target_username = request.data.get('target_username')
    admin_password = request.data.get('admin_password')
    
    if not all([admin_username, target_username, admin_password]):
        return Response(
            {'error': 'admin_username, target_username, and admin_password required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Authenticate admin
    admin_user = authenticate(username=admin_username, password=admin_password)
    
    if not admin_user or not is_user_admin(admin_user):
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/make-admin/', 403, response_time)
        return Response(
            {'error': 'Only users in Admin group can make other users admin'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        target_user = User.objects.get(username=target_username)
        
        # Get or create Admin group
        admin_group, created = DjangoGroup.objects.get_or_create(name='Admin')
        
        # Add user to Admin group
        target_user.groups.add(admin_group)
        target_user.save()
        
        # Update profile
        profile, _ = UserProfile.objects.get_or_create(user=target_user)
        profile.role = 'admin'
        profile.save()
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/make-admin/', 200, response_time)
        
        return Response({
            'success': True,
            'message': f'{target_username} is now an admin',
            'username': target_username,
            'is_admin_group': True
        })
        
    except User.DoesNotExist:
        return Response(
            {'error': 'Target user not found'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def remove_admin(request):
    """Remove user from Admin group"""
    start_time = time.time()
    admin_username = request.data.get('admin_username')
    target_username = request.data.get('target_username')
    admin_password = request.data.get('admin_password')
    
    if not all([admin_username, target_username, admin_password]):
        return Response(
            {'error': 'admin_username, target_username, and admin_password required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Authenticate admin
    admin_user = authenticate(username=admin_username, password=admin_password)
    
    if not admin_user or not is_user_admin(admin_user):
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/remove-admin/', 403, response_time)
        return Response(
            {'error': 'Only users in Admin group can remove admin access'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        target_user = User.objects.get(username=target_username)
        
        # Get Admin group
        admin_group = DjangoGroup.objects.get(name='Admin')
        
        # Remove user from Admin group
        target_user.groups.remove(admin_group)
        target_user.save()
        
        # Update profile
        profile, _ = UserProfile.objects.get_or_create(user=target_user)
        profile.role = 'user'
        profile.save()
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/remove-admin/', 200, response_time)
        
        return Response({
            'success': True,
            'message': f'{target_username} is no longer an admin',
            'username': target_username,
            'is_admin_group': False
        })
        
    except User.DoesNotExist:
        return Response(
            {'error': 'Target user not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except DjangoGroup.DoesNotExist:
        return Response(
            {'error': 'Admin group does not exist'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def admin_stats(request):
    """Get real admin dashboard statistics from database"""
    start_time = time.time()
    
    try:
        # Get today's date
        today = timezone.now().date()
        
        # Total users
        total_users = User.objects.count()
        
        # Active sessions (users active in last 24 hours)
        yesterday = timezone.now() - timedelta(days=1)
        active_sessions = UserProfile.objects.filter(
            last_activity__gte=yesterday,
            is_active_session=True
        ).count()
        
        # API calls today
        api_calls_today = APILog.objects.filter(
            created_at__date=today
        ).count()
        
        # Total messages
        total_messages = Message.objects.count()
        
        # Total groups
        total_groups = Group.objects.count()
        
        # Total calls
        total_calls = Call.objects.count()
        
        # Total statuses
        total_statuses = Status.objects.filter(expires_at__gt=timezone.now()).count()
        
        # Revenue (mock calculation based on messages)
        revenue = total_messages * 0.002  # $0.002 per message
        
        # User growth (last 6 days)
        user_growth = []
        for i in range(6, 0, -1):
            date = today - timedelta(days=i)
            count = User.objects.filter(date_joined__date=date).count()
            user_growth.append(count)
        
        # API usage (last 6 hours)
        api_usage = []
        for i in range(6, 0, -1):
            hour_ago = timezone.now() - timedelta(hours=i)
            count = APILog.objects.filter(
                created_at__gte=hour_ago,
                created_at__lt=hour_ago + timedelta(hours=1)
            ).count()
            api_usage.append(count)
        
        # Recent users
        recent_users = []
        for user in User.objects.select_related('profile').order_by('-date_joined')[:10]:
            profile = getattr(user, 'profile', None)
            is_admin = is_user_admin(user)
            recent_users.append({
                'id': user.id,
                'name': user.get_full_name() or user.username,
                'email': user.email,
                'username': user.username,
                'status': 'Active' if (profile and profile.is_active_session) else 'Inactive',
                'joined': user.date_joined.strftime('%Y-%m-%d'),
                'total_messages': profile.total_messages if profile else 0,
                'is_admin': is_admin
            })
        
        # Recent API logs
        recent_logs = []
        for log in APILog.objects.select_related('user').order_by('-created_at')[:20]:
            recent_logs.append({
                'id': log.id,
                'endpoint': log.endpoint,
                'method': log.method,
                'status': log.status_code,
                'time': f"{log.response_time:.0f}ms",
                'user': log.user.username if log.user else 'Anonymous',
                'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'ip_address': log.ip_address
            })
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/admin/stats/', 200, response_time)
        
        return Response({
            'total_users': total_users,
            'api_calls_today': api_calls_today,
            'active_sessions': active_sessions,
            'total_messages': total_messages,
            'total_groups': total_groups,
            'total_calls': total_calls,
            'total_statuses': total_statuses,
            'revenue': round(revenue, 2),
            'user_growth': user_growth,
            'api_usage': api_usage,
            'recent_users': recent_users,
            'recent_logs': recent_logs
        })
        
    except Exception as e:
        print(f"Error getting admin stats: {e}")
        print(traceback.format_exc())
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/admin/stats/', 500, response_time)
        
        return Response({
            'total_users': 0,
            'api_calls_today': 0,
            'active_sessions': 0,
            'total_messages': 0,
            'total_groups': 0,
            'total_calls': 0,
            'total_statuses': 0,
            'revenue': 0,
            'user_growth': [0, 0, 0, 0, 0, 0],
            'api_usage': [0, 0, 0, 0, 0, 0],
            'recent_users': [],
            'recent_logs': [],
            'error': str(e)
        })

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    start_time = time.time()
    
    # Check database
    db_connected = False
    try:
        User.objects.count()
        db_connected = True
    except Exception as e:
        print(f"Database error: {e}")
    
    # Check Admin group
    admin_group_exists = DjangoGroup.objects.filter(name='Admin').exists()
    
    response_time = (time.time() - start_time) * 1000
    log_api_request(request, '/api/health/', 200, response_time)
    
    return Response({
        'status': 'healthy',
        'service': 'White Beat Backend - Full Featured Chat',
        'database_connected': db_connected,
        'admin_group_exists': admin_group_exists,
        'features': {
            'user_to_user_chat': True,
            'group_chat': True,
            'voice_calls': True,
            'video_calls': True,
            'status_updates': True,
            'media_messages': True,
            'message_reactions': True,
            'contacts': True,
            'group_based_admin': True,
            'signup': True
        },
        'stats': {
            'total_users': User.objects.count() if db_connected else 0,
            'total_messages': Message.objects.count() if db_connected else 0,
            'total_conversations': Conversation.objects.count() if db_connected else 0,
            'total_groups': Group.objects.count() if db_connected else 0,
            'total_calls': Call.objects.count() if db_connected else 0,
            'active_statuses': Status.objects.filter(expires_at__gt=timezone.now()).count() if db_connected else 0,
            'admin_users': User.objects.filter(groups__name='Admin').count() if db_connected else 0
        }
    })
