# BaaS SMS/MMS MCP 서버

[![npm version](https://badge.fury.io/js/baas-sms-mcp.svg)](https://badge.fury.io/js/baas-sms-mcp)
[![PyPI version](https://badge.fury.io/py/baas-sms-mcp.svg)](https://badge.fury.io/py/baas-sms-mcp)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

지능형 코드 생성과 CDN 최적화 템플릿을 통해 BaaS 플랫폼과의 원활한 통합을 제공하는 SMS 및 MMS 메시징 서비스용 종합 모델 컨텍스트 프로토콜 서버입니다.

## 🚀 개요

이 MCP 서버는 AI 개발 워크플로우와 BaaS 메시징 플랫폼 사이의 브리지 역할을 하며 다음을 제공합니다:

- **지능형 코드 생성**: SMS/MMS 통합을 위한 프로덕션 준비 코드 생성
- **CDN 최적화 템플릿**: CDN에서 유지보수되는 최신 코드 템플릿 가져오기
- **다중 언어 및 프레임워크 지원**: React, Vue, Django, Laravel 등과 함께 JavaScript, Python, PHP
- **토큰 효율성**: CDN 기반 템플릿 가져오기를 통한 토큰 사용량 최소화
- **환경 통합**: 자동 API 키 주입 및 환경 변수 관리
- **플랫폼별 가이드**: 주요 플랫폼용 배포 및 통합 가이드

## 📋 아키텍처

### 시스템 구성요소

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP 클라이언트                                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │ MCP 프로토콜
┌─────────────────────────▼───────────────────────────────────────┐
│                    Node.js 래퍼 (index.js)                       │
│                   - 크로스 플랫폼 호환성                             │
│                   - 의존성 관리                                    │
│                   - 프로세스 라이프사이클                             │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                Python MCP 서버 (server.py)                       │
│                   - FastMCP 프레임워크                             │
│                   - CDN 템플릿 가져오기                             │
│                   - 코드 생성 및 커스터마이징                         │
│                   - API 키 주입                                   │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTPS
┌─────────────────────────▼───────────────────────────────────────┐
│                   CDN 템플릿 저장소                                │
│                   - 언어별 템플릿                                  │
│                   - 프레임워크 통합                                 │
│                   - 배포 가이드                                   │
│                   - 프로젝트 헬퍼                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 템플릿 구조

```
templates/
├── javascript/
│   ├── vanilla.md          # 순수 JavaScript 구현
│   └── react.md           # React 컴포넌트 통합
├── python/
│   ├── vanilla.md          # Python requests 기반
│   └── django.md          # Django 통합
├── php/
│   └── vanilla.md          # PHP cURL 구현
├── helpers/
│   └── javascript-project.md  # 프로젝트별 유틸리티
└── deployment/
    └── vercel-production.md    # 플랫폼 배포 가이드
```

## 🛠 설치 및 설정

### npm 설치 (권장)
```bash
npm install -g baas-sms-mcp
```

### 로컬 개발 설정
```bash
git clone https://github.com/jjunmomo/BaaS-MCP.git
cd BaaS-MCP
npm install
```

### Python 의존성
서버가 Python 의존성을 자동으로 관리하지만, 수동으로 설치할 수도 있습니다:
```bash
pip install -r requirements.txt
```

## ⚙️ 구성

### MCP 클라이언트 설정

MCP 클라이언트 구성 파일에 추가:

```json
{
  "mcpServers": {
    "baas-sms-mcp": {
      "command": "npx",
      "args": ["baas-sms-mcp"],
      "env": {
        "BAAS_API_KEY": "실제_API_키를_여기에_입력하세요"
      }
    }
  }
}
```

### 환경 변수

| 변수 | 설명 | 필수 |
|------|------|------|
| `BAAS_API_KEY` | BaaS 플랫폼 API 키 | 예* |

*생성된 코드에 자동 API 키 주입을 위해 필요합니다. 없어도 서버는 작동하지만 수동 키 구성이 필요합니다.

## 🔧 사용 가능한 도구

### 1. `get_code_template_url`
**목적**: 토큰 오버헤드 없이 최적화된 코드 템플릿용 CDN URL 가져오기

**매개변수:**
- `language` (문자열): 프로그래밍 언어
  - 지원: `javascript`, `python`, `php`, `java`, `go`, `csharp`
- `framework` (선택사항): 프레임워크 이름
  - JavaScript: `react`, `vue`, `angular`
  - Python: `django`, `fastapi`, `flask`
  - PHP: `laravel`, `symfony`
- `deployment_platform` (선택사항): 대상 플랫폼
  - `vercel`, `netlify`, `aws`, `docker` 등

**반환값:**
```json
{
  "success": true,
  "template_url": "https://cdn.mbaas.kr/templates/sms-mms/javascript/react.md",
  "integration_url": "https://cdn.mbaas.kr/templates/sms-mms/deployment/vercel.md",
  "api_endpoint": "https://api.aiapp.link/api/message/",
  "configuration": {
    "required_env_vars": ["BAAS_API_KEY"],
    "api_key_injected": true
  }
}
```

### 2. `generate_direct_api_code`
**목적**: CDN 템플릿을 가져와 커스터마이징하여 프로덕션 준비 코드 생성

**매개변수:**
- `language` (문자열, 기본값: "javascript"): 대상 프로그래밍 언어
- `framework` (선택사항): 프레임워크별 구현
- `include_examples` (불린, 기본값: true): 사용 예제 포함

**반환값:**
```json
{
  "success": true,
  "code": "// 완전한 구현 코드...",
  "filename": "baas-sms-service.js",
  "description": "직접 /api/message/ API 호출을 위한 JavaScript BaaS SMS 서비스",
  "source": "CDN 템플릿",
  "configuration": {
    "env_vars": ["BAAS_API_KEY"],
    "install": "npm install (종속성 포함)",
    "api_key_injected": true
  }
}
```

### 3. `create_message_service_template`
**목적**: 커스터마이징을 통한 완전한 프로젝트별 서비스 템플릿 생성

**매개변수:**
- `project_config` (객체): 프로젝트 구성
  ```json
  {
    "default_callback": "02-1234-5678",
    "company_name": "귀하의 회사"
  }
  ```
- `language` (문자열): 대상 프로그래밍 언어
- `features` (배열, 선택사항): 포함할 기능
  - 사용 가능: `["sms", "mms", "status_check", "history", "validation"]`

**반환값:**
```json
{
  "success": true,
  "code": "// 프로젝트 기본값이 포함된 커스터마이즈된 구현...",
  "filename": "귀하의_회사_메시지_서비스.js",
  "description": "귀하의 회사 전용 메시지 서비스 템플릿",
  "source": "CDN 템플릿 + 프로젝트 커스터마이징"
}
```

### 4. `get_integration_guide`
**목적**: 상세한 플랫폼별 배포 및 통합 가이드 가져오기

**매개변수:**
- `platform` (문자열): 대상 플랫폼
  - 지원: `vercel`, `netlify`, `heroku`, `aws`, `gcp`, `azure`, `docker`
- `deployment_type` (문자열, 기본값: "production"): 배포 환경
  - 옵션: `development`, `staging`, `production`

**반환값:**
```json
{
  "success": true,
  "platform": "vercel",
  "deployment_type": "production",
  "guide_content": "# Vercel 배포 가이드\n...",
  "security_checklist": [
    "API 키를 코드에 하드코딩하지 않기",
    "환경 변수 또는 시크릿 관리 서비스 사용",
    "HTTPS 통신 확인",
    "적절한 에러 로깅 설정"
  ]
}
```

## 🚨 중요한 API 변경사항

BaaS 플랫폼이 주요 변경사항으로 업데이트되었습니다:

### 새로운 API 구조
- **베이스 URL**: `https://api.aiapp.link`
- **SMS 엔드포인트**: `/api/message/sms`
- **MMS 엔드포인트**: `/api/message/mms`
- **인증**: `X-API-KEY` 헤더만 사용

### 주요 변경사항
- ❌ 모든 API 호출에서 `PROJECT_ID` 매개변수 **제거됨**
- ❌ 이전 엔드포인트 사용 중단
- ✅ API 키만으로 간소화된 인증
- ✅ 업데이트된 응답 형식

### 마이그레이션 가이드
```javascript
// 이전 (사용 중단)
const response = await fetch('https://api.aiapp.link/message/sms', {
  headers: {
    'Authorization': `Bearer ${jwt_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    project_id: "uuid-string",
    // ... 기타 매개변수
  })
});

// 현재 (신규)
const response = await fetch('https://api.aiapp.link/api/message/sms', {
  headers: {
    'X-API-KEY': process.env.BAAS_API_KEY,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    // project_id 제거됨
    // ... 기타 매개변수
  })
});
```

## 💡 사용 예제

### React SMS 컴포넌트 생성
```javascript
// TypeScript와 함께 React 컴포넌트 생성
const result = await mcp.generate_direct_api_code("javascript", "react", true);
console.log(result.code); // 완전한 React 컴포넌트
```

### 회사별 템플릿 생성
```javascript
const projectConfig = {
  default_callback: "02-1234-5678",
  company_name: "마이테크 코퍼레이션"
};

const template = await mcp.create_message_service_template(
  projectConfig, 
  "python", 
  ["sms", "mms", "status_check"]
);

// 회사 기본값이 포함된 커스터마이즈된 Python 서비스 클래스 반환
```

### Vercel 배포 가이드 가져오기
```javascript
const guide = await mcp.get_integration_guide("vercel", "production");
console.log(guide.guide_content); // 완전한 배포 지침
```

### 토큰 효율성을 위한 템플릿 URL 가져오기
```javascript
const urls = await mcp.get_code_template_url("python", "django", "heroku");
console.log(urls.template_url);     // CDN 템플릿 URL
console.log(urls.integration_url);  // 플랫폼별 가이드 URL
```

## 🏗 개발

### 로컬에서 실행
```bash
# MCP 서버 시작
node index.js

# 환경 변수와 함께 테스트
BAAS_API_KEY="test" node index.js
```

### 프로젝트 구조
```
BaaS-MCP/
├── index.js                 # Node.js 래퍼 및 의존성 관리
├── baas_sms_mcp/
│   ├── __init__.py         # Python 패키지 초기화
│   └── server.py           # 메인 MCP 서버 구현
├── templates/              # 로컬 템플릿 폴백
├── requirements.txt        # Python 의존성
├── package.json           # Node.js 패키지 구성
├── pyproject.toml         # Python 패키지 구성
└── mcp.config.json        # 예제 MCP 구성
```

### 릴리즈 프로세스
```bash
# 패치 버전 (버그 수정)
npm run release:patch

# 마이너 버전 (새 기능)
npm run release:minor

# 메이저 버전 (주요 변경)
npm run release:major
```

## 🔒 보안 모범 사례

### API 키 관리
- 소스 코드에 API 키를 하드코딩하지 말 것
- 환경 변수 또는 시크릿 관리 서비스 사용
- API 키를 정기적으로 교체
- API 키 사용량 모니터링

### 배포 보안
- 모든 통신에 HTTPS 활성화
- 입력 데이터를 철저히 검증
- 적절한 에러 처리 및 로깅 구현
- 최소 권한 접근 원칙 사용

### 코드 생성 보안
- 신뢰할 수 있는 CDN 소스에서 템플릿 가져오기
- 자동 입력 정화
- MCP 서버에서 생성된 코드 실행하지 않음
- 템플릿과 런타임 환경 간의 명확한 분리

## 🤝 기여하기

1. 저장소 포크
2. 기능 브랜치 생성: `git checkout -b feature/new-feature`
3. 변경사항을 만들고 철저히 테스트
4. 명확한 메시지로 커밋: `git commit -m "새 기능 추가"`
5. 포크에 푸시: `git push origin feature/new-feature`
6. Pull Request 생성

## 📊 성능 및 모니터링

### 토큰 효율성
- CDN 기반 템플릿으로 토큰 사용량 60-80% 감소
- 지능형 캐싱으로 중복 API 호출 최소화
- MCP 프로토콜용 최적화된 응답 형식

### 모니터링
- 내장 에러 로깅 및 보고
- CDN 성능 모니터링
- API 키 사용량 추적
- 템플릿 가져오기 성공률

## 📄 라이선스

MIT 라이선스 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🆘 지원 및 커뮤니티

- **GitHub 이슈**: [버그 신고 또는 기능 요청](https://github.com/jjunmomo/BaaS-MCP/issues)
- **이메일 지원**: support@aiapp.link
- **문서**: [API 명세서](SMS_MMS_API_Specification.md)
- **영어 문서**: [README.md](README.eng.md)

## 🗺 로드맵

### 예정된 기능
- [ ] 추가 언어 지원 (Java, Go, C#)
- [ ] 고급 템플릿 커스터마이징 옵션
- [ ] 실시간 템플릿 업데이트
- [ ] 템플릿 버전 관리
- [ ] 향상된 에러 보고 및 디버깅
- [ ] 인기 IDE 확장 프로그램과의 통합

### 버전 히스토리
- **v1.0.18**: API 업데이트가 포함된 현재 안정 릴리즈
- **v1.0.0**: 초기 안정 릴리즈
- **v0.1.4**: 핵심 기능이 포함된 베타 릴리즈

---

> **참고**: 이 MCP 서버는 외부 개발자 워크플로우에 최적화되어 있으며 AI 기반 개발 환경과 원활하게 통합됩니다. 최신 업데이트와 포괄적인 API 문서는 [GitHub 저장소](https://github.com/jjunmomo/BaaS-MCP)를 참조하세요.