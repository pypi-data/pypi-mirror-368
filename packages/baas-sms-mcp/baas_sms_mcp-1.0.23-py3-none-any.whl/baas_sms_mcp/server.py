#!/usr/bin/env python3
"""
BaaS SMS/MMS MCP Server

Model Context Protocol server for SMS and MMS messaging services.
This server provides tools for generating code that directly calls BaaS API.
"""

import os
import httpx
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP

# Create the FastMCP instance for SMS/MMS messaging service
mcp = FastMCP("baas-mcp")

# Configuration
API_BASE_URL = "https://api.aiapp.link"  # Fixed BaaS API endpoint
BAAS_API_KEY = os.getenv("BAAS_API_KEY", "")

# HTTP client setup
client = httpx.AsyncClient(timeout=30.0)

@mcp.tool()
async def get_code_template_url(
    language: str,
    framework: Optional[str] = None,
    deployment_platform: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get URL for BaaS SMS/MMS integration code template from CDN
    
    Perfect for: Getting optimized, maintained code templates without token overhead
    
    Args:
        language: Programming language (javascript, python, php, java, go, csharp)
        framework: Optional framework (react, vue, django, laravel, fastapi, spring, etc.)
        deployment_platform: Optional platform (vercel, netlify, aws, docker, etc.)
    
    Returns:
        CDN URL to markdown file with complete code examples and integration guide
        Templates include direct API calls to https://api.aiapp.link with /api/message/ endpoints
    """
    try:
        language = language.lower()
        framework = framework.lower() if framework else None
        platform = deployment_platform.lower() if deployment_platform else None
        
        # CDN base URL with llms.txt optimization
        base_url = "https://cdn.mbaas.kr/templates/sms-mms"
        
        # Construct template path
        template_path = language
        if framework:
            template_path += f"/{framework}"
        else:
            template_path += "/vanilla"
        
        template_url = f"{base_url}/{template_path}.md"
        
        # Platform-specific integration guide
        integration_url = None
        if platform:
            integration_url = f"{base_url}/deployment/{platform}.md"
        
        # Supported combinations
        supported_languages = ["javascript", "python", "php", "java", "go", "csharp"]
        
        if language not in supported_languages:
            return {
                "success": False,
                "error": f"언어 '{language}'는 아직 지원되지 않습니다",
                "supported_languages": supported_languages,
                "error_code": "UNSUPPORTED_LANGUAGE"
            }
        
        return {
            "success": True,
            "language": language,
            "framework": framework,
            "deployment_platform": platform,
            "template_url": template_url,
            "integration_url": integration_url,
            "api_endpoint": "https://api.aiapp.link/api/message/",
            "cdn_info": {
                "cache_duration": "24시간",
                "last_updated": "자동 업데이트",
                "version": "latest"
            },
            "configuration": {
                "required_env_vars": ["BAAS_API_KEY"],
                "installation_guide": f"{base_url}/setup/{language}.md",
                "api_key_injected": bool(BAAS_API_KEY)
            },
            "message": f"{language} 템플릿 URL을 제공합니다. 토큰 최적화를 위해 CDN에서 직접 다운로드하세요."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"템플릿 URL 생성에 실패했습니다: {str(e)}",
            "error_code": "URL_GENERATION_ERROR"
        }


@mcp.tool()
async def generate_direct_api_code(
    language: str = "javascript",
    framework: Optional[str] = None,
    include_examples: bool = True
) -> Dict[str, Any]:
    """
    Generate code that directly calls BaaS API by fetching templates from CDN
    
    Perfect for: Production deployments, custom integrations, framework-specific implementations
    Token-optimized: Fetches maintained templates from CDN instead of generating locally
    
    Args:
        language: Programming language (javascript, python, php, java, go, csharp)
        framework: Optional framework (react, vue, django, laravel, fastapi, spring, etc.)
        include_examples: Include usage examples and configuration templates
        
    Returns:
        Dictionary with code fetched from CDN, filename, and integration instructions
        Code directly calls https://api.aiapp.link/api/message/ with X-API-KEY header authentication
        If MCP server has BAAS_API_KEY set, it will be automatically injected into code
    """
    try:
        language = language.lower()
        framework = framework.lower() if framework else None
        
        # CDN base URL for templates
        base_url = "https://cdn.mbaas.kr/templates/sms-mms"
        
        # Construct template path
        template_path = language
        if framework:
            template_path += f"/{framework}"
        else:
            template_path += "/vanilla"
        
        template_url = f"{base_url}/{template_path}.md"
        
        # Fetch template from CDN
        try:
            response = await client.get(template_url)
            if response.status_code == 200:
                template_content = response.text
                
                # Extract code from markdown (assuming code is in ```language blocks)
                import re
                code_blocks = re.findall(f'```{language}(.*?)```', template_content, re.DOTALL)
                
                if code_blocks:
                    code = code_blocks[0].strip()
                else:
                    # Fallback: use entire content if no code blocks found
                    code = template_content
                    
            else:
                return {
                    "success": False,
                    "error": f"CDN에서 템플릿을 가져올 수 없습니다 (HTTP {response.status_code})",
                    "cdn_url": template_url,
                    "error_code": "CDN_UNAVAILABLE"
                }
                    
        except Exception as cdn_error:
            return {
                "success": False,
                "error": f"CDN 연결 오류: {str(cdn_error)}",
                "cdn_url": template_url,
                "error_code": "CDN_CONNECTION_ERROR"
            }
        
        # Apply environment variable injection if API key is available
        if BAAS_API_KEY:
            code = code.replace('your-api-key', BAAS_API_KEY)
            code = code.replace('process.env.BAAS_API_KEY', f"'{BAAS_API_KEY}'")
            code = code.replace('os.getenv(\'BAAS_API_KEY\')', f"'{BAAS_API_KEY}'")
            code = code.replace('$_ENV[\'BAAS_API_KEY\']', f"'{BAAS_API_KEY}'")
        
        # File naming
        extensions = {
            "javascript": "js",
            "js": "js", 
            "python": "py",
            "py": "py",
            "php": "php"
        }
        
        extension = extensions.get(language, language)
        filename = f"baas-sms-service.{extension}"
        
        # Configuration instructions
        config_instructions = {
            "javascript": {
                "env_vars": ["BAAS_API_KEY"],
                "install": "npm install (dependencies included in template)",
                "usage": "Import and instantiate BaaSMessageService class",
                "api_key_injected": bool(BAAS_API_KEY)
            },
            "python": {
                "env_vars": ["BAAS_API_KEY"],
                "install": "pip install requests",
                "usage": "Import and instantiate BaaSMessageService class",
                "api_key_injected": bool(BAAS_API_KEY)
            },
            "php": {
                "env_vars": ["BAAS_API_KEY"],
                "install": "cURL extension required (usually included)",
                "usage": "Include file and instantiate BaaSMessageService class",
                "api_key_injected": bool(BAAS_API_KEY)
            }
        }
        
        return {
            "success": True,
            "language": language,
            "framework": framework,
            "code": code,
            "filename": filename,
            "description": f"{language.title()} BaaS SMS service for direct /api/message/ API calls",
            "source": "CDN template",
            "template_url": template_url,
            "configuration": config_instructions.get(language, {}),
            "api_endpoint": "https://api.aiapp.link/api/message/",
            "message": f"{language.title()} 코드가 성공적으로 생성되었습니다 (CDN 소스, API Key {'주입됨' if BAAS_API_KEY else '미설정'})"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"코드 생성에 실패했습니다: {str(e)}",
            "error_code": "CODE_GENERATION_ERROR"
        }

@mcp.tool()
async def create_message_service_template(
    project_config: Dict[str, str],
    language: str = "javascript",
    features: List[str] = None
) -> Dict[str, Any]:
    """
    Create a complete message service template by fetching from CDN and customizing with project config
    
    Perfect for: New project setup, team standardization, rapid prototyping
    Token-optimized: Fetches base template from CDN then applies project customizations
    
    Args:
        project_config: Project configuration {default_callback, company_name, etc.}
        language: Target programming language
        features: List of features to include ["sms", "mms", "status_check", "history", "validation"]
        
    Returns:
        Complete service template with project-specific defaults and configuration
        Automatically injects BAAS_API_KEY from MCP server environment if available
    """
    try:
        if features is None:
            features = ["sms", "mms", "status_check"]
        
        # Extract project configuration
        default_callback = project_config.get("default_callback", "02-1234-5678")
        company_name = project_config.get("company_name", "Your Company")
        
        # Fetch base template from CDN
        base_result = await generate_direct_api_code(language, None, True)
        
        if not base_result.get("success"):
            return base_result
        
        # Customize code with project config
        code = base_result["code"]
        
        # Replace placeholders with actual project values
        code = code.replace("02-1234-5678", default_callback)
        code = code.replace("Your Company", company_name)
        
        # Apply environment variable injection if API key is available
        if BAAS_API_KEY:
            code = code.replace('your-api-key', BAAS_API_KEY)
        
        # Fetch project-specific helpers from CDN
        try:
            helpers_url = f"https://cdn.mbaas.kr/templates/sms-mms/helpers/{language}-project.md"
            response = await client.get(helpers_url)
            
            if response.status_code == 200:
                helpers_template = response.text
                
                # Replace placeholders in helpers template
                helpers_code = helpers_template.replace("{{company_name}}", company_name)
                helpers_code = helpers_code.replace("{{default_callback}}", default_callback)
                
                # Apply environment variable injection
                if BAAS_API_KEY:
                    helpers_code = helpers_code.replace('your-api-key', BAAS_API_KEY)
                
                code += "\n\n" + helpers_code
                
        except Exception:
            # Fallback to basic project helpers if CDN unavailable
            if language == "javascript":
                project_helpers = f'''
// {company_name} Project-Specific Helpers
const PROJECT_CONFIG = {{
    DEFAULT_CALLBACK: '{default_callback}',
    COMPANY_NAME: '{company_name}'
}};

// Pre-configured service instance
const messageService = new BaaSMessageService(
    process.env.BAAS_API_KEY || '{BAAS_API_KEY if BAAS_API_KEY else "your-api-key"}'
);

// Helper functions for common use cases
async function sendVerificationSMS(phoneNumber, code, memberCode) {{
    return await messageService.sendSMS(
        [{{ phone_number: phoneNumber, member_code: memberCode }}],
        `[{company_name}] 인증번호: ${{code}}`,
        PROJECT_CONFIG.DEFAULT_CALLBACK
    );
}}

async function sendOrderConfirmation(phoneNumber, orderNumber, memberCode) {{
    return await messageService.sendSMS(
        [{{ phone_number: phoneNumber, member_code: memberCode }}],
        `[{company_name}] 주문이 완료되었습니다. 주문번호: ${{orderNumber}}`,
        PROJECT_CONFIG.DEFAULT_CALLBACK
    );
}}'''
                code += project_helpers
        
        return {
            "success": True,
            "project_config": project_config,
            "language": language,
            "features": features,
            "code": code,
            "filename": f"{company_name.lower().replace(' ', '_')}_message_service.{language}",
            "description": f"{company_name} 전용 메시지 서비스 템플릿",
            "source": "CDN template + project customization",
            "api_key_injected": bool(BAAS_API_KEY),
            "message": f"프로젝트별 맞춤 코드가 생성되었습니다 (CDN 최적화, API Key {'주입됨' if BAAS_API_KEY else '미설정'})"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"템플릿 생성에 실패했습니다: {str(e)}",
            "error_code": "TEMPLATE_GENERATION_ERROR"
        }

@mcp.tool()
async def get_integration_guide(
    platform: str,
    deployment_type: str = "production"
) -> Dict[str, Any]:
    """
    Get detailed integration guide by fetching from CDN for specific platforms and deployment scenarios
    
    Perfect for: DevOps setup, deployment planning, team onboarding
    Token-optimized: Fetches comprehensive guides from CDN instead of hardcoded responses
    
    Args:
        platform: Target platform (vercel, netlify, heroku, aws, gcp, azure, docker, etc.)
        deployment_type: Deployment type (development, staging, production)
        
    Returns:
        Step-by-step integration guide with platform-specific instructions fetched from CDN
        Updated for new /api/message/ endpoints and X-API-KEY authentication
    """
    try:
        platform = platform.lower()
        deployment_type = deployment_type.lower()
        
        # Try to fetch guide from CDN
        guide_url = f"https://cdn.mbaas.kr/templates/sms-mms/deployment/{platform}-{deployment_type}.md"
        
        try:
            response = await client.get(guide_url)
            if response.status_code == 200:
                guide_content = response.text
                
                return {
                    "success": True,
                    "platform": platform,
                    "deployment_type": deployment_type,
                    "guide_content": guide_content,
                    "source": "CDN",
                    "guide_url": guide_url,
                    "api_changes": {
                        "endpoints": "Updated to /api/message/sms and /api/message/mms",
                        "authentication": "X-API-KEY header only (no project_id needed)",
                        "breaking_changes": "Project ID parameter removed from API calls"
                    },
                    "security_checklist": [
                        "API 키를 코드에 하드코딩하지 않기",
                        "환경 변수 또는 시크릿 관리 서비스 사용",
                        "HTTPS 통신 확인",
                        "적절한 에러 로깅 설정"
                    ],
                    "message": f"{platform.title()} {deployment_type} 배포 가이드입니다 (CDN 최적화)"
                }
        except Exception:
            # Fallback to basic guides if CDN unavailable
            pass
        
        # Fallback guides with updated API information
        basic_guides = {
            "vercel": {
                "title": "Vercel 배포 가이드",
                "steps": [
                    "1. 환경 변수 설정: BAAS_API_KEY (PROJECT_ID 불필요)",
                    "2. vercel.json 설정에 환경 변수 추가",
                    "3. API Routes에서 /api/message/ 엔드포인트 사용",
                    "4. X-API-KEY 헤더로 인증 처리"
                ],
                "config": {
                    "env_vars": "Vercel Dashboard > Settings > Environment Variables",
                    "api_routes": "/api/send-sms.js 형태로 구현",
                    "endpoints": "/api/message/sms, /api/message/mms"
                }
            },
            "netlify": {
                "title": "Netlify Functions 가이드",
                "steps": [
                    "1. netlify/functions 디렉토리에 함수 생성",
                    "2. 환경 변수 BAAS_API_KEY를 Netlify 대시보드에서 설정",
                    "3. X-API-KEY 헤더로 인증하는 함수 구현",
                    "4. /api/message/ 엔드포인트 사용"
                ]
            },
            "docker": {
                "title": "Docker 컨테이너 배포",
                "steps": [
                    "1. Dockerfile에 필요한 의존성 설치",
                    "2. ENV BAAS_API_KEY로 환경 변수 설정",
                    "3. 또는 docker run -e BAAS_API_KEY 옵션 사용",
                    "4. 네트워크 접근성 확인 (api.aiapp.link/api/message/)"
                ]
            }
        }
        
        guide = basic_guides.get(platform)
        
        if not guide:
            return {
                "success": False,
                "error": f"플랫폼 '{platform}'에 대한 가이드가 아직 준비되지 않았습니다",
                "available_platforms": list(basic_guides.keys()),
                "cdn_url": f"https://cdn.mbaas.kr/templates/sms-mms/deployment/",
                "error_code": "PLATFORM_NOT_SUPPORTED"
            }
        
        # Add deployment-specific notes
        deployment_notes = {
            "development": "개발 환경에서는 .env 파일 사용 권장",
            "staging": "스테이징 환경에서는 별도 API 키 사용",
            "production": "프로덕션에서는 환경 변수 암호화 및 로깅 설정 필요"
        }
        
        return {
            "success": True,
            "platform": platform,
            "deployment_type": deployment_type,
            "guide": guide,
            "source": "Local fallback",
            "deployment_notes": deployment_notes.get(deployment_type, ""),
            "api_changes": {
                "endpoints": "Updated to /api/message/sms and /api/message/mms",
                "authentication": "X-API-KEY header only (no project_id needed)",
                "breaking_changes": "Project ID parameter removed from API calls"
            },
            "security_checklist": [
                "API 키를 코드에 하드코딩하지 않기",
                "환경 변수 또는 시크릿 관리 서비스 사용",
                "HTTPS 통신 확인",
                "적절한 에러 로깅 설정"
            ],
            "message": f"{platform.title()} {deployment_type} 배포 가이드입니다 (로컬 폴백)"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"가이드 조회에 실패했습니다: {str(e)}",
            "error_code": "GUIDE_RETRIEVAL_ERROR"
        }

# Cleanup function to close HTTP client
async def cleanup():
    await client.aclose()

def main():
    """BaaS SMS/MCP 서버의 메인 진입점"""
    print("BaaS SMS/MMS MCP 서버를 시작합니다...")
    print(f"API 기본 URL: {API_BASE_URL}")
    print(f"API 키: {'설정됨' if BAAS_API_KEY else '설정되지 않음'}")
    print("주요 변경사항:")
    print("- API 경로: /api/message/sms, /api/message/mms")
    print("- 인증: X-API-KEY 헤더만 사용 (PROJECT_ID 불필요)")
    print("- CDN 기반 템플릿 제공으로 토큰 최적화")
    
    try:
        mcp.run(transport="stdio")
    finally:
        import asyncio
        asyncio.run(cleanup())

# Run the server if the script is executed directly
if __name__ == "__main__":
    main()