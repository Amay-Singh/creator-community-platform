# Coding Standards (2025, Enforced)

- **Readability**: Self-documenting names; functions < 50 lines; classes < 200 lines; complex logic commented.
- **Reusability**: Shared utilities for logging, auth, and DB access; avoid duplication (DRY).
- **Performance**: Profile critical paths; prefer O(n) over O(n^2); cache read-heavy queries.
- **Low Code**: Use framework features (ORM, routers) before custom code.
- **Testing**: Every feature ships with **unit + integration** tests and coverage snapshot.
- **Tooling**: Linting + formatting enforced in CI; fail the build on violations.
- **Security**: No secrets in code; read from env; respect principle of least privilege.
