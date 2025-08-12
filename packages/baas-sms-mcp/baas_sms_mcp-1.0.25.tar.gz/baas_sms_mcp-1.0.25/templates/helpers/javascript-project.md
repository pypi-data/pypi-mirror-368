# BaaS SMS/MMS Project Helpers - JavaScript

Project-specific helper functions and utilities for {{company_name}}.

## Project Configuration

```javascript
// {{company_name}} Project-Specific Configuration
const PROJECT_CONFIG = {
    PROJECT_ID: '{{project_id}}',
    DEFAULT_CALLBACK: '{{default_callback}}',
    COMPANY_NAME: '{{company_name}}',
    API_KEY: process.env.BAAS_API_KEY || 'your-api-key',
    BASE_URL: 'https://api.aiapp.link'
};

// Pre-configured service instance
const messageService = new BaaSMessageService(
    PROJECT_CONFIG.API_KEY,
    PROJECT_CONFIG.PROJECT_ID
);
```

## Helper Functions

```javascript
/**
 * Send verification SMS with company branding
 * @param {string} phoneNumber - Recipient phone number
 * @param {string} verificationCode - Verification code
 * @param {string} memberCode - Member identifier
 * @returns {Promise<Object>} Send result
 */
async function sendVerificationSMS(phoneNumber, verificationCode, memberCode) {
    const recipients = [
        { phone_number: phoneNumber, member_code: memberCode }
    ];
    
    const message = `[${PROJECT_CONFIG.COMPANY_NAME}] 인증번호: ${verificationCode}`;
    
    return await messageService.sendSMS(
        recipients,
        message,
        PROJECT_CONFIG.DEFAULT_CALLBACK
    );
}

/**
 * Send order confirmation SMS
 * @param {string} phoneNumber - Customer phone number
 * @param {string} orderNumber - Order number
 * @param {number} totalAmount - Total order amount
 * @param {string} memberCode - Member identifier
 * @returns {Promise<Object>} Send result
 */
async function sendOrderConfirmationSMS(phoneNumber, orderNumber, totalAmount, memberCode) {
    const recipients = [
        { phone_number: phoneNumber, member_code: memberCode }
    ];
    
    const message = `[${PROJECT_CONFIG.COMPANY_NAME}] 주문이 완료되었습니다.\n주문번호: ${orderNumber}\n총 금액: ${totalAmount.toLocaleString()}원`;
    
    return await messageService.sendSMS(
        recipients,
        message,
        PROJECT_CONFIG.DEFAULT_CALLBACK
    );
}

/**
 * Send promotional MMS with company branding
 * @param {Array} phoneNumbers - Array of phone numbers
 * @param {string} title - Promotion title
 * @param {string} content - Promotion content
 * @param {Array} imageUrls - Promotion images
 * @returns {Promise<Object>} Send result
 */
async function sendPromotionalMMS(phoneNumbers, title, content, imageUrls = []) {
    const recipients = phoneNumbers.map((phone, index) => ({
        phone_number: phone,
        member_code: `promo_${index}`
    }));
    
    const message = `[${PROJECT_CONFIG.COMPANY_NAME}] ${content}`;
    const subject = `${PROJECT_CONFIG.COMPANY_NAME} - ${title}`;
    
    return await messageService.sendMMS(
        recipients,
        message,
        subject,
        PROJECT_CONFIG.DEFAULT_CALLBACK,
        imageUrls
    );
}

/**
 * Send password reset SMS
 * @param {string} phoneNumber - User phone number
 * @param {string} resetCode - Password reset code
 * @param {string} memberCode - Member identifier
 * @returns {Promise<Object>} Send result
 */
async function sendPasswordResetSMS(phoneNumber, resetCode, memberCode) {
    const recipients = [
        { phone_number: phoneNumber, member_code: memberCode }
    ];
    
    const message = `[${PROJECT_CONFIG.COMPANY_NAME}] 비밀번호 재설정 코드: ${resetCode}\n5분 내에 입력해주세요.`;
    
    return await messageService.sendSMS(
        recipients,
        message,
        PROJECT_CONFIG.DEFAULT_CALLBACK
    );
}

/**
 * Send appointment reminder SMS
 * @param {string} phoneNumber - Customer phone number
 * @param {string} appointmentDate - Appointment date and time
 * @param {string} location - Appointment location
 * @param {string} memberCode - Member identifier
 * @returns {Promise<Object>} Send result
 */
async function sendAppointmentReminderSMS(phoneNumber, appointmentDate, location, memberCode) {
    const recipients = [
        { phone_number: phoneNumber, member_code: memberCode }
    ];
    
    const message = `[${PROJECT_CONFIG.COMPANY_NAME}] 예약 알림\n일시: ${appointmentDate}\n장소: ${location}\n변경이 필요하시면 연락주세요.`;
    
    return await messageService.sendSMS(
        recipients,
        message,
        PROJECT_CONFIG.DEFAULT_CALLBACK
    );
}

/**
 * Send delivery status update SMS
 * @param {string} phoneNumber - Customer phone number
 * @param {string} trackingNumber - Delivery tracking number
 * @param {string} status - Delivery status
 * @param {string} memberCode - Member identifier
 * @returns {Promise<Object>} Send result
 */
async function sendDeliveryStatusSMS(phoneNumber, trackingNumber, status, memberCode) {
    const recipients = [
        { phone_number: phoneNumber, member_code: memberCode }
    ];
    
    const message = `[${PROJECT_CONFIG.COMPANY_NAME}] 배송상태 업데이트\n송장번호: ${trackingNumber}\n상태: ${status}`;
    
    return await messageService.sendSMS(
        recipients,
        message,
        PROJECT_CONFIG.DEFAULT_CALLBACK
    );
}

/**
 * Send welcome MMS for new members
 * @param {string} phoneNumber - New member phone number
 * @param {string} memberName - Member name
 * @param {string} memberCode - Member identifier
 * @param {Array} welcomeImages - Welcome images
 * @returns {Promise<Object>} Send result
 */
async function sendWelcomeMMS(phoneNumber, memberName, memberCode, welcomeImages = []) {
    const recipients = [
        { phone_number: phoneNumber, member_code: memberCode }
    ];
    
    const message = `${memberName}님, ${PROJECT_CONFIG.COMPANY_NAME}에 가입해주셔서 감사합니다!\n앞으로 다양한 혜택과 서비스를 제공해드리겠습니다.`;
    const subject = `${PROJECT_CONFIG.COMPANY_NAME} 가입 환영`;
    
    return await messageService.sendMMS(
        recipients,
        message,
        subject,
        PROJECT_CONFIG.DEFAULT_CALLBACK,
        welcomeImages
    );
}

/**
 * Send event invitation MMS
 * @param {Array} phoneNumbers - Invitee phone numbers
 * @param {string} eventName - Event name
 * @param {string} eventDate - Event date and time
 * @param {string} eventLocation - Event location
 * @param {Array} eventImages - Event images
 * @returns {Promise<Object>} Send result
 */
async function sendEventInvitationMMS(phoneNumbers, eventName, eventDate, eventLocation, eventImages = []) {
    const recipients = phoneNumbers.map((phone, index) => ({
        phone_number: phone,
        member_code: `event_${index}`
    }));
    
    const message = `[${PROJECT_CONFIG.COMPANY_NAME}] ${eventName} 초대\n일시: ${eventDate}\n장소: ${eventLocation}\n많은 참여 부탁드립니다!`;
    const subject = `${eventName} 초대장`;
    
    return await messageService.sendMMS(
        recipients,
        message,
        subject,
        PROJECT_CONFIG.DEFAULT_CALLBACK,
        eventImages
    );
}
```

## Utility Functions

```javascript
/**
 * Format phone number to standard format
 * @param {string} phoneNumber - Raw phone number
 * @returns {string} Formatted phone number
 */
function formatPhoneNumber(phoneNumber) {
    const cleaned = phoneNumber.replace(/\D/g, '');
    if (cleaned.length === 11 && cleaned.startsWith('010')) {
        return `${cleaned.slice(0, 3)}-${cleaned.slice(3, 7)}-${cleaned.slice(7)}`;
    }
    return phoneNumber;
}

/**
 * Validate phone number format
 * @param {string} phoneNumber - Phone number to validate
 * @returns {boolean} True if valid
 */
function isValidPhoneNumber(phoneNumber) {
    const pattern = /^010-\d{4}-\d{4}$/;
    return pattern.test(phoneNumber);
}

/**
 * Generate verification code
 * @param {number} length - Code length (default: 6)
 * @returns {string} Generated code
 */
function generateVerificationCode(length = 6) {
    return Math.floor(Math.random() * Math.pow(10, length)).toString().padStart(length, '0');
}

/**
 * Check if message exceeds SMS limit and suggest MMS
 * @param {string} message - Message content
 * @returns {Object} Recommendation object
 */
function getMessageTypeRecommendation(message) {
    const smsLimit = 90; // Typical SMS character limit for Korean
    const mmsLimit = 2000;
    
    if (message.length <= smsLimit) {
        return {
            type: 'SMS',
            recommended: true,
            reason: 'Message fits within SMS limit'
        };
    } else if (message.length <= mmsLimit) {
        return {
            type: 'MMS',
            recommended: true,
            reason: 'Message exceeds SMS limit, MMS recommended'
        };
    } else {
        return {
            type: 'ERROR',
            recommended: false,
            reason: 'Message exceeds maximum length'
        };
    }
}

/**
 * Batch process phone numbers with validation
 * @param {Array} phoneNumbers - Array of phone numbers
 * @returns {Object} Processed phone numbers
 */
function processPhoneNumbers(phoneNumbers) {
    const valid = [];
    const invalid = [];
    
    phoneNumbers.forEach(phone => {
        const formatted = formatPhoneNumber(phone);
        if (isValidPhoneNumber(formatted)) {
            valid.push(formatted);
        } else {
            invalid.push(phone);
        }
    });
    
    return { valid, invalid };
}
```

## Error Handling

```javascript
/**
 * Enhanced error handler for SMS/MMS operations
 * @param {Object} result - Result from SMS/MMS operation
 * @param {string} operation - Operation type (SMS/MMS)
 * @returns {Object} Standardized error response
 */
function handleMessageResult(result, operation = 'SMS') {
    if (result.success) {
        return {
            success: true,
            message: `${operation} sent successfully`,
            groupId: result.groupId,
            data: result
        };
    }
    
    // Map common error codes to user-friendly messages
    const errorMessages = {
        'MISSING_PROJECT_ID': '프로젝트 설정이 올바르지 않습니다.',
        'INVALID_RECIPIENTS_COUNT': '수신자 수가 올바르지 않습니다.',
        'MESSAGE_TOO_LONG': '메시지가 너무 깁니다.',
        'SUBJECT_TOO_LONG': '제목이 너무 깁니다.',
        'TOO_MANY_IMAGES': '이미지가 너무 많습니다.',
        'API_ERROR': 'API 호출 중 오류가 발생했습니다.',
        'NETWORK_ERROR': '네트워크 오류가 발생했습니다.'
    };
    
    const friendlyMessage = errorMessages[result.errorCode] || result.error || `${operation} 전송에 실패했습니다.`;
    
    return {
        success: false,
        message: friendlyMessage,
        errorCode: result.errorCode,
        originalError: result.error
    };
}

/**
 * Retry mechanism for failed operations
 * @param {Function} operation - Operation to retry
 * @param {number} maxRetries - Maximum retry attempts
 * @param {number} delay - Delay between retries (ms)
 * @returns {Promise<Object>} Operation result
 */
async function retryOperation(operation, maxRetries = 3, delay = 1000) {
    let lastError;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            const result = await operation();
            if (result.success) {
                return result;
            }
            lastError = result;
        } catch (error) {
            lastError = { success: false, error: error.message };
        }
        
        if (attempt < maxRetries) {
            await new Promise(resolve => setTimeout(resolve, delay * attempt));
        }
    }
    
    return {
        success: false,
        error: `Operation failed after ${maxRetries} attempts`,
        lastError
    };
}
```

## Usage Examples

```javascript
// Example 1: User registration verification
async function handleUserRegistration(phoneNumber, userEmail) {
    const verificationCode = generateVerificationCode();
    const result = await sendVerificationSMS(phoneNumber, verificationCode, userEmail);
    
    const handledResult = handleMessageResult(result, 'SMS');
    
    if (handledResult.success) {
        // Store verification code in database/cache
        console.log('Verification SMS sent:', handledResult.groupId);
    } else {
        console.error('Failed to send verification SMS:', handledResult.message);
    }
    
    return handledResult;
}

// Example 2: Order processing workflow
async function processOrder(orderData) {
    const { customerPhone, orderNumber, totalAmount, memberCode } = orderData;
    
    // Send order confirmation
    const confirmationResult = await sendOrderConfirmationSMS(
        customerPhone, 
        orderNumber, 
        totalAmount, 
        memberCode
    );
    
    if (confirmationResult.success) {
        console.log('Order confirmation sent');
        
        // Schedule delivery reminder (simulate with timeout)
        setTimeout(async () => {
            await sendDeliveryStatusSMS(
                customerPhone,
                `TRK${orderNumber}`,
                '배송 준비중',
                memberCode
            );
        }, 60000); // 1 minute delay
    }
    
    return confirmationResult;
}

// Example 3: Bulk promotional campaign
async function runPromotionalCampaign(customerList, promotionData) {
    const { title, content, images } = promotionData;
    
    // Process and validate phone numbers
    const phoneNumbers = customerList.map(customer => customer.phone);
    const processed = processPhoneNumbers(phoneNumbers);
    
    if (processed.invalid.length > 0) {
        console.warn('Invalid phone numbers found:', processed.invalid);
    }
    
    if (processed.valid.length === 0) {
        return { success: false, error: 'No valid phone numbers found' };
    }
    
    // Send promotional MMS
    const result = await retryOperation(
        () => sendPromotionalMMS(processed.valid, title, content, images),
        3,
        2000
    );
    
    return handleMessageResult(result, 'MMS');
}

// Example 4: Event management
async function manageEvent(eventData, inviteeList) {
    const { name, date, location, images } = eventData;
    const phoneNumbers = inviteeList.map(invitee => invitee.phone);
    
    const result = await sendEventInvitationMMS(phoneNumbers, name, date, location, images);
    
    if (result.success) {
        // Track invitation status
        console.log(`Event invitations sent to ${phoneNumbers.length} recipients`);
        
        // Schedule reminder (simulate)
        const reminderDate = new Date(date);
        reminderDate.setDate(reminderDate.getDate() - 1); // 1 day before
        
        console.log(`Reminder scheduled for: ${reminderDate}`);
    }
    
    return result;
}
```

## Integration with Popular Frameworks

### Express.js Integration

```javascript
// routes/sms.js
const express = require('express');
const router = express.Router();

router.post('/verification', async (req, res) => {
    const { phoneNumber, memberCode } = req.body;
    
    try {
        const verificationCode = generateVerificationCode();
        const result = await sendVerificationSMS(phoneNumber, verificationCode, memberCode);
        
        if (result.success) {
            // Store verification code (implement your storage logic)
            res.json({
                success: true,
                message: '인증번호가 전송되었습니다.',
                groupId: result.groupId
            });
        } else {
            res.status(400).json({
                success: false,
                message: result.error
            });
        }
    } catch (error) {
        res.status(500).json({
            success: false,
            message: '서버 오류가 발생했습니다.'
        });
    }
});

module.exports = router;
```

### React Integration

```javascript
// hooks/useBaaSSMS.js
import { useState, useCallback } from 'react';

export function useBaaSSMS() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const sendVerification = useCallback(async (phoneNumber, memberCode) => {
        setLoading(true);
        setError(null);
        
        try {
            const result = await sendVerificationSMS(phoneNumber, generateVerificationCode(), memberCode);
            const handled = handleMessageResult(result, 'SMS');
            
            if (!handled.success) {
                setError(handled.message);
            }
            
            return handled;
        } catch (err) {
            setError('네트워크 오류가 발생했습니다.');
            return { success: false, error: err.message };
        } finally {
            setLoading(false);
        }
    }, []);
    
    return {
        sendVerification,
        loading,
        error
    };
}
```

This helper file provides project-specific functions optimized for {{company_name}}'s messaging needs with proper error handling, validation, and integration examples.