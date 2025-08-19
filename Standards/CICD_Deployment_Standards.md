# CI/CD & Deployment Standards (2025, Enforced)

- **Branching**: `develop` → UAT auto-deploy; `main` → PROD with manual approval; `uat` protected if used.
- **Pipelines**: Lint → Unit → Integration → Build → Artifact → Deploy; cache dependencies.
- **Environments**: Separate UAT/PROD with distinct DB URLs and secrets.
- **Zero-Downtime**: Prefer blue/green or rolling when possible.
- **Observability**: Emit logs/metrics; surface URLs and run IDs in outputs.
- **Security**: SAST/SCA/Container scans as pipeline steps; block on critical findings.
