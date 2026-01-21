from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from django.db.models import Count, Sum, Q, Max
from django.utils import timezone
from datetime import timedelta
import traceback
import time

from .models import UserProfile, Conversation, Message, APILog, SystemStats

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

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """
    User signup - creates regular user account
    Users in 'Admin' group go to admin dashboard
    Regular users go to user dashboard
    """
    start_time = time.time()
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', f'{username}@whitebeat.com')
    
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
        # Create new regular user (NOT in Admin group)
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
            is_active_session=True
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
    """
    Handle user/admin login with Django authentication
    - Users in 'Admin' group → Admin Dashboard
    - Regular users → User Dashboard
    """
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
        
        if is_admin:
            # Admin user (in Admin group)
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': 'admin'}
            )
            profile.role = 'admin'
            profile.is_active_session = True
            profile.save()
            
            response_time = (time.time() - start_time) * 1000
            log_api_request(request, '/api/login/', 200, response_time)
            
            return Response({
                'role': 'admin',
                'username': username,
                'email': user.email,
                'message': 'Admin login successful',
                'user_id': user.id,
                'is_staff': user.is_staff,
                'is_admin_group': True,
                'groups': list(user.groups.values_list('name', flat=True))
            })
        else:
            # Regular user (not in Admin group)
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': 'user'}
            )
            profile.role = 'user'
            profile.is_active_session = True
            profile.save()
            
            response_time = (time.time() - start_time) * 1000
            log_api_request(request, '/api/login/', 200, response_time)
            
            return Response({
                'role': 'user',
                'username': username,
                'email': user.email,
                'message': 'User login successful',
                'user_id': user.id,
                'is_admin_group': False,
                'groups': list(user.groups.values_list('name', flat=True))
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
def verify_admin(request):
    """
    Verify if user is admin (in Admin group)
    Used by frontend to check admin access
    """
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
    """
    Add user to Admin group
    Only users already in Admin group can do this
    """
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
        admin_group, created = Group.objects.get_or_create(name='Admin')
        
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
            'is_admin_group': True,
            'groups': list(target_user.groups.values_list('name', flat=True))
        })
        
    except User.DoesNotExist:
        return Response(
            {'error': 'Target user not found'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def remove_admin(request):
    """
    Remove user from Admin group
    Only users in Admin group can do this
    """
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
        admin_group = Group.objects.get(name='Admin')
        
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
            'is_admin_group': False,
            'groups': list(target_user.groups.values_list('name', flat=True))
        })
        
    except User.DoesNotExist:
        return Response(
            {'error': 'Target user not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Group.DoesNotExist:
        return Response(
            {'error': 'Admin group does not exist'},
            status=status.HTTP_404_NOT_FOUND
        )

# ============= USER-TO-USER MESSAGING ENDPOINTS =============

@api_view(['GET'])
@permission_classes([AllowAny])
def get_users(request):
    """Get list of all users for chat"""
    start_time = time.time()
    current_username = request.GET.get('username')
    
    if not current_username:
        return Response({'error': 'Username required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        current_user = User.objects.get(username=current_username)
        
        # Get all users except current user
        users = User.objects.exclude(id=current_user.id).select_related('profile')
        
        users_list = []
        for user in users:
            profile = getattr(user, 'profile', None)
            users_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'status': profile.status if profile else 'Hey there! I am using White Beat',
                'is_online': profile.is_active_session if profile else False,
                'last_activity': profile.last_activity.isoformat() if profile else None
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
        ).select_related('user1', 'user2').prefetch_related('messages')
        
        conversations_list = []
        for conv in conversations:
            other_user = conv.get_other_user(user)
            other_profile = getattr(other_user, 'profile', None)
            
            # Get last message
            last_message = conv.messages.last()
            
            # Count unread messages
            unread_count = conv.messages.filter(
                receiver=user,
                is_read=False
            ).count()
            
            conversations_list.append({
                'id': conv.id,
                'other_user': {
                    'id': other_user.id,
                    'username': other_user.username,
                    'email': other_user.email,
                    'status': other_profile.status if other_profile else '',
                    'is_online': other_profile.is_active_session if other_profile else False
                },
                'last_message': {
                    'content': last_message.content if last_message else '',
                    'created_at': last_message.created_at.isoformat() if last_message else None,
                    'sender': last_message.sender.username if last_message else None
                } if last_message else None,
                'unread_count': unread_count,
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
        
        # Get all messages
        messages = conversation.messages.select_related('sender', 'receiver')
        
        messages_list = []
        for msg in messages:
            messages_list.append({
                'id': msg.id,
                'sender': msg.sender.username,
                'receiver': msg.receiver.username,
                'content': msg.content,
                'is_read': msg.is_read,
                'created_at': msg.created_at.isoformat(),
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
            'count': len(messages_list)
        })
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_message(request):
    """Send a message to another user"""
    start_time = time.time()
    sender_username = request.data.get('sender')
    receiver_username = request.data.get('receiver')
    content = request.data.get('content')
    
    if not all([sender_username, receiver_username, content]):
        return Response(
            {'error': 'sender, receiver, and content are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        sender = User.objects.get(username=sender_username)
        receiver = User.objects.get(username=receiver_username)
        
        # Get or create conversation
        conversation = get_or_create_conversation(sender, receiver)
        
        # Create message
        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            receiver=receiver,
            content=content
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
                'content': message.content,
                'created_at': message.created_at.isoformat(),
                'is_read': message.is_read
            }
        }, status=status.HTTP_201_CREATED)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

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

# ============= ADMIN ENDPOINTS =============

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
                'is_admin': is_admin,
                'groups': list(user.groups.values_list('name', flat=True))
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
    admin_group_exists = Group.objects.filter(name='Admin').exists()
    
    response_time = (time.time() - start_time) * 1000
    log_api_request(request, '/api/health/', 200, response_time)
    
    return Response({
        'status': 'healthy',
        'service': 'White Beat Backend - User Chat',
        'database_connected': db_connected,
        'admin_group_exists': admin_group_exists,
        'features': {
            'user_to_user_chat': True,
            'group_based_admin': True,
            'signup': True
        },
        'stats': {
            'total_users': User.objects.count() if db_connected else 0,
            'total_messages': Message.objects.count() if db_connected else 0,
            'total_conversations': Conversation.objects.count() if db_connected else 0,
            'admin_users': User.objects.filter(groups__name='Admin').count() if db_connected else 0
        }
    })
