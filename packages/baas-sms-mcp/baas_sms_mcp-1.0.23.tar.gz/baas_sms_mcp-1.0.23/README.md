# BaaS SMS/MMS MCP Server

[![npm version](https://badge.fury.io/js/baas-sms-mcp.svg)](https://badge.fury.io/js/baas-sms-mcp)
[![PyPI version](https://badge.fury.io/py/baas-sms-mcp.svg)](https://badge.fury.io/py/baas-sms-mcp)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Model Context Protocol server for SMS and MMS messaging services, designed to provide seamless integration with the BaaS platform through intelligent code generation and CDN-optimized templates.

## 🚀 Overview

This MCP server acts as a bridge between AI development workflows and the BaaS messaging platform, providing:

- **Intelligent Code Generation**: Generate production-ready code for SMS/MMS integration
- **CDN-Optimized Templates**: Fetch maintained, up-to-date code templates from CDN
- **Multi-Language & Framework Support**: JavaScript, Python, PHP with React, Vue, Django, Laravel, and more
- **Token Efficiency**: Minimize token usage through CDN-based template fetching
- **Environment Integration**: Automatic API key injection and environment variable management
- **Platform-Specific Guides**: Deployment and integration guides for major platforms

## 📋 Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Client (Claude, etc.)                │
└─────────────────────────┬───────────────────────────────────────┘
                          │ MCP Protocol
┌─────────────────────────▼───────────────────────────────────────┐
│                    Node.js Wrapper (index.js)                   │
│                   - Cross-platform compatibility                │
│                   - Dependency management                       │
│                   - Process lifecycle                          │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│               Python MCP Server (server.py)                     │
│                   - FastMCP framework                          │
│                   - CDN template fetching                      │
│                   - Code generation & customization            │
│                   - API key injection                          │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTPS
┌─────────────────────────▼───────────────────────────────────────┐
│                CDN Template Repository                          │
│                   - Language-specific templates                │
│                   - Framework integrations                     │
│                   - Deployment guides                          │
│                   - Project helpers                            │
└─────────────────────────────────────────────────────────────────┘
```

### Template Structure

```
templates/
├── javascript/
│   ├── vanilla.md          # Pure JavaScript implementation
│   └── react.md           # React component integration
├── python/
│   ├── vanilla.md          # Python requests-based
│   └── django.md          # Django integration
├── php/
│   └── vanilla.md          # PHP cURL implementation
├── helpers/
│   └── javascript-project.md  # Project-specific utilities
└── deployment/
    └── vercel-production.md    # Platform deployment guides
```

## 🛠 Installation & Setup

### npm Installation (Recommended)
```bash
npm install -g baas-sms-mcp
```

### Local Development Setup
```bash
git clone https://github.com/jjunmomo/BaaS-MCP.git
cd BaaS-MCP
npm install
```

### Python Dependencies
The server automatically manages Python dependencies, but you can install manually:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### MCP Client Configuration

Add to your MCP client configuration file:

```json
{
  "mcpServers": {
    "baas-sms-mcp": {
      "command": "npx",
      "args": ["baas-sms-mcp"],
      "env": {
        "BAAS_API_KEY": "your_actual_api_key_here"
      }
    }
  }
}
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BAAS_API_KEY` | Your BaaS platform API key | Yes* |

*Required for automatic API key injection into generated code. The server works without it but requires manual key configuration.

## 🔧 Available Tools

### 1. `get_code_template_url`
**Purpose**: Get CDN URLs for optimized code templates without token overhead

**Parameters:**
- `language` (string): Programming language 
  - Supported: `javascript`, `python`, `php`, `java`, `go`, `csharp`
- `framework` (optional): Framework name
  - JavaScript: `react`, `vue`, `angular`
  - Python: `django`, `fastapi`, `flask`
  - PHP: `laravel`, `symfony`
- `deployment_platform` (optional): Target platform
  - `vercel`, `netlify`, `aws`, `docker`, etc.

**Returns:**
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
**Purpose**: Generate production-ready code by fetching and customizing CDN templates

**Parameters:**
- `language` (string, default: "javascript"): Target programming language
- `framework` (optional): Framework-specific implementation
- `include_examples` (boolean, default: true): Include usage examples

**Returns:**
```json
{
  "success": true,
  "code": "// Complete implementation code...",
  "filename": "baas-sms-service.js",
  "description": "JavaScript BaaS SMS service for direct /api/message/ API calls",
  "source": "CDN template",
  "configuration": {
    "env_vars": ["BAAS_API_KEY"],
    "install": "npm install (dependencies included)",
    "api_key_injected": true
  }
}
```

### 3. `create_message_service_template`
**Purpose**: Create complete project-specific service templates with customization

**Parameters:**
- `project_config` (object): Project configuration
  ```json
  {
    "default_callback": "02-1234-5678",
    "company_name": "Your Company"
  }
  ```
- `language` (string): Target programming language
- `features` (array, optional): Features to include
  - Available: `["sms", "mms", "status_check", "history", "validation"]`

**Returns:**
```json
{
  "success": true,
  "code": "// Customized implementation with project defaults...",
  "filename": "your_company_message_service.js",
  "description": "Your Company 전용 메시지 서비스 템플릿",
  "source": "CDN template + project customization"
}
```

### 4. `get_integration_guide`
**Purpose**: Get detailed platform-specific deployment and integration guides

**Parameters:**
- `platform` (string): Target platform
  - Supported: `vercel`, `netlify`, `heroku`, `aws`, `gcp`, `azure`, `docker`
- `deployment_type` (string, default: "production"): Deployment environment
  - Options: `development`, `staging`, `production`

**Returns:**
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

## 🚨 Important API Changes

The BaaS platform has been updated with breaking changes:

### New API Structure
- **Base URL**: `https://api.aiapp.link`
- **SMS Endpoint**: `/api/message/sms`
- **MMS Endpoint**: `/api/message/mms`
- **Authentication**: `X-API-KEY` header only

### Breaking Changes
- ❌ `PROJECT_ID` parameter **removed** from all API calls
- ❌ Old endpoints deprecated
- ✅ Simplified authentication with API key only
- ✅ Updated response format

### Migration Guide
```javascript
// OLD (deprecated)
const response = await fetch('https://api.aiapp.link/message/sms', {
  headers: {
    'Authorization': `Bearer ${jwt_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    project_id: "uuid-string",
    // ... other params
  })
});

// NEW (current)
const response = await fetch('https://api.aiapp.link/api/message/sms', {
  headers: {
    'X-API-KEY': process.env.BAAS_API_KEY,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    // project_id removed
    // ... other params
  })
});
```

## 💡 Usage Examples

### Generate React SMS Component
```javascript
// Generate React component with TypeScript
const result = await mcp.generate_direct_api_code("javascript", "react", true);
console.log(result.code); // Complete React component
```

### Create Company-Specific Template
```javascript
const projectConfig = {
  default_callback: "02-1234-5678",
  company_name: "MyTech Corp"
};

const template = await mcp.create_message_service_template(
  projectConfig, 
  "python", 
  ["sms", "mms", "status_check"]
);

// Returns customized Python service class with company defaults
```

### Get Vercel Deployment Guide
```javascript
const guide = await mcp.get_integration_guide("vercel", "production");
console.log(guide.guide_content); // Complete deployment instructions
```

### Fetch Template URLs for Token Efficiency
```javascript
const urls = await mcp.get_code_template_url("python", "django", "heroku");
console.log(urls.template_url);     // CDN template URL
console.log(urls.integration_url);  // Platform-specific guide URL
```

## 🏗 Development

### Running Locally
```bash
# Start the MCP server
node index.js

# Test with environment variables
BAAS_API_KEY="test" node index.js
```

### Project Structure
```
BaaS-MCP/
├── index.js                 # Node.js wrapper & dependency management
├── baas_sms_mcp/
│   ├── __init__.py         # Python package initialization
│   └── server.py           # Main MCP server implementation
├── templates/              # Local template fallbacks
├── requirements.txt        # Python dependencies
├── package.json           # Node.js package configuration
├── pyproject.toml         # Python package configuration
└── mcp.config.json        # Example MCP configuration
```

### Release Process
```bash
# Patch version (bug fixes)
npm run release:patch

# Minor version (new features)
npm run release:minor

# Major version (breaking changes)
npm run release:major
```

## 🔒 Security Best Practices

### API Key Management
- Never hardcode API keys in source code
- Use environment variables or secret management services
- Rotate API keys regularly
- Monitor API key usage

### Deployment Security
- Enable HTTPS for all communications
- Validate input data thoroughly
- Implement proper error handling and logging
- Use least-privilege access principles

### Code Generation Security
- Templates are fetched from trusted CDN sources
- Automatic input sanitization
- No execution of generated code by the MCP server
- Clear separation between template and runtime environments

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and test thoroughly
4. Commit with clear messages: `git commit -m "Add new feature"`
5. Push to your fork: `git push origin feature/new-feature`
6. Create a Pull Request

## 📊 Performance & Monitoring

### Token Efficiency
- CDN-based templates reduce token usage by 60-80%
- Intelligent caching minimizes redundant API calls
- Optimized response formats for MCP protocol

### Monitoring
- Built-in error logging and reporting
- CDN performance monitoring
- API key usage tracking
- Template fetch success rates

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support & Community

- **GitHub Issues**: [Report bugs or request features](https://github.com/jjunmomo/BaaS-MCP/issues)
- **Email Support**: support@aiapp.link
- **Documentation**: [API Specification](SMS_MMS_API_Specification.md)
- **Korean Documentation**: [README.ko.md](README.ko.md)

## 🗺 Roadmap

### Upcoming Features
- [ ] Additional language support (Java, Go, C#)
- [ ] Advanced template customization options
- [ ] Real-time template updates
- [ ] Template version management
- [ ] Enhanced error reporting and debugging
- [ ] Integration with popular IDE extensions

### Version History
- **v1.0.18**: Current stable release with API updates
- **v1.0.0**: Initial stable release
- **v0.1.4**: Beta release with core functionality

---

> **Note**: This MCP server is optimized for external developer workflows and integrates seamlessly with AI-powered development environments. For the latest updates and comprehensive API documentation, visit our [GitHub repository](https://github.com/jjunmomo/BaaS-MCP).