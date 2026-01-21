"""
Dashboard-specific views for User Dashboard
Handles API logs, system stats, conversations, and analytics
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
import json

from .models import (
    UserProfile, APILog, SystemStats, Conversation, 
    Message, MessageReaction, StatusView, Call, Status, Group, Contact
)


@csrf_exempt
def get_api_logs(request):
    """Get API logs for admin dashboard"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        username = request.GET.get('username')
        if not username:
            return JsonResponse({'error': 'Username required'}, status=400)
        
        # Verify user is admin
        user = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
        
        if profile.role != 'admin':
            return JsonResponse({'error': 'Admin access required'}, status=403)
        
        # Get recent API logs
        limit = int(request.GET.get('limit', 50))
        logs = APILog.objects.all().order_by('-created_at')[:limit]
        
        logs_data = [{
            'id': log.id,
            'endpoint': log.endpoint,
            'method': log.method,
            'user': log.user.username if log.user else 'Anonymous',
            'status_code': log.status_code,
            'response_time': log.response_time,
            'ip_address': log.ip_address,
            'created_at': log.created_at.isoformat()
        } for log in logs]
        
        return JsonResponse({
            'success': True,
            'logs': logs_data,
            'total': APILog.objects.count()
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_system_stats(request):
    """Get system statistics for admin dashboard"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        username = request.GET.get('username')
        if not username:
            return JsonResponse({'error': 'Username required'}, status=400)
        
        # Verify user is admin
        user = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
        
        if profile.role != 'admin':
            return JsonResponse({'error': 'Admin access required'}, status=403)
        
        # Get recent system stats
        days = int(request.GET.get('days', 30))
        stats = SystemStats.objects.all().order_by('-date')[:days]
        
        stats_data = [{
            'date': stat.date.isoformat(),
            'total_users': stat.total_users,
            'active_users': stat.active_users,
            'total_messages': stat.total_messages,
            'total_groups': stat.total_groups,
            'total_calls': stat.total_calls,
            'total_statuses': stat.total_statuses,
            'total_api_calls': stat.total_api_calls,
            'revenue': float(stat.revenue)
        } for stat in stats]
        
        # Calculate current stats
        current_stats = {
            'total_users': User.objects.count(),
            'active_users': UserProfile.objects.filter(is_online=True).count(),
            'total_messages': Message.objects.count(),
            'total_groups': Group.objects.count(),
            'total_calls': Call.objects.count(),
            'total_statuses': Status.objects.filter(expires_at__gt=timezone.now()).count(),
            'total_api_calls': APILog.objects.count(),
            'total_conversations': Conversation.objects.count(),
            'total_reactions': MessageReaction.objects.count()
        }
        
        return JsonResponse({
            'success': True,
            'stats': stats_data,
            'current': current_stats
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_message_reactions(request):
    """Get message reactions for a user"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        username = request.GET.get('username')
        if not username:
            return JsonResponse({'error': 'Username required'}, status=400)
        
        user = User.objects.get(username=username)
        
        # Get reactions on user's messages
        user_messages = Message.objects.filter(sender=user)
        reactions = MessageReaction.objects.filter(message__in=user_messages)
        
        reactions_data = [{
            'id': reaction.id,
            'message_id': reaction.message.id,
            'message_content': reaction.message.content[:50] if reaction.message.content else '',
            'user': reaction.user.username,
            'reaction_type': reaction.reaction_type,
            'reaction_emoji': reaction.get_reaction_type_display(),
            'created_at': reaction.created_at.isoformat()
        } for reaction in reactions]
        
        # Group by reaction type
        reaction_counts = reactions.values('reaction_type').annotate(count=Count('id'))
        
        return JsonResponse({
            'success': True,
            'reactions': reactions_data,
            'total': reactions.count(),
            'counts': list(reaction_counts)
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_status_views(request):
    """Get status views for a user"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        username = request.GET.get('username')
        if not username:
            return JsonResponse({'error': 'Username required'}, status=400)
        
        user = User.objects.get(username=username)
        
        # Get views on user's statuses
        user_statuses = Status.objects.filter(user=user)
        views = StatusView.objects.filter(status__in=user_statuses)
        
        views_data = [{
            'id': view.id,
            'status_id': view.status.id,
            'status_type': view.status.status_type,
            'viewer': view.user.username,
            'viewer_name': view.user.get_full_name() or view.user.username,
            'viewed_at': view.viewed_at.isoformat()
        } for view in views]
        
        # Group by status
        status_view_counts = views.values('status__id').annotate(count=Count('id'))
        
        return JsonResponse({
            'success': True,
            'views': views_data,
            'total': views.count(),
            'status_counts': list(status_view_counts)
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_user_analytics(request):
    """Get comprehensive analytics for a user"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        username = request.GET.get('username')
        if not username:
            return JsonResponse({'error': 'Username required'}, status=400)
        
        user = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
        
        # Calculate various metrics
        analytics = {
            # Basic stats
            'total_contacts': Contact.objects.filter(user=user).count(),
            'total_groups': Group.objects.filter(members=user).count(),
            'total_conversations': Conversation.objects.filter(
                Q(user1=user) | Q(user2=user)
            ).count(),
            
            # Messaging stats
            'messages_sent': Message.objects.filter(sender=user).count(),
            'messages_received': Message.objects.filter(receiver=user).count(),
            'total_reactions_given': MessageReaction.objects.filter(user=user).count(),
            'total_reactions_received': MessageReaction.objects.filter(
                message__sender=user
            ).count(),
            
            # Call stats
            'calls_made': Call.objects.filter(caller=user).count(),
            'calls_received': Call.objects.filter(receiver=user).count(),
            'total_call_duration': Call.objects.filter(
                Q(caller=user) | Q(receiver=user),
                status='completed'
            ).aggregate(total=Sum('duration'))['total'] or 0,
            
            # Status stats
            'statuses_posted': Status.objects.filter(user=user).count(),
            'status_views_received': StatusView.objects.filter(
                status__user=user
            ).count(),
            'statuses_viewed': StatusView.objects.filter(user=user).count(),
            
            # Activity stats
            'is_online': profile.is_online,
            'last_seen': profile.last_seen.isoformat() if profile.last_seen else None,
            'joined_date': profile.joined_date.isoformat(),
            'total_messages': profile.total_messages,
            
            # Recent activity
            'messages_today': Message.objects.filter(
                sender=user,
                created_at__gte=timezone.now() - timedelta(days=1)
            ).count(),
            'calls_today': Call.objects.filter(
                caller=user,
                started_at__gte=timezone.now() - timedelta(days=1)
            ).count(),
            'statuses_today': Status.objects.filter(
                user=user,
                created_at__gte=timezone.now() - timedelta(days=1)
            ).count()
        }
        
        return JsonResponse({
            'success': True,
            'analytics': analytics
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_conversation_details(request):
    """Get detailed conversation information"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        username = request.GET.get('username')
        conversation_id = request.GET.get('conversation_id')
        
        if not username or not conversation_id:
            return JsonResponse({'error': 'Username and conversation_id required'}, status=400)
        
        user = User.objects.get(username=username)
        conversation = Conversation.objects.get(id=conversation_id)
        
        # Verify user is part of conversation
        if conversation.user1 != user and conversation.user2 != user:
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        other_user = conversation.get_other_user(user)
        other_profile = UserProfile.objects.get(user=other_user)
        
        # Get conversation stats
        total_messages = Message.objects.filter(conversation=conversation).count()
        unread_messages = Message.objects.filter(
            conversation=conversation,
            receiver=user,
            is_read=False
        ).count()
        
        # Get last message
        last_message = Message.objects.filter(
            conversation=conversation
        ).order_by('-created_at').first()
        
        conversation_data = {
            'id': conversation.id,
            'other_user': other_user.username,
            'other_user_name': other_user.get_full_name() or other_user.username,
            'other_user_avatar': other_profile.avatar,
            'is_online': other_profile.is_online,
            'last_seen': other_profile.last_seen.isoformat() if other_profile.last_seen else None,
            'total_messages': total_messages,
            'unread_count': unread_messages,
            'last_message': last_message.content if last_message else None,
            'last_message_time': last_message.created_at.isoformat() if last_message else None,
            'is_archived': conversation.is_archived_by_user1 if conversation.user1 == user else conversation.is_archived_by_user2,
            'is_muted': conversation.is_muted_by_user1 if conversation.user1 == user else conversation.is_muted_by_user2,
            'created_at': conversation.created_at.isoformat(),
            'updated_at': conversation.updated_at.isoformat()
        }
        
        return JsonResponse({
            'success': True,
            'conversation': conversation_data
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def update_system_stats(request):
    """Update daily system statistics (admin only)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        username = data.get('username')
        
        if not username:
            return JsonResponse({'error': 'Username required'}, status=400)
        
        # Verify user is admin
        user = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
        
        if profile.role != 'admin':
            return JsonResponse({'error': 'Admin access required'}, status=403)
        
        # Get or create today's stats
        today = timezone.now().date()
        stats, created = SystemStats.objects.get_or_create(date=today)
        
        # Update stats
        stats.total_users = User.objects.count()
        stats.active_users = UserProfile.objects.filter(is_online=True).count()
        stats.total_messages = Message.objects.count()
        stats.total_groups = Group.objects.count()
        stats.total_calls = Call.objects.count()
        stats.total_statuses = Status.objects.filter(expires_at__gt=timezone.now()).count()
        stats.total_api_calls = APILog.objects.count()
        stats.save()
        
        return JsonResponse({
            'success': True,
            'message': 'System stats updated successfully',
            'stats': {
                'date': stats.date.isoformat(),
                'total_users': stats.total_users,
                'active_users': stats.active_users,
                'total_messages': stats.total_messages,
                'total_groups': stats.total_groups,
                'total_calls': stats.total_calls,
                'total_statuses': stats.total_statuses,
                'total_api_calls': stats.total_api_calls
            }
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
