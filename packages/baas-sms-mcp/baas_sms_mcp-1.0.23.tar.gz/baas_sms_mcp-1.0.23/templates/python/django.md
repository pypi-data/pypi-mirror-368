# BaaS SMS/MMS Django Integration

Django service and management commands for BaaS SMS/MMS services.

## Installation

```bash
pip install requests django
```

## Code

```python
"""
BaaS SMS/MMS Django Integration
Django service, models, and management commands
"""

# services/baas_sms.py
import requests
import logging
from typing import List, Dict, Optional
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

class BaaSMessageService:
    def __init__(self, api_key: str = None, project_id: str = None, base_url: str = None):
        self.api_key = api_key or getattr(settings, 'BAAS_API_KEY', None)
        self.project_id = project_id or getattr(settings, 'BAAS_PROJECT_ID', None)
        self.base_url = base_url or getattr(settings, 'BAAS_BASE_URL', 'https://api.aiapp.link')
        
        if not self.api_key:
            raise ImproperlyConfigured("BAAS_API_KEY must be set in Django settings")
        if not self.project_id:
            raise ImproperlyConfigured("BAAS_PROJECT_ID must be set in Django settings")
    
    def send_sms(self, recipients: List[Dict], message: str, callback_number: str) -> Dict:
        """Send SMS message"""
        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'recipients': recipients,
                'message': message,
                'callback_number': callback_number,
                'project_id': self.project_id,
                'channel_id': 1
            }
            
            response = requests.post(
                f'{self.base_url}/message/sms',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                logger.info(f"SMS sent successfully to {len(recipients)} recipients. Group ID: {result['data']['group_id']}")
                return {
                    'success': True,
                    'group_id': result['data']['group_id'],
                    'message': 'SMS sent successfully'
                }
            else:
                logger.error(f"SMS sending failed: {result.get('message')}")
                return {
                    'success': False,
                    'error': result.get('message', 'Send failed'),
                    'error_code': result.get('error_code')
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while sending SMS: {str(e)}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
    
    def send_mms(self, recipients: List[Dict], message: str, subject: str, 
                callback_number: str, image_urls: Optional[List[str]] = None) -> Dict:
        """Send MMS message with images"""
        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'recipients': recipients,
                'message': message,
                'subject': subject,
                'callback_number': callback_number,
                'project_id': self.project_id,
                'channel_id': 3,
                'img_url_list': image_urls or []
            }
            
            response = requests.post(
                f'{self.base_url}/message/mms',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                logger.info(f"MMS sent successfully to {len(recipients)} recipients. Group ID: {result['data']['group_id']}")
                return {
                    'success': True,
                    'group_id': result['data']['group_id'],
                    'message': 'MMS sent successfully'
                }
            else:
                logger.error(f"MMS sending failed: {result.get('message')}")
                return {
                    'success': False,
                    'error': result.get('message', 'Send failed'),
                    'error_code': result.get('error_code')
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while sending MMS: {str(e)}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
    
    def get_message_status(self, group_id: int) -> Dict:
        """Check message delivery status"""
        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'{self.base_url}/message/send_history/sms/{group_id}/messages',
                headers=headers,
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                messages = result.get('data', [])
                total_count = len(messages)
                success_count = sum(1 for msg in messages if msg.get('result') == '성공')
                failed_count = sum(1 for msg in messages if msg.get('result') == '실패')
                pending_count = total_count - success_count - failed_count
                
                if pending_count > 0:
                    status = '전송중'
                elif failed_count == 0:
                    status = '성공'
                else:
                    status = '실패' if success_count == 0 else '부분성공'
                
                return {
                    'group_id': group_id,
                    'status': status,
                    'total_count': total_count,
                    'success_count': success_count,
                    'failed_count': failed_count,
                    'pending_count': pending_count,
                    'messages': [
                        {
                            'phone': msg.get('phone', ''),
                            'name': msg.get('name', ''),
                            'status': msg.get('result', ''),
                            'reason': msg.get('reason')
                        }
                        for msg in messages
                    ]
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Status check failed')
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
    
    def send_sms_cached(self, recipients: List[Dict], message: str, callback_number: str, 
                       cache_timeout: int = 300) -> Dict:
        """Send SMS with caching for duplicate prevention"""
        cache_key = f"baas_sms_{hash(str(recipients))}{hash(message)}"
        
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"SMS request found in cache: {cache_key}")
            return cached_result
            
        result = self.send_sms(recipients, message, callback_number)
        
        if result.get('success'):
            cache.set(cache_key, result, cache_timeout)
            
        return result

# models.py
from django.db import models
from django.contrib.auth.models import User

class SMSMessage(models.Model):
    STATUS_CHOICES = [
        ('pending', '전송중'),
        ('success', '성공'),
        ('failed', '실패'),
        ('partial', '부분성공'),
    ]
    
    MESSAGE_TYPE_CHOICES = [
        ('sms', 'SMS'),
        ('mms', 'MMS'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sms_messages')
    message_type = models.CharField(max_length=3, choices=MESSAGE_TYPE_CHOICES, default='sms')
    recipients = models.JSONField()  # List of recipients
    message = models.TextField()
    subject = models.CharField(max_length=40, blank=True)  # For MMS
    callback_number = models.CharField(max_length=20)
    group_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    total_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_message_type_display()} to {len(self.recipients)} recipients"
    
    def update_status(self):
        """Update status from BaaS API"""
        if not self.group_id:
            return
            
        service = BaaSMessageService()
        status_result = service.get_message_status(self.group_id)
        
        if status_result.get('success', True):  # API returns status info, not success/failed
            self.status = status_result.get('status', 'pending')
            self.total_count = status_result.get('total_count', 0)
            self.success_count = status_result.get('success_count', 0)
            self.failed_count = status_result.get('failed_count', 0)
            self.save()

# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

@login_required
def send_sms_view(request):
    if request.method == 'POST':
        phone_numbers = request.POST.get('phone_numbers', '').split('\n')
        message = request.POST.get('message', '')
        callback_number = request.POST.get('callback_number', '')
        
        # Validate input
        phone_numbers = [phone.strip() for phone in phone_numbers if phone.strip()]
        if not phone_numbers or not message:
            messages.error(request, '전화번호와 메시지를 입력해주세요.')
            return render(request, 'sms/send.html')
        
        # Prepare recipients
        recipients = [
            {"phone_number": phone, "member_code": f"user_{i}"}
            for i, phone in enumerate(phone_numbers)
        ]
        
        # Send SMS
        service = BaaSMessageService()
        result = service.send_sms(recipients, message, callback_number)
        
        # Save to database
        sms_message = SMSMessage.objects.create(
            user=request.user,
            message_type='sms',
            recipients=recipients,
            message=message,
            callback_number=callback_number,
            group_id=result.get('group_id'),
            status='success' if result.get('success') else 'failed',
            total_count=len(recipients)
        )
        
        if result.get('success'):
            messages.success(request, f'SMS가 성공적으로 전송되었습니다. (Group ID: {result["group_id"]})')
        else:
            messages.error(request, f'SMS 전송에 실패했습니다: {result.get("error")}')
        
        return redirect('sms:history')
    
    return render(request, 'sms/send.html')

@login_required
def sms_history_view(request):
    messages = SMSMessage.objects.filter(user=request.user)
    return render(request, 'sms/history.html', {'messages': messages})

class SMSStatusAPI(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, message_id):
        try:
            sms_message = SMSMessage.objects.get(id=message_id, user=request.user)
            sms_message.update_status()
            
            return JsonResponse({
                'success': True,
                'status': sms_message.status,
                'total_count': sms_message.total_count,
                'success_count': sms_message.success_count,
                'failed_count': sms_message.failed_count
            })
        except SMSMessage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Message not found'})

# management/commands/send_bulk_sms.py
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import csv

class Command(BaseCommand):
    help = 'Send bulk SMS from CSV file'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file with phone numbers')
        parser.add_argument('message', type=str, help='Message to send')
        parser.add_argument('--callback', type=str, default='02-1234-5678', help='Callback number')
        parser.add_argument('--user-id', type=int, required=True, help='User ID for tracking')
    
    def handle(self, *args, **options):
        try:
            user = User.objects.get(id=options['user_id'])
        except User.DoesNotExist:
            raise CommandError(f'User with ID {options["user_id"]} does not exist')
        
        # Read CSV file
        recipients = []
        with open(options['csv_file'], 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                recipients.append({
                    "phone_number": row.get('phone_number', ''),
                    "member_code": row.get('member_code', f'bulk_{i}')
                })
        
        if not recipients:
            raise CommandError('No recipients found in CSV file')
        
        # Send SMS
        service = BaaSMessageService()
        result = service.send_sms(recipients, options['message'], options['callback'])
        
        # Save to database
        sms_message = SMSMessage.objects.create(
            user=user,
            message_type='sms',
            recipients=recipients,
            message=options['message'],
            callback_number=options['callback'],
            group_id=result.get('group_id'),
            status='success' if result.get('success') else 'failed',
            total_count=len(recipients)
        )
        
        if result.get('success'):
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully sent SMS to {len(recipients)} recipients. '
                    f'Group ID: {result["group_id"]}, DB ID: {sms_message.id}'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'Failed to send SMS: {result.get("error")}')
            )

# management/commands/check_sms_status.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Check and update SMS status for pending messages'
    
    def add_arguments(self, parser):
        parser.add_argument('--hours', type=int, default=24, help='Check messages from last N hours')
    
    def handle(self, *args, **options):
        since = timezone.now() - timedelta(hours=options['hours'])
        
        pending_messages = SMSMessage.objects.filter(
            status='pending',
            created_at__gte=since,
            group_id__isnull=False
        )
        
        updated_count = 0
        for message in pending_messages:
            old_status = message.status
            message.update_status()
            
            if message.status != old_status:
                updated_count += 1
                self.stdout.write(f'Updated message {message.id}: {old_status} -> {message.status}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Updated {updated_count} messages out of {pending_messages.count()} checked')
        )
```

## Usage Examples

```python
# Example 1: Using the service directly
from myapp.services.baas_sms import BaaSMessageService

def send_verification_sms(user, phone_number, verification_code):
    service = BaaSMessageService()
    recipients = [
        {"phone_number": phone_number, "member_code": str(user.id)}
    ]
    
    message = f"[MyApp] 인증번호: {verification_code}"
    result = service.send_sms(recipients, message, "02-1234-5678")
    
    # Save to database
    SMSMessage.objects.create(
        user=user,
        message_type='sms',
        recipients=recipients,
        message=message,
        callback_number="02-1234-5678",
        group_id=result.get('group_id'),
        status='success' if result.get('success') else 'failed',
        total_count=1
    )
    
    return result

# Example 2: Django view with form handling
from django.shortcuts import render
from django.contrib import messages as django_messages
from .forms import SMSForm

def send_sms_form_view(request):
    if request.method == 'POST':
        form = SMSForm(request.POST)
        if form.is_valid():
            service = BaaSMessageService()
            
            recipients = [
                {"phone_number": form.cleaned_data['phone_number'], 
                 "member_code": "form_user"}
            ]
            
            result = service.send_sms(
                recipients,
                form.cleaned_data['message'],
                form.cleaned_data['callback_number']
            )
            
            if result.get('success'):
                django_messages.success(request, 'SMS sent successfully!')
            else:
                django_messages.error(request, f'Failed to send SMS: {result.get("error")}')
            
            return redirect('sms_success')
    else:
        form = SMSForm()
    
    return render(request, 'send_sms.html', {'form': form})

# Example 3: Celery task for async SMS sending
from celery import shared_task

@shared_task
def send_sms_async(user_id, recipients, message, callback_number):
    from django.contrib.auth.models import User
    
    try:
        user = User.objects.get(id=user_id)
        service = BaaSMessageService()
        
        result = service.send_sms(recipients, message, callback_number)
        
        # Save to database
        SMSMessage.objects.create(
            user=user,
            message_type='sms',
            recipients=recipients,
            message=message,
            callback_number=callback_number,
            group_id=result.get('group_id'),
            status='success' if result.get('success') else 'failed',
            total_count=len(recipients)
        )
        
        return result
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Example 4: Django admin integration
from django.contrib import admin

@admin.register(SMSMessage)
class SMSMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message_type', 'status', 'total_count', 'success_count', 'created_at']
    list_filter = ['message_type', 'status', 'created_at']
    search_fields = ['user__username', 'message']
    readonly_fields = ['group_id', 'created_at', 'updated_at']
    
    actions = ['update_status']
    
    def update_status(self, request, queryset):
        updated = 0
        for message in queryset:
            if message.group_id:
                message.update_status()
                updated += 1
        
        self.message_user(request, f'{updated} messages updated.')
    
    update_status.short_description = "Update status from API"
```

## Django Settings

```python
# settings.py
BAAS_API_KEY = os.environ.get('BAAS_API_KEY')
BAAS_PROJECT_ID = os.environ.get('BAAS_PROJECT_ID')
BAAS_BASE_URL = 'https://api.aiapp.link'  # Optional, uses default if not set

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'sms.log',
        },
    },
    'loggers': {
        'myapp.services.baas_sms': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Cache configuration (for SMS deduplication)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

## URLs Configuration

```python
# urls.py
from django.urls import path
from . import views

app_name = 'sms'

urlpatterns = [
    path('send/', views.send_sms_view, name='send'),
    path('history/', views.sms_history_view, name='history'),
    path('api/status/<int:message_id>/', views.SMSStatusAPI.as_view(), name='api_status'),
]
```

## Templates

```html
<!-- templates/sms/send.html -->
<form method="post">
    {% csrf_token %}
    <div>
        <label for="phone_numbers">Phone Numbers (one per line):</label>
        <textarea name="phone_numbers" id="phone_numbers" rows="5" required></textarea>
    </div>
    
    <div>
        <label for="message">Message:</label>
        <textarea name="message" id="message" maxlength="2000" required></textarea>
    </div>
    
    <div>
        <label for="callback_number">Callback Number:</label>
        <input type="tel" name="callback_number" id="callback_number" value="02-1234-5678" required>
    </div>
    
    <button type="submit">Send SMS</button>
</form>

<!-- templates/sms/history.html -->
<table>
    <tr>
        <th>ID</th>
        <th>Type</th>
        <th>Recipients</th>
        <th>Message</th>
        <th>Status</th>
        <th>Created</th>
        <th>Actions</th>
    </tr>
    {% for message in messages %}
    <tr>
        <td>{{ message.id }}</td>
        <td>{{ message.get_message_type_display }}</td>
        <td>{{ message.recipients|length }}</td>
        <td>{{ message.message|truncatechars:50 }}</td>
        <td>{{ message.get_status_display }}</td>
        <td>{{ message.created_at }}</td>
        <td>
            {% if message.group_id %}
            <button onclick="checkStatus({{ message.id }})">Check Status</button>
            {% endif %}
        </td>
    </tr>
    {% endfor %}
</table>

<script>
function checkStatus(messageId) {
    fetch(`/sms/api/status/${messageId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`Status: ${data.status}\nSuccess: ${data.success_count}\nFailed: ${data.failed_count}`);
                location.reload();
            } else {
                alert('Failed to check status');
            }
        });
}
</script>
```

## Management Commands

```bash
# Send bulk SMS from CSV
python manage.py send_bulk_sms recipients.csv "Hello from Django!" --callback "02-1234-5678" --user-id 1

# Check status of pending messages
python manage.py check_sms_status --hours 24
```

## Best Practices

1. **Environment Variables**: Store sensitive data in environment variables
2. **Database Tracking**: Save all SMS operations for audit and status tracking
3. **Caching**: Use caching to prevent duplicate SMS sending
4. **Async Processing**: Use Celery for bulk SMS operations
5. **Error Handling**: Implement comprehensive error handling and logging
6. **Rate Limiting**: Implement rate limiting for user-facing SMS endpoints
7. **Admin Interface**: Use Django admin for SMS monitoring and management