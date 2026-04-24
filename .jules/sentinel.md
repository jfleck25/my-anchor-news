## 2026-04-24 - Fix Insecure Transport Allowed for OAuth
**Vulnerability:** Setting `OAUTHLIB_INSECURE_TRANSPORT="1"` globally based solely on `FLASK_ENV != 'production'` risks unintentionally enabling insecure OAuth transport in intermediate environments (like staging or CI/CD test suites).
**Learning:** Security-degrading developer conveniences must be strictly opt-in using explicitly named feature flags, rather than relying on broad environment negations.
**Prevention:** Require specific override environment variables (e.g., `ALLOW_INSECURE_OAUTH=1`) for local development conveniences that weaken security, and explicitly unset dangerous flags if the override is not provided.
