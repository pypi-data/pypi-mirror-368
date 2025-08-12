# BaaS SMS/MMS PHP SDK

Direct API integration for BaaS SMS/MMS services without MCP dependency.

## Installation

PHP 7.4+ with cURL extension (usually included by default)

## Code

```php
<?php
/**
 * BaaS SMS/MMS Direct API Client
 * Directly calls https://api.aiapp.link without MCP
 */

class BaaSMessageService {
    private $apiKey;
    private $projectId;
    private $baseUrl;
    
    public function __construct($apiKey, $baseUrl = 'https://api.aiapp.link') {
        $this->apiKey = $apiKey;
        $this->baseUrl = $baseUrl;
    }
    
    /**
     * Send SMS message
     * @param array $recipients Array of ['phone_number' => '', 'member_code' => '']
     * @param string $message Message content (max 2000 chars)
     * @param string $callbackNumber Sender callback number
     * @return array Response array
     */
    public function sendSMS($recipients, $message, $callbackNumber) {
        $payload = [
            'recipients' => $recipients,
            'message' => $message,
            'callback_number' => $callbackNumber,
            'channel_id' => 1
        ];
        
        return $this->makeRequest('/api/message/sms', $payload);
    }
    
    /**
     * Send MMS message with images
     * @param array $recipients Array of recipients
     * @param string $message Message content
     * @param string $subject MMS subject (max 40 chars)
     * @param string $callbackNumber Sender callback number
     * @param array $imageUrls Array of image URLs (max 5)
     * @return array Response array
     */
    public function sendMMS($recipients, $message, $subject, $callbackNumber, $imageUrls = []) {
        $payload = [
            'recipients' => $recipients,
            'message' => $message,
            'subject' => $subject,
            'callback_number' => $callbackNumber,
            'channel_id' => 3,
            'img_url_list' => $imageUrls
        ];
        
        return $this->makeRequest('/api/message/mms', $payload);
    }
    
    /**
     * Check message delivery status
     * @param int $groupId Message group ID
     * @return array Status information
     */
    public function getMessageStatus($groupId) {
        $url = "/message/send_history/sms/{$groupId}/messages";
        return $this->makeRequest($url, null, 'GET');
    }
    
    /**
     * Make HTTP request to BaaS API
     * @param string $endpoint API endpoint
     * @param array|null $payload Request payload
     * @param string $method HTTP method
     * @return array Response array
     */
    private function makeRequest($endpoint, $payload = null, $method = 'POST') {
        $headers = [
            'X-API-KEY: ' . $this->apiKey,
            'Content-Type: application/json'
        ];
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $this->baseUrl . $endpoint);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
        
        if ($method === 'POST') {
            curl_setopt($ch, CURLOPT_POST, true);
            if ($payload) {
                curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
            }
        }
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        curl_close($ch);
        
        if ($response === false || !empty($error)) {
            return [
                'success' => false,
                'error' => 'cURL error: ' . $error
            ];
        }
        
        $result = json_decode($response, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            return [
                'success' => false,
                'error' => 'Invalid JSON response'
            ];
        }
        
        if ($httpCode === 200 && isset($result['success']) && $result['success']) {
            return [
                'success' => true,
                'group_id' => $result['data']['group_id'] ?? null,
                'message' => 'Request successful'
            ];
        } else {
            return [
                'success' => false,
                'error' => $result['message'] ?? 'Request failed',
                'error_code' => $result['error_code'] ?? null
            ];
        }
    }
    
    /**
     * Validate phone number format
     * @param string $phoneNumber Phone number to validate
     * @return bool True if valid
     */
    public static function validatePhoneNumber($phoneNumber) {
        return preg_match('/^010-\d{4}-\d{4}$/', $phoneNumber);
    }
    
    /**
     * Format phone number to standard format
     * @param string $phoneNumber Raw phone number
     * @return string Formatted phone number
     */
    public static function formatPhoneNumber($phoneNumber) {
        $cleanPhone = preg_replace('/[^\d]/', '', $phoneNumber);
        
        if (strlen($cleanPhone) === 11 && substr($cleanPhone, 0, 3) === '010') {
            return substr($cleanPhone, 0, 3) . '-' . 
                   substr($cleanPhone, 3, 4) . '-' . 
                   substr($cleanPhone, 7, 4);
        }
        
        return $phoneNumber;
    }
}

/**
 * BaaS Message Service Factory
 * Handles configuration from environment variables
 */
class BaaSMessageServiceFactory {
    public static function create($apiKey = null, $projectId = null) {
        $apiKey = $apiKey ?: $_ENV['BAAS_API_KEY'] ?? null;
        $projectId = $projectId ?: $_ENV['BAAS_PROJECT_ID'] ?? null;
        
        if (!$apiKey) {
            throw new InvalidArgumentException('BAAS_API_KEY is required');
        }
        
        if (!$projectId) {
            throw new InvalidArgumentException('BAAS_PROJECT_ID is required');
        }
        
        return new BaaSMessageService($apiKey, $projectId);
    }
}

/**
 * Simple logging utility
 */
class BaaSLogger {
    private static $logFile = 'baas_sms.log';
    
    public static function log($level, $message, $context = []) {
        $timestamp = date('Y-m-d H:i:s');
        $contextStr = empty($context) ? '' : ' ' . json_encode($context);
        $logLine = "[{$timestamp}] {$level}: {$message}{$contextStr}" . PHP_EOL;
        
        file_put_contents(self::$logFile, $logLine, FILE_APPEND | LOCK_EX);
    }
    
    public static function info($message, $context = []) {
        self::log('INFO', $message, $context);
    }
    
    public static function error($message, $context = []) {
        self::log('ERROR', $message, $context);
    }
}

/**
 * Configuration manager
 */
class BaaSConfig {
    private static $config = [];
    
    public static function load($configFile = null) {
        if ($configFile && file_exists($configFile)) {
            $fileConfig = include $configFile;
            self::$config = array_merge(self::$config, $fileConfig);
        }
        
        // Load from environment variables
        $envConfig = [
            'api_key' => $_ENV['BAAS_API_KEY'] ?? null,
            'project_id' => $_ENV['BAAS_PROJECT_ID'] ?? null,
            'base_url' => $_ENV['BAAS_BASE_URL'] ?? 'https://api.aiapp.link',
            'default_callback' => $_ENV['BAAS_DEFAULT_CALLBACK'] ?? '02-1234-5678'
        ];
        
        self::$config = array_merge(self::$config, array_filter($envConfig));
    }
    
    public static function get($key, $default = null) {
        return self::$config[$key] ?? $default;
    }
    
    public static function set($key, $value) {
        self::$config[$key] = $value;
    }
}

/**
 * Bulk SMS handler
 */
class BulkSMSHandler {
    private $service;
    private $batchSize;
    
    public function __construct(BaaSMessageService $service, $batchSize = 100) {
        $this->service = $service;
        $this->batchSize = $batchSize;
    }
    
    /**
     * Send SMS to multiple recipients in batches
     * @param array $phoneNumbers Array of phone numbers
     * @param string $message Message content
     * @param string $callbackNumber Callback number
     * @return array Results array
     */
    public function sendBulkSMS($phoneNumbers, $message, $callbackNumber) {
        $results = [];
        $batches = array_chunk($phoneNumbers, $this->batchSize);
        
        foreach ($batches as $batchIndex => $batch) {
            $recipients = [];
            foreach ($batch as $index => $phoneNumber) {
                $formattedPhone = BaaSMessageService::formatPhoneNumber($phoneNumber);
                if (BaaSMessageService::validatePhoneNumber($formattedPhone)) {
                    $recipients[] = [
                        'phone_number' => $formattedPhone,
                        'member_code' => 'bulk_' . ($batchIndex * $this->batchSize + $index)
                    ];
                }
            }
            
            if (!empty($recipients)) {
                $result = $this->service->sendSMS($recipients, $message, $callbackNumber);
                $results[] = [
                    'batch' => $batchIndex + 1,
                    'recipients_count' => count($recipients),
                    'result' => $result
                ];
                
                BaaSLogger::info("Batch " . ($batchIndex + 1) . " sent", [
                    'recipients' => count($recipients),
                    'success' => $result['success']
                ]);
                
                // Add delay between batches to avoid rate limiting
                if ($batchIndex < count($batches) - 1) {
                    sleep(1);
                }
            }
        }
        
        return $results;
    }
}
```

## Usage Examples

```php
<?php
// Example 1: Basic SMS sending
require_once 'BaaSMessageService.php';

// Initialize configuration
BaaSConfig::load('config.php');  // Optional config file
BaaSConfig::load();  // Load from environment

try {
    $service = BaaSMessageServiceFactory::create();
    
    $recipients = [
        ['phone_number' => '010-1234-5678', 'member_code' => 'user_001']
    ];
    
    $result = $service->sendSMS(
        $recipients,
        '안녕하세요! 인증번호는 123456입니다.',
        '02-1234-5678'
    );
    
    if ($result['success']) {
        echo "SMS sent successfully! Group ID: " . $result['group_id'] . "\n";
        BaaSLogger::info('SMS sent successfully', ['group_id' => $result['group_id']]);
    } else {
        echo "Failed to send SMS: " . $result['error'] . "\n";
        BaaSLogger::error('SMS sending failed', ['error' => $result['error']]);
    }
    
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
    BaaSLogger::error('Exception occurred', ['exception' => $e->getMessage()]);
}

// Example 2: MMS with images
try {
    $service = BaaSMessageServiceFactory::create();
    
    $recipients = [
        ['phone_number' => '010-1234-5678', 'member_code' => 'user_001']
    ];
    
    $imageUrls = [
        'https://example.com/image1.jpg',
        'https://example.com/image2.png'
    ];
    
    $result = $service->sendMMS(
        $recipients,
        '이미지가 포함된 MMS입니다.',
        'MMS 테스트',
        '02-1234-5678',
        $imageUrls
    );
    
    if ($result['success']) {
        echo "MMS sent successfully! Group ID: " . $result['group_id'] . "\n";
    } else {
        echo "Failed to send MMS: " . $result['error'] . "\n";
    }
    
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}

// Example 3: Check message status
if (isset($result['group_id']) && $result['success']) {
    $status = $service->getMessageStatus($result['group_id']);
    
    if ($status['success'] !== false) {
        echo "Message Status: " . $status['status'] . "\n";
        echo "Success Count: " . $status['success_count'] . "\n";
        echo "Failed Count: " . $status['failed_count'] . "\n";
    }
}

// Example 4: Bulk SMS sending
$phoneNumbers = [
    '010-1111-2222',
    '010-3333-4444',
    '010-5555-6666',
    // ... more numbers
];

$bulk = new BulkSMSHandler($service);
$bulkResults = $bulk->sendBulkSMS(
    $phoneNumbers,
    '대량 발송 테스트 메시지입니다.',
    '02-1234-5678'
);

foreach ($bulkResults as $batchResult) {
    echo "Batch {$batchResult['batch']}: ";
    echo $batchResult['result']['success'] ? 'Success' : 'Failed';
    echo " ({$batchResult['recipients_count']} recipients)\n";
}

// Example 5: Web form handler
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $phoneNumber = $_POST['phone_number'] ?? '';
    $message = $_POST['message'] ?? '';
    $callbackNumber = $_POST['callback_number'] ?? '02-1234-5678';
    
    // Validate input
    $errors = [];
    if (empty($phoneNumber)) {
        $errors[] = '전화번호를 입력해주세요.';
    } elseif (!BaaSMessageService::validatePhoneNumber(BaaSMessageService::formatPhoneNumber($phoneNumber))) {
        $errors[] = '올바른 전화번호 형식이 아닙니다. (예: 010-1234-5678)';
    }
    
    if (empty($message)) {
        $errors[] = '메시지를 입력해주세요.';
    } elseif (strlen($message) > 2000) {
        $errors[] = '메시지는 2000자를 초과할 수 없습니다.';
    }
    
    if (empty($errors)) {
        try {
            $service = BaaSMessageServiceFactory::create();
            $recipients = [
                ['phone_number' => BaaSMessageService::formatPhoneNumber($phoneNumber), 'member_code' => 'web_user']
            ];
            
            $result = $service->sendSMS($recipients, $message, $callbackNumber);
            
            if ($result['success']) {
                $successMessage = "SMS가 성공적으로 전송되었습니다! (Group ID: {$result['group_id']})";
            } else {
                $errorMessage = "SMS 전송에 실패했습니다: " . $result['error'];
            }
            
        } catch (Exception $e) {
            $errorMessage = "오류가 발생했습니다: " . $e->getMessage();
        }
    }
}

// Example 6: CSV bulk processing
function processBulkSMSFromCSV($csvFile, $message, $callbackNumber) {
    if (!file_exists($csvFile)) {
        throw new InvalidArgumentException("CSV file not found: $csvFile");
    }
    
    $phoneNumbers = [];
    $handle = fopen($csvFile, 'r');
    
    // Skip header row
    fgetcsv($handle);
    
    while (($data = fgetcsv($handle)) !== FALSE) {
        if (isset($data[0]) && !empty($data[0])) {
            $phoneNumbers[] = $data[0];
        }
    }
    
    fclose($handle);
    
    if (empty($phoneNumbers)) {
        throw new InvalidArgumentException("No phone numbers found in CSV");
    }
    
    $service = BaaSMessageServiceFactory::create();
    $bulk = new BulkSMSHandler($service);
    
    return $bulk->sendBulkSMS($phoneNumbers, $message, $callbackNumber);
}

// Usage
// $results = processBulkSMSFromCSV('recipients.csv', 'Hello from PHP!', '02-1234-5678');

// Example 7: Simple verification SMS function
function sendVerificationSMS($phoneNumber, $verificationCode) {
    try {
        $service = BaaSMessageServiceFactory::create();
        $recipients = [
            ['phone_number' => BaaSMessageService::formatPhoneNumber($phoneNumber), 'member_code' => 'verification']
        ];
        
        $message = "[인증번호] {$verificationCode}를 입력해주세요.";
        $result = $service->sendSMS($recipients, $message, BaaSConfig::get('default_callback', '02-1234-5678'));
        
        return $result;
        
    } catch (Exception $e) {
        BaaSLogger::error('Verification SMS failed', ['phone' => $phoneNumber, 'error' => $e->getMessage()]);
        return ['success' => false, 'error' => $e->getMessage()];
    }
}

// Usage
// $result = sendVerificationSMS('010-1234-5678', '123456');
?>
```

## Configuration

### config.php
```php
<?php
return [
    'api_key' => 'your-api-key-here',
    'project_id' => 'your-project-id-here',
    'base_url' => 'https://api.aiapp.link',
    'default_callback' => '02-1234-5678'
];
```

### Environment Variables (.env)
```env
BAAS_API_KEY=your-api-key-here
BAAS_PROJECT_ID=your-project-id-here
BAAS_BASE_URL=https://api.aiapp.link
BAAS_DEFAULT_CALLBACK=02-1234-5678
```

## HTML Form Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>SMS 전송</title>
    <meta charset="UTF-8">
</head>
<body>
    <h1>SMS 전송</h1>
    
    <?php if (isset($successMessage)): ?>
        <div style="color: green; padding: 10px; background: #e8f5e8; border: 1px solid #4caf50;">
            <?= htmlspecialchars($successMessage) ?>
        </div>
    <?php endif; ?>
    
    <?php if (isset($errorMessage)): ?>
        <div style="color: red; padding: 10px; background: #ffeaea; border: 1px solid #f44336;">
            <?= htmlspecialchars($errorMessage) ?>
        </div>
    <?php endif; ?>
    
    <?php if (!empty($errors)): ?>
        <div style="color: red; padding: 10px; background: #ffeaea; border: 1px solid #f44336;">
            <ul>
                <?php foreach ($errors as $error): ?>
                    <li><?= htmlspecialchars($error) ?></li>
                <?php endforeach; ?>
            </ul>
        </div>
    <?php endif; ?>
    
    <form method="POST">
        <div style="margin-bottom: 15px;">
            <label for="phone_number">전화번호:</label><br>
            <input type="tel" id="phone_number" name="phone_number" 
                   placeholder="010-1234-5678" 
                   value="<?= htmlspecialchars($_POST['phone_number'] ?? '') ?>" 
                   required>
        </div>
        
        <div style="margin-bottom: 15px;">
            <label for="message">메시지:</label><br>
            <textarea id="message" name="message" rows="4" cols="50" 
                      maxlength="2000" placeholder="전송할 메시지를 입력하세요" 
                      required><?= htmlspecialchars($_POST['message'] ?? '') ?></textarea>
            <br><small>최대 2000자</small>
        </div>
        
        <div style="margin-bottom: 15px;">
            <label for="callback_number">발신번호:</label><br>
            <input type="tel" id="callback_number" name="callback_number" 
                   value="<?= htmlspecialchars($_POST['callback_number'] ?? '02-1234-5678') ?>" 
                   required>
        </div>
        
        <button type="submit">SMS 전송</button>
    </form>
</body>
</html>
```

## Error Handling

All methods return consistent response arrays:

```php
// Success response
[
    'success' => true,
    'group_id' => 12345,
    'message' => 'Request successful'
]

// Error response
[
    'success' => false,
    'error' => 'Error description',
    'error_code' => 'ERROR_CODE'  // Optional
]
```

## Best Practices

1. **Environment Variables**: Store API keys in environment variables, not in code
2. **Error Handling**: Always check the `success` field in responses
3. **Validation**: Validate phone numbers and message content before sending
4. **Logging**: Implement proper logging for debugging and audit trails
5. **Rate Limiting**: Implement delays between bulk operations
6. **Security**: Use HTTPS and validate all input data
7. **Configuration**: Use configuration files or environment variables for settings

## Requirements

- PHP 7.4 or higher
- cURL extension enabled
- JSON extension enabled (usually included by default)
- SSL/TLS support for HTTPS requests