# BaaS SMS/MMS JavaScript SDK

Direct API integration for BaaS SMS/MMS services without MCP dependency.

## Installation

```bash
npm install node-fetch  # For Node.js environments
```

## Code

```javascript
/**
 * BaaS SMS/MMS Direct API Client
 * Directly calls https://api.aiapp.link without MCP
 */

class BaaSMessageService {
    constructor(apiKey, baseUrl = 'https://api.aiapp.link') {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
    }
    
    /**
     * Send SMS message
     * @param {Array} recipients - Array of {phone_number, member_code}
     * @param {string} message - Message content (max 2000 chars)
     * @param {string} callbackNumber - Sender callback number
     * @returns {Promise<Object>} Response object
     */
    async sendSMS(recipients, message, callbackNumber) {
        try {
            const response = await fetch(`${this.baseUrl}/api/message/sms`, {
                method: 'POST',
                headers: {
                    'X-API-KEY': this.apiKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    recipients: recipients,
                    message: message,
                    callback_number: callbackNumber,
                    channel_id: 1
                })
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                return {
                    success: true,
                    groupId: result.data.group_id,
                    message: 'SMS sent successfully'
                };
            } else {
                return {
                    success: false,
                    error: result.message || 'Send failed',
                    errorCode: result.error_code
                };
            }
        } catch (error) {
            return {
                success: false,
                error: `Network error: ${error.message}`
            };
        }
    }
    
    /**
     * Send MMS message with images
     * @param {Array} recipients - Array of {phone_number, member_code}
     * @param {string} message - Message content
     * @param {string} subject - MMS subject (max 40 chars)
     * @param {string} callbackNumber - Sender callback number
     * @param {Array} imageUrls - Array of image URLs (max 5)
     * @returns {Promise<Object>} Response object
     */
    async sendMMS(recipients, message, subject, callbackNumber, imageUrls = []) {
        try {
            const response = await fetch(`${this.baseUrl}/api/message/mms`, {
                method: 'POST',
                headers: {
                    'X-API-KEY': this.apiKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    recipients: recipients,
                    message: message,
                    subject: subject,
                    callback_number: callbackNumber,
                    channel_id: 3,
                    img_url_list: imageUrls
                })
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                return {
                    success: true,
                    groupId: result.data.group_id,
                    message: 'MMS sent successfully'
                };
            } else {
                return {
                    success: false,
                    error: result.message || 'Send failed',
                    errorCode: result.error_code
                };
            }
        } catch (error) {
            return {
                success: false,
                error: `Network error: ${error.message}`
            };
        }
    }
    
    /**
     * Check message delivery status
     * @param {number} groupId - Message group ID
     * @returns {Promise<Object>} Status information
     */
    async getMessageStatus(groupId) {
        try {
            const response = await fetch(
                `${this.baseUrl}/message/send_history/sms/${groupId}/messages`,
                {
                    method: 'GET',
                    headers: {
                        'X-API-KEY': this.apiKey,
                        'Content-Type': 'application/json'
                    }
                }
            );
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                const messages = result.data || [];
                const totalCount = messages.length;
                const successCount = messages.filter(msg => msg.result === '성공').length;
                const failedCount = messages.filter(msg => msg.result === '실패').length;
                const pendingCount = totalCount - successCount - failedCount;
                
                let status = '전송중';
                if (pendingCount === 0) {
                    status = failedCount === 0 ? '성공' : 
                            (successCount === 0 ? '실패' : '부분성공');
                }
                
                return {
                    groupId: groupId,
                    status: status,
                    totalCount: totalCount,
                    successCount: successCount,
                    failedCount: failedCount,
                    pendingCount: pendingCount,
                    messages: messages.map(msg => ({
                        phone: msg.phone,
                        name: msg.name,
                        status: msg.result,
                        reason: msg.reason
                    }))
                };
            } else {
                return {
                    success: false,
                    error: result.message || 'Status check failed'
                };
            }
        } catch (error) {
            return {
                success: false,
                error: `Network error: ${error.message}`
            };
        }
    }
}

// Node.js export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { BaaSMessageService };
}

// ES6 export
export { BaaSMessageService };
```

## Usage Examples

```javascript
// Example 1: Basic SMS sending
const messageService = new BaaSMessageService('your-api-key', 'your-project-id');

const recipients = [
    { phone_number: "010-1234-5678", member_code: "user_001" }
];

// Send SMS
messageService.sendSMS(
    recipients,
    "안녕하세요! 인증번호는 123456입니다.",
    "02-1234-5678"
).then(result => {
    console.log('SMS Result:', result);
    if (result.success) {
        // Check status
        return messageService.getMessageStatus(result.groupId);
    }
}).then(status => {
    console.log('Status:', status);
});

// Example 2: MMS with images
messageService.sendMMS(
    recipients,
    "신상품 출시 안내드립니다!",
    "신상품 알림",
    "02-1234-5678",
    ["https://example.com/product.jpg"]
).then(result => {
    console.log('MMS Result:', result);
});

// Example 3: Environment-based configuration
const apiKey = process.env.BAAS_API_KEY || 'your-api-key';
const projectId = process.env.BAAS_PROJECT_ID || 'your-project-id';
const service = new BaaSMessageService(apiKey, projectId);
```

## Configuration

### Environment Variables
- `BAAS_API_KEY`: Your BaaS API key
- `BAAS_PROJECT_ID`: Your project UUID

### Error Handling
All methods return consistent response objects with `success` boolean and appropriate error information.

### Rate Limits
- SMS: Up to 1000 recipients per request
- MMS: Up to 1000 recipients per request
- Status checks: No specific limits

## Support
- Node.js 14+
- Modern browsers with fetch API
- TypeScript support available