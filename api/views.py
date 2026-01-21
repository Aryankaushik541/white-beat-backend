from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
from django.conf import settings
import random

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

# Demo responses for testing without OpenAI
DEMO_RESPONSES = [
    "Hello! I'm a demo AI assistant. To enable real AI responses, please add your OpenAI API key to the .env file.",
    "That's an interesting question! This is a simulated response. For actual AI-powered answers, configure your OpenAI API key.",
    "I understand what you're asking. Currently running in demo mode. Add OPENAI_API_KEY to unlock full AI capabilities!",
    "Great question! I'm here to help. Note: This is a demo response. Real AI responses require OpenAI API configuration.",
    "Thanks for your message! I'm operating in demo mode right now. Set up your OpenAI API key for intelligent responses."
]

@api_view(['POST'])
def login(request):
    """
    Handle user/admin login
    Admin credentials: username='admin', password='admin123'
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Admin check
    if username == 'admin' and password == 'admin123':
        return Response({
            'role': 'admin',
            'username': username,
            'message': 'Admin login successful'
        })
    
    # Regular user login (accept any credentials for demo)
    return Response({
        'role': 'user',
        'username': username,
        'message': 'User login successful'
    })


@api_view(['POST'])
def chat(request):
    """
    Handle AI chat requests using OpenAI API
    Falls back to demo responses if API key not configured
    """
    prompt = request.data.get('prompt')
    
    if not prompt:
        return Response(
            {'error': 'Prompt is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if OpenAI is configured
    if not client:
        # Return intelligent demo response
        demo_response = random.choice(DEMO_RESPONSES)
        return Response({
            'response': f"{demo_response}\n\nYour message was: \"{prompt}\"",
            'model': 'demo-mode',
            'demo': True
        })
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant for White Beat platform."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return Response({
            'response': response.choices[0].message.content,
            'model': 'gpt-3.5-turbo',
            'demo': False
        })
        
    except Exception as e:
        return Response(
            {'error': f'OpenAI API error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def admin_stats(request):
    """
    Get admin dashboard statistics
    """
    return Response({
        'total_users': 1234,
        'api_calls_today': 45678,
        'active_sessions': 89,
        'revenue': 12345,
        'user_growth': [60, 75, 85, 70, 90, 95],
        'api_usage': [80, 65, 90, 75, 85, 70]
    })


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint
    """
    return Response({
        'status': 'healthy',
        'service': 'White Beat Backend',
        'openai_configured': bool(client),
        'mode': 'production' if client else 'demo'
    })