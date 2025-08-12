# Security Policy

## Overview

The XML Analysis Framework is designed with security as a top priority. We use **defusedxml** to protect against common XML vulnerabilities and follow security best practices throughout the codebase.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.2.x   | :white_check_mark: |
| 1.1.x   | :x:                |
| < 1.1   | :x:                |

## Security Features

### 1. Protected Against XML Attacks

The framework automatically protects against:

- **XXE (XML External Entity) Injection**
  - Prevents reading local files via entity references
  - Blocks SSRF attacks through external entity resolution
  - Disables DTD processing by default

- **Billion Laughs / XML Bomb**
  - Prevents exponential entity expansion attacks
  - Protects against memory exhaustion DoS attacks
  - Limits entity expansion depth

- **External DTD Retrieval**
  - Blocks fetching of external DTDs
  - Prevents data exfiltration through DTD requests
  - Eliminates network-based attack vectors

### 2. Safe Parsing Implementation

All XML parsing in the framework uses defusedxml:

```python
# Safe - uses defusedxml
# ET import removed - not used in this handler
tree = ET.parse(file_path)

# NEVER use standard library directly
# import xml.etree.ElementTree as ET  # UNSAFE!
```

### 3. Security Exception Handling

The framework gracefully handles security exceptions:

```python
{
    "error": "XML parsing blocked for security: EntitiesForbidden - ...",
    "file_path": "malicious.xml",
    "security_issue": true
}
```

## Security Best Practices

### For Framework Users

1. **File Size Validation**
   ```python
   def validate_file_size(file_path, max_mb=100):
       size_mb = os.path.getsize(file_path) / (1024 * 1024)
       if size_mb > max_mb:
           raise ValueError(f"File too large: {size_mb}MB")
   ```

2. **Path Validation**
   ```python
   import os
   
   def validate_file_path(file_path):
       # Resolve to absolute path
       abs_path = os.path.abspath(file_path)
       
       # Ensure file exists and is readable
       if not os.path.exists(abs_path):
           raise FileNotFoundError(f"File not found: {abs_path}")
       
       # Ensure it's a file, not a directory
       if not os.path.isfile(abs_path):
           raise ValueError(f"Not a file: {abs_path}")
       
       return abs_path
   ```

3. **Input Sanitization**
   - Always validate and sanitize file paths
   - Implement rate limiting for analysis requests
   - Log security events for monitoring

### For Framework Contributors

1. **Never Import Standard XML Libraries Directly**
   - Always use `defusedxml` imports
   - Maintain TYPE_CHECKING blocks for type hints

2. **Security Testing**
   - Test new handlers with malicious XML samples
   - Verify protection against XXE and billion laughs
   - Ensure graceful error handling

3. **Dependency Management**
   - Keep defusedxml updated to latest version
   - Monitor security advisories
   - Minimize additional dependencies

## Reporting Security Vulnerabilities

If you discover a security vulnerability, please:

1. **DO NOT** create a public issue
2. Email security details to: wjackson@redhat.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

We will acknowledge receipt within 48 hours and provide a detailed response within 5 business days.

## Security Checklist for Deployments

- [ ] Implement file size limits appropriate for your use case
- [ ] Validate all file paths before processing
- [ ] Set up monitoring for security exceptions
- [ ] Keep the framework and defusedxml updated
- [ ] Review and restrict file system access permissions
- [ ] Implement rate limiting for API endpoints
- [ ] Log all security events for audit trails
- [ ] Regular security scans of processed XML files

## Testing Security

Test the framework's security with these examples:

```python
# Test XXE Protection
xxe_test = '''<?xml version="1.0"?>
<!DOCTYPE root [
<!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>&xxe;</root>'''

# Test Billion Laughs Protection  
bomb_test = '''<?xml version="1.0"?>
<!DOCTYPE lolz [
<!ENTITY lol "lol">
<!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
]>
<lolz>&lol2;</lolz>'''

# Both should be safely rejected
analyzer = XMLDocumentAnalyzer()
result = analyzer.analyze_document("malicious.xml")
assert result.get('security_issue') == True
```

## Security Updates

Stay informed about security updates:

- Watch the [GitHub repository](https://github.com/redhat-ai-americas/xml-analysis-framework)
- Monitor [defusedxml security advisories](https://github.com/tiran/defusedxml)
- Review release notes for security fixes

## Compliance

This framework's security measures help with compliance for:

- **OWASP Top 10** - A05:2021 Security Misconfiguration
- **CWE-611** - Improper Restriction of XML External Entity Reference
- **CWE-776** - Improper Restriction of Recursive Entity References