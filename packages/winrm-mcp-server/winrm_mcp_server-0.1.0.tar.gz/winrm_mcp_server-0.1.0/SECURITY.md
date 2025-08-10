# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please send an email to the project maintainers. Please do not open a public issue for security vulnerabilities.

When reporting vulnerabilities, please include:

1. A description of the vulnerability
2. Steps to reproduce the issue
3. Potential impact of the vulnerability
4. Any suggested fixes or mitigations

We will respond to security reports within 48 hours and will provide regular updates as we work to address the issue.

## Security Considerations

This MCP server handles sensitive information including:

- Remote Windows machine credentials
- PowerShell command execution
- Network communications

### Built-in Security Features

- Credentials are never logged or exposed in output
- SSL/TLS encryption support for WinRM connections
- Input validation to prevent command injection
- Configurable SSL certificate verification
- Connection timeouts to prevent hanging connections

### Recommendations for Secure Usage

1. **Use HTTPS**: Always prefer HTTPS (port 5986) over HTTP (port 5985) for WinRM connections
2. **Enable SSL Verification**: Keep `WINRM_MCP_SKIP_SSL_VERIFICATION=false` unless absolutely necessary
3. **Secure Credentials**: Store credentials securely using environment variables or secure credential stores
4. **Network Security**: Ensure WinRM ports are only accessible from trusted networks
5. **Principle of Least Privilege**: Use accounts with minimal required permissions on target machines
6. **Regular Updates**: Keep the package and its dependencies updated

### Known Security Limitations

- Credentials must be provided as environment variables (consider using secure credential storage)
- Command execution happens with the privileges of the configured user account
- Network traffic may be logged by network infrastructure (use HTTPS to mitigate)
