# BaaS SMS/MMS React Integration

React hooks and components for BaaS SMS/MMS services.

## Installation

```bash
npm install axios  # or use fetch
```

## Code

```javascript
/**
 * BaaS SMS/MMS React Integration
 * Custom hooks and service for React applications
 */

import { useState, useCallback } from 'react';

// Base service class
class BaaSMessageService {
    constructor(apiKey, projectId, baseUrl = 'https://api.aiapp.link') {
        this.apiKey = apiKey;
        this.projectId = projectId;
        this.baseUrl = baseUrl;
    }
    
    async sendSMS(recipients, message, callbackNumber) {
        try {
            const response = await fetch(`${this.baseUrl}/message/sms`, {
                method: 'POST',
                headers: {
                    'X-API-KEY': this.apiKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    recipients: recipients,
                    message: message,
                    callback_number: callbackNumber,
                    project_id: this.projectId,
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
    
    async sendMMS(recipients, message, subject, callbackNumber, imageUrls = []) {
        try {
            const response = await fetch(`${this.baseUrl}/message/mms`, {
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
                    project_id: this.projectId,
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

/**
 * React Hook for BaaS SMS service
 */
export function useBaaSMessageService(apiKey, projectId) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lastResult, setLastResult] = useState(null);
    
    const service = new BaaSMessageService(apiKey, projectId);
    
    const sendSMS = useCallback(async (recipients, message, callbackNumber) => {
        setLoading(true);
        setError(null);
        
        try {
            const result = await service.sendSMS(recipients, message, callbackNumber);
            setLastResult(result);
            return result;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [service]);
    
    const sendMMS = useCallback(async (recipients, message, subject, callbackNumber, imageUrls) => {
        setLoading(true);
        setError(null);
        
        try {
            const result = await service.sendMMS(recipients, message, subject, callbackNumber, imageUrls);
            setLastResult(result);
            return result;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [service]);
    
    const checkStatus = useCallback(async (groupId) => {
        setLoading(true);
        setError(null);
        
        try {
            const result = await service.getMessageStatus(groupId);
            return result;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [service]);
    
    return {
        sendSMS,
        sendMMS,
        checkStatus,
        loading,
        error,
        lastResult
    };
}

/**
 * React Context Provider for BaaS service
 */
import { createContext, useContext } from 'react';

const BaaSContext = createContext();

export function BaaSProvider({ children, apiKey, projectId }) {
    const service = useBaaSMessageService(apiKey, projectId);
    
    return (
        <BaaSContext.Provider value={service}>
            {children}
        </BaaSContext.Provider>
    );
}

export function useBaaS() {
    const context = useContext(BaaSContext);
    if (!context) {
        throw new Error('useBaaS must be used within BaaSProvider');
    }
    return context;
}
```

## Usage Examples

```javascript
// Example 1: Using the hook directly
import React from 'react';
import { useBaaSMessageService } from './baas-sms-service';

function SMSComponent() {
    const { sendSMS, loading, error, lastResult } = useBaaSMessageService(
        process.env.REACT_APP_BAAS_API_KEY,
        process.env.REACT_APP_BAAS_PROJECT_ID
    );
    
    const handleSendSMS = async () => {
        const recipients = [
            { phone_number: "010-1234-5678", member_code: "user_001" }
        ];
        
        try {
            const result = await sendSMS(
                recipients,
                "안녕하세요! 인증번호는 123456입니다.",
                "02-1234-5678"
            );
            
            if (result.success) {
                alert('SMS sent successfully!');
            } else {
                alert(`Failed to send SMS: ${result.error}`);
            }
        } catch (err) {
            console.error('Error:', err);
        }
    };
    
    return (
        <div>
            <button onClick={handleSendSMS} disabled={loading}>
                {loading ? 'Sending...' : 'Send SMS'}
            </button>
            
            {error && <div style={{color: 'red'}}>Error: {error}</div>}
            
            {lastResult && (
                <div>
                    Last result: {lastResult.success ? 'Success' : 'Failed'}
                    {lastResult.groupId && <div>Group ID: {lastResult.groupId}</div>}
                </div>
            )}
        </div>
    );
}

// Example 2: Using Context Provider
function App() {
    return (
        <BaaSProvider 
            apiKey={process.env.REACT_APP_BAAS_API_KEY}
            projectId={process.env.REACT_APP_BAAS_PROJECT_ID}
        >
            <SMSComponent />
        </BaaSProvider>
    );
}

function SMSComponent() {
    const { sendSMS, loading, error } = useBaaS();
    
    // ... component logic
}

// Example 3: Form component with validation
function SMSForm() {
    const [phoneNumber, setPhoneNumber] = useState('');
    const [message, setMessage] = useState('');
    const { sendSMS, loading, error } = useBaaS();
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!phoneNumber || !message) {
            alert('Please fill in all fields');
            return;
        }
        
        const recipients = [
            { phone_number: phoneNumber, member_code: "user_001" }
        ];
        
        try {
            const result = await sendSMS(recipients, message, "02-1234-5678");
            if (result.success) {
                setPhoneNumber('');
                setMessage('');
                alert('SMS sent successfully!');
            }
        } catch (err) {
            console.error('Error:', err);
        }
    };
    
    return (
        <form onSubmit={handleSubmit}>
            <div>
                <label>Phone Number:</label>
                <input
                    type="tel"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    placeholder="010-1234-5678"
                />
            </div>
            
            <div>
                <label>Message:</label>
                <textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Enter your message"
                    maxLength={2000}
                />
            </div>
            
            <button type="submit" disabled={loading}>
                {loading ? 'Sending...' : 'Send SMS'}
            </button>
            
            {error && <div className="error">Error: {error}</div>}
        </form>
    );
}
```

## Environment Variables

Create a `.env` file in your React project root:

```env
REACT_APP_BAAS_API_KEY=your-api-key-here
REACT_APP_BAAS_PROJECT_ID=your-project-id-here
```

## TypeScript Support

```typescript
interface Recipient {
    phone_number: string;
    member_code: string;
}

interface SendResult {
    success: boolean;
    groupId?: number;
    message: string;
    error?: string;
    errorCode?: string;
}

interface StatusResult {
    groupId: number;
    status: string;
    totalCount: number;
    successCount: number;
    failedCount: number;
    pendingCount: number;
    messages: Array<{
        phone: string;
        name: string;
        status: string;
        reason?: string;
    }>;
}
```

## Best Practices

1. **Error Handling**: Always handle errors gracefully in your UI
2. **Loading States**: Show loading indicators during API calls
3. **Validation**: Validate phone numbers and message content
4. **Environment Variables**: Never hardcode API keys
5. **Rate Limiting**: Implement client-side rate limiting if needed