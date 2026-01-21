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

# Import local AI and OSINT engines
try:
    from .ai_engine import chat_with_ai, get_ai_engine
    AI_AVAILABLE = True
except Exception as e:
    print(f"⚠️ AI Engine not available: {e}")
    AI_AVAILABLE = False

try:
    from .osint_engine import osint_search, get_osint_engine
    OSINT_AVAILABLE = True
except Exception as e:
    print(f"⚠️ OSINT Engine not available: {e}")
    OSINT_AVAILABLE = False

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
def signup(request):
    """
    User signup - creates regular user account
    Superusers created via Django command go to admin
    Regular signups go to user dashboard
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
        # Create new regular user (NOT admin)
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            is_staff=False,  # Regular user
            is_superuser=False  # Regular user
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
    - Superusers (created via createsuperuser) → Admin Dashboard
    - Regular users (created via signup) → User Dashboard
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
        # Check if user is superuser (created via createsuperuser)
        if user.is_superuser:
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
                'email': user.email,
                'message': 'Admin login successful',
                'user_id': user.id,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            })
        else:
            # Regular user (created via signup)
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
                'email': user.email,
                'message': 'User login successful',
                'user_id': user.id
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
    Verify if user is admin (superuser only)
    Used by frontend to check admin access
    """
    start_time = time.time()
    username = request.data.get('username')
    
    if not username:
        return Response({'is_admin': False, 'error': 'Username required'})
    
    try:
        user = User.objects.get(username=username)
        is_admin = user.is_superuser  # Only superusers are admins
        
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
def make_admin(request):
    """
    Make a user admin (superuser)
    Only existing superusers can do this
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
    
    if not admin_user or not admin_user.is_superuser:
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/make-admin/', 403, response_time)
        return Response(
            {'error': 'Only superusers can make other users admin'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        target_user = User.objects.get(username=target_username)
        target_user.is_staff = True
        target_user.is_superuser = True
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
            'is_staff': True,
            'is_superuser': True
        })
        
    except User.DoesNotExist:
        return Response(
            {'error': 'Target user not found'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def chat(request):
    """Handle AI chat with local AI engine"""
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
    
    # Check if AI engine is available
    if not AI_AVAILABLE:
        demo_response = "Local AI engine not initialized. Please install required packages: pip install transformers torch"
        
        ChatMessage.objects.create(
            user=user,
            prompt=prompt,
            response=demo_response,
            model_used='unavailable',
            tokens_used=0,
            response_time=(time.time() - start_time)
        )
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/chat/', 200, response_time)
        
        return Response({
            'response': demo_response,
            'model': 'unavailable',
            'demo': True
        })
    
    try:
        print(f"🔄 Processing chat with local AI: {prompt[:50]}...")
        
        # Get AI response
        ai_response = chat_with_ai(prompt)
        
        # Get model info
        engine = get_ai_engine()
        model_name = getattr(engine, 'model_name', 'local-ai')
        
        # Log message
        ChatMessage.objects.create(
            user=user,
            prompt=prompt,
            response=ai_response,
            model_used=model_name,
            tokens_used=len(prompt.split()) + len(ai_response.split()),  # Approximate
            response_time=(time.time() - start_time)
        )
        
        # Update user profile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.total_messages += 1
        profile.save()
        
        print(f"✅ Local AI response generated")
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/chat/', 200, response_time)
        
        return Response({
            'response': ai_response,
            'model': model_name,
            'demo': False,
            'engine': 'local-ai'
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ AI Error: {error_msg}")
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/chat/', 500, response_time)
        
        return Response({
            'response': f"Error: {error_msg}",
            'error': error_msg,
            'model': 'error-mode'
        })

@api_view(['POST'])
@permission_classes([AllowAny])
def osint_lookup(request):
    """OSINT intelligence gathering endpoint"""
    start_time = time.time()
    query = request.data.get('query')
    search_type = request.data.get('type', 'auto')
    
    if not query:
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/osint/', 400, response_time)
        return Response({'error': 'Query is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not OSINT_AVAILABLE:
        return Response({
            'error': 'OSINT engine not available',
            'message': 'Please install required packages: pip install requests beautifulsoup4 dnspython'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    try:
        print(f"🔍 OSINT lookup: {query} (type: {search_type})")
        
        # Perform OSINT search
        results = osint_search(query, search_type)
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/osint/', 200, response_time)
        
        return Response({
            'success': True,
            'query': query,
            'type': search_type,
            'results': results,
            'response_time': f"{response_time:.0f}ms"
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ OSINT Error: {error_msg}")
        
        response_time = (time.time() - start_time) * 1000
        log_api_request(request, '/api/osint/', 500, response_time)
        
        return Response({
            'error': error_msg,
            'query': query
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    """Health check with all engines status"""
    start_time = time.time()
    
    # Check database
    db_connected = False
    try:
        User.objects.count()
        db_connected = True
    except Exception as e:
        print(f"Database error: {e}")
    
    # Check AI engine
    ai_status = "unavailable"
    if AI_AVAILABLE:
        try:
            engine = get_ai_engine()
            if engine and engine.initialized:
                ai_status = "initialized"
            else:
                ai_status = "not initialized"
        except:
            ai_status = "error"
    
    # Check OSINT engine
    osint_status = "unavailable"
    if OSINT_AVAILABLE:
        try:
            engine = get_osint_engine()
            if engine:
                osint_status = "available"
        except:
            osint_status = "error"
    
    response_time = (time.time() - start_time) * 1000
    log_api_request(request, '/api/health/', 200, response_time)
    
    return Response({
        'status': 'healthy',
        'service': 'White Beat Backend',
        'database_connected': db_connected,
        'ai_engine': ai_status,
        'osint_engine': osint_status,
        'features': {
            'local_ai': AI_AVAILABLE,
            'osint': OSINT_AVAILABLE,
            'admin_control': True,
            'signup': True
        },
        'stats': {
            'total_users': User.objects.count() if db_connected else 0,
            'total_messages': ChatMessage.objects.count() if db_connected else 0
        }
    })
