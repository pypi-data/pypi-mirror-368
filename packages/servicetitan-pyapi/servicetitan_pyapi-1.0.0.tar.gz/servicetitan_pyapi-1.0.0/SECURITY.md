# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of ServiceTitan Python API Client seriously. If you discover a security vulnerability, please follow these steps:

### 🚨 For Security Issues
**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please:

1. **Email us directly** at: [security@n90-co.com] (replace with your actual security contact)
2. **Include the following information:**
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact assessment
   - Suggested fix (if you have one)

### ⏱️ Response Timeline
- **Acknowledgment**: We will acknowledge receipt within 48 hours
- **Initial Assessment**: We will provide an initial assessment within 5 business days
- **Resolution**: We aim to resolve critical issues within 30 days

### 🛡️ Security Best Practices for Users

#### Credential Management
- **Never commit credentials** to version control
- **Use environment variables** or secure credential stores
- **Rotate credentials regularly**
- **Use least-privilege access** for ServiceTitan API keys

#### Configuration Security
```python
# ❌ DON'T: Hardcode credentials
api = ServiceTitanAPI({
    "client_id": "your_actual_client_id",  # Never do this!
    "client_secret": "your_actual_secret"
})

# ✅ DO: Use secure configuration
api = ServiceTitanAPI("config/servicetitan_config.json")  # File not in repo
# or
api = ServiceTitanAPI()  # Uses environment variables
```

#### Network Security
- **Use HTTPS only** (enforced by default)
- **Validate SSL certificates** (default behavior)
- **Monitor API usage** for unusual patterns

### 🔐 Common Security Considerations

#### Data Handling
- **Sensitive Data**: Never log sensitive customer data
- **Data Retention**: Follow your organization's data retention policies
- **Data Transmission**: All data is transmitted over HTTPS

#### Authentication
- **Token Storage**: Tokens are stored in memory only
- **Token Expiry**: Automatic token refresh with configurable expiry buffer
- **Rate Limiting**: Respect ServiceTitan's rate limits

### 📋 Security Checklist for Contributors

When contributing code, ensure:

- [ ] No hardcoded credentials or sensitive data
- [ ] Proper error handling that doesn't leak information
- [ ] Input validation for user-provided data
- [ ] Secure defaults in configuration
- [ ] No logging of sensitive information
- [ ] Dependencies are up to date and secure

### 🔍 Vulnerability Scope

We are particularly interested in vulnerabilities related to:

- **Authentication bypass**
- **Credential leakage**
- **Code injection**
- **Data exposure**
- **Dependency vulnerabilities**

### 📞 Contact Information

For security-related questions or concerns:
- **Email**: [security@n90-co.com]
- **Response Time**: 48 hours for acknowledgment

Thank you for helping keep ServiceTitan Python API Client secure! 🔒
