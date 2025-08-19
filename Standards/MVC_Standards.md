# MVC Standards (2025, Enforced)

- **Separation of Concerns**: Controllers handle I/O & orchestration; Models contain data/business logic; Views render UI.
- **Testability**: Each layer is unit-testable; DB calls wrapped behind repository/services for mocking.
- **Async & Caching**: Use async I/O for network/DB work; cache hot reads where safe.
- **Boundaries**: Clear module ownership; denylist unsafe cross-module imports.
- **Front-end**: If SPA, adopt MVVM flavor (components = Views; stores/services = Models/Controllers).
