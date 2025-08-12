# BaaS SMS/MMS Vercel Production Deployment

Complete guide for deploying BaaS SMS/MMS integration on Vercel.

## Prerequisites

- Vercel account
- BaaS API key and project ID
- Node.js project with Next.js (recommended)

## Environment Configuration

### 1. Environment Variables

Add these environment variables in Vercel Dashboard:

```bash
# Vercel Dashboard > Settings > Environment Variables
BAAS_API_KEY=your-api-key-here
BAAS_BASE_URL=https://api.aiapp.link
```

### 2. vercel.json Configuration

```json
{
  "env": {
    "BAAS_API_KEY": "@baas-api-key",
    "BAAS_BASE_URL": "https://api.aiapp.link"
  },
  "build": {
    "env": {
      "BAAS_API_KEY": "@baas-api-key"
    }
  },
  "functions": {
    "pages/api/**/*.js": {
      "maxDuration": 30
    }
  }
}
```

## API Routes Implementation

### pages/api/sms/send.js

```javascript
import { BaaSMessageService } from '../../../lib/baas-sms-service';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { recipients, message, callbackNumber } = req.body;

    // Validate input
    if (!recipients || !Array.isArray(recipients) || recipients.length === 0) {
      return res.status(400).json({ error: 'Recipients are required' });
    }

    if (!message || message.length > 2000) {
      return res.status(400).json({ error: 'Invalid message' });
    }

    // Initialize service
    const service = new BaaSMessageService(
      process.env.BAAS_API_KEY
    );

    // Send SMS
    const result = await service.sendSMS(recipients, message, callbackNumber);

    if (result.success) {
      res.status(200).json({
        success: true,
        groupId: result.groupId,
        message: 'SMS sent successfully'
      });
    } else {
      res.status(400).json({
        success: false,
        error: result.error,
        errorCode: result.errorCode
      });
    }

  } catch (error) {
    console.error('SMS API Error:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
}
```

### pages/api/mms/send.js

```javascript
import { BaaSMessageService } from '../../../lib/baas-sms-service';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { recipients, message, subject, callbackNumber, imageUrls } = req.body;

    // Validate input
    if (!recipients || !Array.isArray(recipients) || recipients.length === 0) {
      return res.status(400).json({ error: 'Recipients are required' });
    }

    if (!message || message.length > 2000) {
      return res.status(400).json({ error: 'Invalid message' });
    }

    if (!subject || subject.length > 40) {
      return res.status(400).json({ error: 'Invalid subject' });
    }

    if (imageUrls && imageUrls.length > 5) {
      return res.status(400).json({ error: 'Maximum 5 images allowed' });
    }

    // Initialize service
    const service = new BaaSMessageService(
      process.env.BAAS_API_KEY
    );

    // Send MMS
    const result = await service.sendMMS(recipients, message, subject, callbackNumber, imageUrls);

    if (result.success) {
      res.status(200).json({
        success: true,
        groupId: result.groupId,
        message: 'MMS sent successfully'
      });
    } else {
      res.status(400).json({
        success: false,
        error: result.error,
        errorCode: result.errorCode
      });
    }

  } catch (error) {
    console.error('MMS API Error:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
}
```

### pages/api/sms/status/[groupId].js

```javascript
import { BaaSMessageService } from '../../../../lib/baas-sms-service';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { groupId } = req.query;

    if (!groupId || isNaN(parseInt(groupId))) {
      return res.status(400).json({ error: 'Invalid group ID' });
    }

    // Initialize service
    const service = new BaaSMessageService(
      process.env.BAAS_API_KEY
    );

    // Check status
    const result = await service.getMessageStatus(parseInt(groupId));

    if (result.success !== false) {
      res.status(200).json(result);
    } else {
      res.status(400).json({
        success: false,
        error: result.error
      });
    }

  } catch (error) {
    console.error('Status API Error:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
}
```

## Frontend Integration

### components/SMSForm.js

```javascript
import { useState } from 'react';

export default function SMSForm() {
  const [formData, setFormData] = useState({
    phoneNumber: '',
    message: '',
    callbackNumber: '02-1234-5678'
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const recipients = [
        {
          phone_number: formData.phoneNumber,
          member_code: 'web_user'
        }
      ];

      const response = await fetch('/api/sms/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recipients,
          message: formData.message,
          callbackNumber: formData.callbackNumber
        }),
      });

      const data = await response.json();
      setResult(data);

      if (data.success) {
        setFormData({ ...formData, phoneNumber: '', message: '' });
      }

    } catch (error) {
      setResult({
        success: false,
        error: 'Network error occurred'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">SMS 전송</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">
            전화번호
          </label>
          <input
            type="tel"
            value={formData.phoneNumber}
            onChange={(e) => setFormData({ ...formData, phoneNumber: e.target.value })}
            placeholder="010-1234-5678"
            className="w-full p-2 border rounded-md"
            required
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">
            메시지
          </label>
          <textarea
            value={formData.message}
            onChange={(e) => setFormData({ ...formData, message: e.target.value })}
            placeholder="전송할 메시지를 입력하세요"
            maxLength={2000}
            rows={4}
            className="w-full p-2 border rounded-md"
            required
          />
          <div className="text-sm text-gray-500 mt-1">
            {formData.message.length}/2000
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">
            발신번호
          </label>
          <input
            type="tel"
            value={formData.callbackNumber}
            onChange={(e) => setFormData({ ...formData, callbackNumber: e.target.value })}
            className="w-full p-2 border rounded-md"
            required
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600 disabled:opacity-50"
        >
          {loading ? '전송 중...' : 'SMS 전송'}
        </button>
      </form>

      {result && (
        <div className={`mt-4 p-3 rounded-md ${
          result.success ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }`}>
          {result.success ? (
            <div>
              <div>✅ SMS가 성공적으로 전송되었습니다!</div>
              <div className="text-sm mt-1">Group ID: {result.groupId}</div>
            </div>
          ) : (
            <div>❌ {result.error}</div>
          )}
        </div>
      )}
    </div>
  );
}
```

## Deployment Steps

### 1. Install Dependencies

```bash
npm install
# or
yarn install
```

### 2. Environment Variables Setup

```bash
# Add to Vercel Dashboard > Settings > Environment Variables
BAAS_API_KEY=your-actual-api-key
```

### 3. Deploy to Vercel

```bash
# Using Vercel CLI
npm i -g vercel
vercel

# Or connect GitHub repository in Vercel Dashboard
```

### 4. Test Deployment

```bash
curl -X POST https://your-app.vercel.app/api/sms/send \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": [{"phone_number": "010-1234-5678", "member_code": "test"}],
    "message": "Test message",
    "callbackNumber": "02-1234-5678"
  }'
```

## Edge Runtime Compatibility

### pages/api/sms/send-edge.js (Edge Runtime)

```javascript
export const config = {
  runtime: 'edge',
}

export default async function handler(req) {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  try {
    const body = await req.json();
    const { recipients, message, callbackNumber } = body;

    // Validate input
    if (!recipients || !Array.isArray(recipients) || recipients.length === 0) {
      return new Response(JSON.stringify({ error: 'Recipients are required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Make direct API call (Edge Runtime compatible)
    const response = await fetch('https://api.aiapp.link/api/message/sms', {
      method: 'POST',
      headers: {
        'X-API-KEY': process.env.BAAS_API_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        recipients,
        message,
        callback_number: callbackNumber,
        channel_id: 1
      })
    });

    const result = await response.json();

    if (response.ok && result.success) {
      return new Response(JSON.stringify({
        success: true,
        groupId: result.data.group_id,
        message: 'SMS sent successfully'
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    } else {
      return new Response(JSON.stringify({
        success: false,
        error: result.message || 'Send failed',
        errorCode: result.error_code
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: 'Internal server error'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
```

## Monitoring and Logging

### lib/logger.js

```javascript
export class Logger {
  static log(level, message, meta = {}) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      message,
      ...meta
    };

    // In production, use a logging service like LogRocket, Sentry, etc.
    if (process.env.NODE_ENV === 'production') {
      console.log(JSON.stringify(logEntry));
    } else {
      console.log(`[${timestamp}] ${level.toUpperCase()}: ${message}`, meta);
    }
  }

  static info(message, meta = {}) {
    this.log('info', message, meta);
  }

  static error(message, meta = {}) {
    this.log('error', message, meta);
  }

  static warn(message, meta = {}) {
    this.log('warn', message, meta);
  }
}
```

## Security Best Practices

### 1. Rate Limiting

```javascript
// lib/rate-limit.js
const rateLimitMap = new Map();

export function rateLimit(ip, maxRequests = 10, windowMs = 60000) {
  const now = Date.now();
  const windowStart = now - windowMs;

  if (!rateLimitMap.has(ip)) {
    rateLimitMap.set(ip, []);
  }

  const requests = rateLimitMap.get(ip);
  
  // Remove old requests
  const validRequests = requests.filter(time => time > windowStart);
  
  if (validRequests.length >= maxRequests) {
    return false;
  }

  validRequests.push(now);
  rateLimitMap.set(ip, validRequests);
  
  return true;
}
```

### 2. Input Validation

```javascript
// lib/validation.js
export function validatePhoneNumber(phoneNumber) {
  const pattern = /^010-\d{4}-\d{4}$/;
  return pattern.test(phoneNumber);
}

export function validateMessage(message) {
  return message && typeof message === 'string' && message.length <= 2000;
}

export function sanitizeInput(input) {
  if (typeof input !== 'string') return input;
  return input.trim().replace(/[<>]/g, '');
}
```

## Troubleshooting

### Common Issues

1. **Environment Variables Not Loading**
   - Check Vercel Dashboard environment variable spelling
   - Ensure variables are set for correct environment (Production/Preview/Development)

2. **Function Timeout**
   - Increase timeout in vercel.json
   - Optimize API calls to BaaS service

3. **CORS Issues**
   - Add proper CORS headers to API routes
   - Configure allowed origins

4. **Build Failures**
   - Check Node.js version compatibility
   - Verify all dependencies are listed in package.json

## Performance Optimization

### 1. Caching Strategy

```javascript
// lib/cache.js
const cache = new Map();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

export function getCached(key) {
  const item = cache.get(key);
  if (!item) return null;
  
  if (Date.now() > item.expiry) {
    cache.delete(key);
    return null;
  }
  
  return item.data;
}

export function setCache(key, data, ttl = CACHE_TTL) {
  cache.set(key, {
    data,
    expiry: Date.now() + ttl
  });
}
```

### 2. Bundle Optimization

```javascript
// next.config.js
module.exports = {
  webpack: (config) => {
    config.optimization.splitChunks = {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
      },
    };
    return config;
  },
};
```

This deployment guide ensures your BaaS SMS/MMS integration runs smoothly on Vercel with proper error handling, monitoring, and security measures.