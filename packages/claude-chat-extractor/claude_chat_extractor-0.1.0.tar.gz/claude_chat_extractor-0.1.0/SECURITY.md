# Security Policy

## 🛡️ Supported Versions

We actively maintain and provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | ✅ Yes             |
| < 0.1   | ❌ No              |

## 🚨 Reporting a Vulnerability

We take security vulnerabilities seriously. If you believe you have found a security vulnerability, please report it to us as described below.

**Please do not report security vulnerabilities through public GitHub issues, discussions, or pull requests.**

### 🔒 How to Report

1. **Email Security Team**: Send an email to [INSERT_SECURITY_EMAIL] with the subject line `[SECURITY] Vulnerability Report`

2. **Include Details**: Please provide as much information as possible, including:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
   - Your contact information

3. **Response Timeline**: We will acknowledge receipt within 48 hours and provide a timeline for addressing the issue.

### 📋 What to Include

When reporting a vulnerability, please include:

- **Vulnerability Type**: (e.g., SQL injection, XSS, privilege escalation)
- **Affected Component**: Which part of the codebase is affected
- **Severity**: Your assessment of the vulnerability's impact
- **Proof of Concept**: Code or steps to demonstrate the issue
- **Environment**: OS, Python version, and any relevant configuration

### 🎯 Vulnerability Categories

We classify vulnerabilities by severity:

- **Critical**: Remote code execution, authentication bypass, data exposure
- **High**: Privilege escalation, data manipulation, denial of service
- **Medium**: Information disclosure, limited data access
- **Low**: Minor issues with limited impact

## 🔧 Security Measures

### Code Security

- All code changes undergo security review
- Dependencies are regularly updated for security patches
- Input validation and sanitization throughout the codebase
- Secure handling of file operations and JSON parsing

### Development Security

- No secrets or credentials in source code
- Environment variables for configuration
- Secure dependency management with UV
- Regular security audits of dependencies

### Testing Security

- Security-focused testing in CI/CD pipeline
- Fuzzing tests for input validation
- Memory safety testing for large file processing
- Cross-platform security validation

## 🚀 Security Updates

### Disclosure Process

1. **Private Fix**: Vulnerabilities are fixed in private branches
2. **Security Release**: Patched versions are released with security advisories
3. **Public Disclosure**: After users have had time to update, details are made public
4. **CVE Assignment**: Critical vulnerabilities receive CVE identifiers

### Update Timeline

- **Critical**: Immediate release (within 24-48 hours)
- **High**: Within 1 week
- **Medium**: Within 2 weeks
- **Low**: Within 1 month

## 🛠️ Security Best Practices

### For Users

- Keep the tool updated to the latest version
- Validate input files before processing
- Use the tool in isolated environments when processing untrusted data
- Monitor for security advisories

### For Contributors

- Follow secure coding practices
- Validate all inputs and outputs
- Use parameterized operations where applicable
- Avoid introducing new dependencies without security review

## 📚 Security Resources

- [Python Security Best Practices](https://docs.python.org/3/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Common Weakness Enumeration (CWE)](https://cwe.mitre.org/)

## 🤝 Acknowledgments

We appreciate security researchers and contributors who help us maintain the security of Claude Conversation Extractor. Responsible disclosure helps us protect all users of the tool.

## 📞 Contact

For security-related questions or to report vulnerabilities:

- **Security Email**: [INSERT_SECURITY_EMAIL]
- **PGP Key**: [INSERT_PGP_KEY_FINGERPRINT] (if applicable)
- **Response Time**: Within 48 hours for initial acknowledgment

---

**Note**: This security policy is a living document and will be updated as our security practices evolve. Please check back regularly for updates.
