# Security Standards (2025, Enforced)

- **Secrets**: Only via environment variables or secrets managers (GitHub Secrets, cloud Key Vault). Never commit secrets.
- **AuthN/Z**: Use well-known frameworks; enforce RBAC for admin features.
- **Transport**: HTTPS only; HSTS recommended.
- **Data**: Encrypt sensitive data at rest where applicable; hash passwords (argon2/bcrypt).
- **OWASP/AI**: Guard against injection, XSS/CSRF, SSRF, prompt injection; sanitize model inputs/outputs.
- **Supply Chain**: Pin dependencies; run SCA/Container scans in CI.
