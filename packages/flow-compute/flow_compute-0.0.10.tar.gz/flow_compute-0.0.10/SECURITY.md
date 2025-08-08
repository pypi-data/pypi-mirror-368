# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in Flow SDK, please report it by emailing security@mithril.ai

Please do not report security vulnerabilities through public GitHub issues.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Security Measures

Flow SDK implements several security measures:

- API keys are never logged or exposed
- SSH keys are generated securely and stored safely
- All network communications use encrypted channels
- Input validation prevents injection attacks