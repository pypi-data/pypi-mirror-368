# BaaS SMS/MMS Python SDK

Direct API integration for BaaS SMS/MMS services without MCP dependency.

## Installation

```bash
pip install requests
```

## Code

```python
"""
BaaS SMS/MMS Direct API Client
Directly calls https://api.aiapp.link without MCP
"""

import requests
import json
from typing import List, Dict, Optional, Union

class BaaSMessageService:
    def __init__(self, api_key: str, base_url: str = 'https://api.aiapp.link'):
        self.api_key = api_key
        self.base_url = base_url
        
    def send_sms(self, recipients: List[Dict], message: str, callback_number: str) -> Dict:
        """
        Send SMS message
        
        Args:
            recipients: List of {phone_number, member_code}
            message: Message content (max 2000 chars)
            callback_number: Sender callback number
            
        Returns:
            Dict: Response object
        """
        try:
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'recipients': recipients,
                'message': message,
                'callback_number': callback_number,
                'channel_id': 1
            }
            
            response = requests.post(
                f'{self.base_url}/api/message/sms',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                return {
                    'success': True,
                    'group_id': result['data']['group_id'],
                    'message': 'SMS sent successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Send failed'),
                    'error_code': result.get('error_code')
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
    
    def send_mms(self, recipients: List[Dict], message: str, subject: str, 
                callback_number: str, image_urls: Optional[List[str]] = None) -> Dict:
        """
        Send MMS message with images
        
        Args:
            recipients: List of {phone_number, member_code}
            message: Message content
            subject: MMS subject (max 40 chars)
            callback_number: Sender callback number
            image_urls: List of image URLs (max 5)
            
        Returns:
            Dict: Response object
        """
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
                'channel_id': 3,
                'img_url_list': image_urls or []
            }
            
            response = requests.post(
                f'{self.base_url}/api/message/mms',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                return {
                    'success': True,
                    'group_id': result['data']['group_id'],
                    'message': 'MMS sent successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'Send failed'),
                    'error_code': result.get('error_code')
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
    
    def get_message_status(self, group_id: int) -> Dict:
        """
        Check message delivery status
        
        Args:
            group_id: Message group ID
            
        Returns:
            Dict: Status information
        """
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

# Utility functions
def validate_phone_number(phone_number: str) -> bool:
    """Validate Korean phone number format"""
    import re
    pattern = r'^010-\d{4}-\d{4}$'
    return bool(re.match(pattern, phone_number))

def format_phone_number(phone_number: str) -> str:
    """Format phone number to standard format"""
    clean_phone = ''.join(filter(str.isdigit, phone_number))
    if len(clean_phone) == 11 and clean_phone.startswith('010'):
        return f"{clean_phone[:3]}-{clean_phone[3:7]}-{clean_phone[7:]}"
    return phone_number

# Context manager for service
class BaaSServiceContext:
    def __init__(self, api_key: str, project_id: str):
        self.service = BaaSMessageService(api_key, project_id)
        
    def __enter__(self):
        return self.service
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup if needed
        pass
```

## Usage Examples

```python
# Example 1: Basic usage
import os

if __name__ == "__main__":
    # Configuration from environment variables
    api_key = os.getenv('BAAS_API_KEY', 'your-api-key')
    project_id = os.getenv('BAAS_PROJECT_ID', 'your-project-id')
    
    # Create service instance
    service = BaaSMessageService(api_key, project_id)
    
    # Example 1: Send SMS
    recipients = [
        {"phone_number": "010-1234-5678", "member_code": "user_001"}
    ]
    
    sms_result = service.send_sms(
        recipients,
        "안녕하세요! 인증번호는 123456입니다.",
        "02-1234-5678"
    )
    print("SMS Result:", sms_result)
    
    # Example 2: Send MMS
    if sms_result.get('success'):
        mms_result = service.send_mms(
            recipients,
            "이미지가 포함된 MMS입니다.",
            "MMS 테스트",
            "02-1234-5678",
            ["https://example.com/image.jpg"]
        )
        print("MMS Result:", mms_result)
        
        # Example 3: Check status
        if mms_result.get('success'):
            status = service.get_message_status(mms_result['group_id'])
            print("Message Status:", status)

# Example 4: Using context manager
def send_verification_sms(phone_number: str, verification_code: str):
    api_key = os.getenv('BAAS_API_KEY')
    project_id = os.getenv('BAAS_PROJECT_ID')
    
    with BaaSServiceContext(api_key, project_id) as service:
        recipients = [
            {"phone_number": phone_number, "member_code": "verification"}
        ]
        
        message = f"인증번호: {verification_code}"
        result = service.send_sms(recipients, message, "02-1234-5678")
        
        return result

# Example 5: Bulk SMS sending
def send_bulk_notification(phone_numbers: List[str], message: str):
    api_key = os.getenv('BAAS_API_KEY')
    project_id = os.getenv('BAAS_PROJECT_ID')
    
    service = BaaSMessageService(api_key, project_id)
    
    # Prepare recipients
    recipients = [
        {"phone_number": format_phone_number(phone), "member_code": f"user_{i}"}
        for i, phone in enumerate(phone_numbers)
        if validate_phone_number(format_phone_number(phone))
    ]
    
    if not recipients:
        return {"success": False, "error": "No valid phone numbers"}
    
    # Send SMS
    result = service.send_sms(recipients, message, "02-1234-5678")
    
    if result.get('success'):
        print(f"Successfully sent to {len(recipients)} recipients")
        print(f"Group ID: {result['group_id']}")
    
    return result

# Example 6: Async wrapper (optional)
import asyncio
import aiohttp

class AsyncBaaSMessageService:
    def __init__(self, api_key: str, project_id: str, base_url: str = 'https://api.aiapp.link'):
        self.api_key = api_key
        self.project_id = project_id
        self.base_url = base_url
    
    async def send_sms_async(self, recipients: List[Dict], message: str, callback_number: str) -> Dict:
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
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'{self.base_url}/message/sms',
                    headers=headers,
                    json=payload,
                    timeout=30
                ) as response:
                    result = await response.json()
                    
                    if response.status == 200 and result.get('success'):
                        return {
                            'success': True,
                            'group_id': result['data']['group_id'],
                            'message': 'SMS sent successfully'
                        }
                    else:
                        return {
                            'success': False,
                            'error': result.get('message', 'Send failed'),
                            'error_code': result.get('error_code')
                        }
        except Exception as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }

# Async usage example
async def async_sms_example():
    service = AsyncBaaSMessageService('your-api-key', 'your-project-id')
    recipients = [{"phone_number": "010-1234-5678", "member_code": "user_001"}]
    
    result = await service.send_sms_async(
        recipients,
        "비동기 SMS 테스트입니다.",
        "02-1234-5678"
    )
    
    print("Async SMS Result:", result)

# Run async example
# asyncio.run(async_sms_example())
```

## Configuration

### Environment Variables
Create a `.env` file in your project root:

```env
BAAS_API_KEY=your-api-key-here
BAAS_PROJECT_ID=your-project-id-here
```

### Requirements.txt
```txt
requests>=2.25.1
python-dotenv>=0.19.0  # For loading .env files
aiohttp>=3.8.0  # For async support (optional)
```

## Error Handling

All methods return consistent response dictionaries:

```python
# Success response
{
    'success': True,
    'group_id': 12345,
    'message': 'Operation completed successfully'
}

# Error response
{
    'success': False,
    'error': 'Error description',
    'error_code': 'ERROR_CODE'
}
```

## Best Practices

1. **Environment Variables**: Store API keys in environment variables
2. **Error Handling**: Always check the `success` field in responses
3. **Timeout**: Set appropriate timeouts for network requests
4. **Validation**: Validate phone numbers before sending
5. **Rate Limiting**: Implement rate limiting for high-volume applications
6. **Logging**: Log important events and errors for debugging

## Support

- Python 3.7+
- Requests library for HTTP calls
- Optional: aiohttp for async support