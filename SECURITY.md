# Security Policy

## Supported versions

Security fixes are considered for the default branch while the project is actively developed.

## Reporting a vulnerability

Do not open a public issue for secrets, authentication problems, or exploitable vulnerabilities. Contact the repository owner privately through GitHub with a clear description, affected path, reproduction steps, and potential impact.

Never include credentials or personal data in a report.

## Security expectations

- Keep API keys in local environment variables.
- Do not commit `.env` files or credentials.
- Validate untrusted data before processing.
- Treat external data and model outputs as untrusted.
- Review third-party dependencies and data terms before deployment.
