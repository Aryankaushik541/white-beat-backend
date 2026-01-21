from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
import random
import traceback
import time

from .models import UserProfile, ChatMessage, APILog, SystemStats

# Demo responses for testing without OpenAI
DEMO_RESPONSES = [
    "Hello! I'm a demo AI assistant. To enable real AI responses, please add your OpenAI API key to the .env file.",
    "That's an interesting question! This is a simulated response. For actual AI-powered answers, configure your OpenAI API key.",
    "I understand what you're asking. Currently running in demo mode. Add OPENAI_API_KEY to unlock full AI capabilities!",
]

# Initialize OpenAI client
client = None
openai_error = None

try:
    from openai import OpenAI
    from django.conf import settings
    
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    
    if api_key and api_key.startswith('sk-'):
        client = OpenAI(api_key=api_key)
        print(f"✅ OpenAI initialized: {api_key[:15]}...")
    else:
        print(f"⚠️ Invalid API key format: {api_key[:15] if api_key else 'None'}")
except Exception as e:
    openai_error = str(e)
    print(f"❌ OpenAI init error: {e}")

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

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Handle user/admin login with Django authentication
    Only Django staff/superuser can access admin dashboard
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
        # Check if user is admin (staff or superuser)
        if user.is_staff or user.is_superuser:
            # Get or create profile
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
                'message': 'Admin login successful',
                'user_id': user.id,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            })
        else:
            # Regular user
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': 'user'}
            )
            profile.is_active_session = True
            profile.save()
            
            response_time = (time.time() - start_time) * 1000
            log_api_request(request, '/api/login/', 200, response_time)
            
            return Response({
                'role': 'user',
                'username': username,
                'message': 'User login successful',
                'user_id': user.id
            })
    else:
        # Invalid credentials - create regular user for demo
        # Check if user exists
        try:
            existing_user = User.objects.get(username=username)
            # User exists but wrong password
            response_time = (time.time() - start_time) * 1000
            log_api_request(request, '/api/login/', 401, response_time)
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except User.DoesNotExist:
            # Create new regular user
            user = User.objects.create_user(
                username=username,
                password=password,
                email=f'{username}@whitebeat.com'
            )
            
            # Create profile
            profile = UserProfile.objects.create(
                user=user,
                role='user',
                is_active_session=True
            )
            
            response_time = (time.time() - start_time) * 1000
            log_api_request(request, '/api/login/', 200, response_time)
            
            return Response({
                'role': 'user',
                'username': username,
                'message': 'User account created and logged in',
                'user_id': user.id
            })

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_admin(request):
    """
    Verify if user is admin (staff/superuser)
    Used by frontend to check admin access
    """
    start_time = time.time()
    username = request.data.get('username')
    
    if not username:
        return Response({'is_admin': False, 'error': 'Username required'})
    
    try:
        user = User.objects.get(username=username)
        is_admin = user.is_staff or user.is_superuser
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/verify-admin/', 200, response_time)
        
        return Response({
            'is_admin': is_admin,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'username': username
        })
    except User.DoesNotExist:
        return Response({'is_admin': False, 'error': 'User not found'})

@api_view(['POST'])
@permission_classes([AllowAny])
def chat(request):
    """Handle AI chat with message logging"""
    start_time = time.time()
    prompt = request.data.get('prompt')
    username = request.data.get('username', 'anonymous')
    
    if not prompt:
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/chat/', 400, response_time)
        return Response({'error': 'Prompt is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get or create user
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={'email': f'{username}@whitebeat.com'}
    )
    
    # If no OpenAI client, return demo response
    if not client:
        demo_response = random.choice(DEMO_RESPONSES)
        response_text = f"{demo_response}\n\nYour message was: \"{prompt}\""
        
        # Log message
        ChatMessage.objects.create(
            user=user,
            prompt=prompt,
            response=response_text,
            model_used='demo-mode',
            tokens_used=0,
            response_time=(time.time() - start_time)
        )
        
        # Update user profile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.total_messages += 1
        profile.save()
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/chat/', 200, response_time)
        
        return Response({
            'response': response_text,
            'model': 'demo-mode',
            'demo': True
        })
    
    try:
        print(f"🔄 Calling OpenAI with: {prompt[:50]}...")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant for White Beat platform."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content
        tokens = response.usage.total_tokens if hasattr(response, 'usage') else 0
        
        # Log message
        ChatMessage.objects.create(
            user=user,
            prompt=prompt,
            response=response_text,
            model_used='gpt-3.5-turbo',
            tokens_used=tokens,
            response_time=(time.time() - start_time)
        )
        
        # Update user profile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.total_messages += 1
        profile.save()
        
        print(f"✅ OpenAI response received")
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/chat/', 200, response_time)
        
        return Response({
            'response': response_text,
            'model': 'gpt-3.5-turbo',
            'demo': False,
            'tokens': tokens
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ OpenAI Error: {error_msg}")
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/chat/', 500, response_time)
        
        return Response({
            'response': f"Error: {error_msg}\n\nYour message: \"{prompt}\"",
            'error': error_msg,
            'model': 'error-mode'
        })

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
        total_messages = ChatMessage.objects.count()
        
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
            recent_users.append({
                'id': user.id,
                'name': user.get_full_name() or user.username,
                'email': user.email,
                'username': user.username,
                'status': 'Active' if (profile and profile.is_active_session) else 'Inactive',
                'joined': user.date_joined.strftime('%Y-%m-%d'),
                'total_messages': profile.total_messages if profile else 0,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
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
        
        # Return mock data if error
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
    """Health check with database connectivity"""
    start_time = time.time()
    
    from django.conf import settings
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    
    # Check database
    db_connected = False
    try:
        User.objects.count()
        db_connected = True
    except Exception as e:
        print(f"Database error: {e}")
    
    response_time = (time.time() - start_time) * 1000
    log_api_request(request, '/api/health/', 200, response_time)
    
    return Response({
        'status': 'healthy',
        'service': 'White Beat Backend',
        'openai_configured': bool(client),
        'database_connected': db_connected,
        'mode': 'production' if client else 'demo',
        'debug': {
            'api_key_exists': bool(api_key),
            'api_key_valid': api_key.startswith('sk-') if api_key else False,
            'api_key_prefix': api_key[:15] if api_key else 'None',
            'client_status': 'initialized' if client else 'not initialized',
            'error': openai_error,
            'total_users': User.objects.count() if db_connected else 0,
            'total_messages': ChatMessage.objects.count() if db_connected else 0
        }
    })