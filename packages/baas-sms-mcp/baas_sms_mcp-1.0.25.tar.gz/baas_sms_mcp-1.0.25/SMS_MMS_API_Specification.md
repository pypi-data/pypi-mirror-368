# SMS/MMS API 명세서

## 개요

본 문서는 MaaS (Mobile-as-a-Service) 플랫폼의 SMS/MMS 메시징 서비스 API에 대해 정의합니다. 이 명세서는 MCP 서버 구축을 위한 기반 문서로 사용됩니다.

## 아키텍처 개요

### 시스템 구성
- **프론트엔드**: FastAPI 기반 REST API
- **백엔드**: 외부 메시징 벤더 연동 (Telnet, Uracle)
- **데이터베이스**: MySQL/MariaDB with SQLAlchemy ORM
- **인증**: JWT 기반 프로젝트별 격리

### 메시지 처리 플로우
1. API 요청 수신 및 검증
2. 메시지 그룹 생성
3. 수신자별 메시지 레코드 생성
4. 외부 벤더 API 호출
5. 결과 처리 및 상태 업데이트

## API 엔드포인트

### 1. SMS 발송 API

#### 엔드포인트
```
POST /message/sms
```

#### 요청 헤더
```
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

#### 요청 바디 (SMSRequest)
```json
{
    "recipients": [
        {
            "phone_number": "010-1234-5678",
            "member_code": "uuid-string",
            "message_id": null
        }
    ],
    "message": "전송할 SMS 메시지 내용",
    "callback_number": "02-1234-5678",
    "project_id": "uuid-string",
    "channel_id": 1
}
```

#### 요청 필드 검증
- `phone_number`: `010-\d{4}-\d{4}` 패턴 (13자 고정)
- `callback_number`: `\d{2,4}-\d{3,4}-\d{4}` 또는 `\d{4}-\d{4}` 패턴 (9-13자)
- `message`: 최대 2000자
- `project_id`: UUID 형식
- `channel_id`: 정수형 (SMS=1)

#### 응답 형식
**성공 응답 (200)**:
```json
{
    "success": true,
    "message": "SMS 발송 성공",
    "data": {
        "group_id": 12345
    }
}
```

**에러 응답**:
```json
{
    "success": false,
    "message": "에러 메시지",
    "error_code": "ERROR_CODE"
}
```

### 2. MMS 발송 API

#### 엔드포인트
```
POST /message/mms
```

#### 요청 바디 (MMSRequest)
```json
{
    "recipients": [
        {
            "phone_number": "010-1234-5678",
            "member_code": "uuid-string",
            "message_id": null
        }
    ],
    "message": "전송할 MMS 메시지 내용",
    "subject": "MMS 제목",
    "callback_number": "02-1234-5678",
    "project_id": "uuid-string",
    "channel_id": 3,
    "img_url_list": [
        "https://example.com/image1.jpg",
        "https://example.com/image2.jpg"
    ]
}
```

#### 응답 형식
SMS와 동일한 응답 구조

### 3. 발송 이력 조회 API

#### 엔드포인트
```
GET /message/send_history/sms/{group_id}/messages
```

#### 응답 형식
```json
{
    "success": true,
    "data": [
        {
            "phone": "010-1234-5678",
            "name": "수신자명",
            "result": "성공",
            "reason": null
        }
    ]
}
```

## 벤더 연동

### 벤더 API 호출 구조

#### SMS 단건 발송
```
POST {MESSAGING_API}/api/send/sms
```
```json
{
    "vendor": "telnet",
    "phone_number": "010-1234-5678",
    "callback_number": "02-1234-5678",
    "member_code": "uuid-string",
    "message_id": "group-id",
    "message": "메시지 내용"
}
```

#### SMS 복수 발송
```
POST {MESSAGING_API}/api/send/sms/batch
```
```json
{
    "vendor": "telnet",
    "recipient_list": [
        {
            "phone_number": "010-1234-5678",
            "member_code": "uuid-string",
            "message_id": "group-id"
        }
    ],
    "callback_number": "02-1234-5678",
    "message": "메시지 내용"
}
```

#### MMS 발송
```
POST {MESSAGING_API}/api/send/mms
POST {MESSAGING_API}/api/send/mms/batch
```
SMS와 동일한 구조에 추가 필드:
```json
{
    "subject": "MMS 제목",
    "img_url_list": ["image_url1", "image_url2"]
}
```

### 지원 벤더
- **Telnet**: 기본 SMS/MMS 벤더
- **Uracle**: 대체 벤더 (향후 확장)

## 에러 처리

### HTTP 상태 코드
- `200`: 성공
- `400`: 잘못된 요청
- `422`: 유효성 검사 실패
- `500`: 서버 내부 오류
- `502`: 외부 벤더 API 오류

### 에러 코드 체계
- `BAD_REQUEST`: 잘못된 요청 파라미터
- `EXTERNAL_SERVER_ERROR`: 벤더 API 호출 실패
- `VALIDATION_ERROR`: 입력값 유효성 검사 실패

### 에러 응답 예시
```json
{
    "success": false,
    "message": "Vendor API 호출 실패: Connection timeout",
    "error_code": "EXTERNAL_SERVER_ERROR",
    "detail": [
        {
            "field": "phone_number",
            "reason": "잘못된 전화번호 형식"
        }
    ]
}
```

## 인증 및 권한

### JWT 인증
- Bearer 토큰 또는 쿠키 기반 인증
- 프로젝트별 격리된 접근 권한
- Account 모델과 연동된 사용자 인증

### 프로젝트 격리
- 모든 API 요청은 `project_id` 기반으로 격리
- 사용자는 소속 프로젝트의 리소스만 접근 가능
- 수신자(Recipient) 검증을 통한 추가 보안

## 비즈니스 로직

### 메시지 그룹 생성
1. 요청 타입에 따라 그룹명 결정 (단건/복수 발송)
2. 발신자 정보(Account ID) 저장
3. 메시지 채널 및 원본 메시지 데이터 저장

### 수신자 검증
1. `member_code`를 통한 Recipient 존재 여부 확인
2. 존재하지 않는 수신자는 실패 처리
3. 유효한 수신자만 벤더 API 호출에 포함

### 배치 처리
- `is_batch` 속성으로 단건/복수 발송 구분
- 복수 발송 시 배치 API 엔드포인트 사용
- 개별 메시지 상태 추적 가능

### 상태 관리
- 초기 상태: `0` (전송 중)
- 벤더 API 호출 성공 시: `1` (성공)
- 실패 시: `2` (실패) + 실패 사유 저장

## 확장 가능성

### 새로운 벤더 추가
- `Vendor` enum 확장
- 벤더별 payload 빌더 함수 구현
- 설정값 추가

### 메시지 타입 확장
- 새로운 MessageChannel 추가
- 요청 스키마 확장
- 벤더 API 엔드포인트 매핑

### 웹훅 지원
- 벤더로부터의 전송 결과 콜백 처리
- 실시간 상태 업데이트 지원

## MCP 서버 구축 고려사항

### 필수 구현 기능
1. SMS/MMS 발송 API 래핑
2. 발송 이력 조회 기능
3. 프로젝트별 인증 처리
4. 에러 처리 및 로깅

### 권장 추가 기능
1. 발송 통계 조회
2. 템플릿 기반 메시지 발송
3. 예약 발송 기능
4. 실시간 상태 조회

### 성능 고려사항
1. 대량 발송 시 배치 처리 활용
2. 데이터베이스 연결 풀 관리
3. 외부 API 호출 타임아웃 설정
4. 적절한 로깅 레벨 설정