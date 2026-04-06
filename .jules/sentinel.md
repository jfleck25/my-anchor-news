## 2024-05-30 - Fix overly permissive CORS configuration
**Vulnerability:** The application defaulted to allowing all origins (`CORS(app)`) when the `ALLOWED_ORIGINS` environment variable was missing, enabling any site to interact with the backend API.
**Learning:** Defaulting to a wide-open CORS configuration (`*`) when an environment variable isn't present introduces a significant Cross-Origin Resource Sharing vulnerability, especially dangerous given that the API handles authenticated requests.
**Prevention:** Always default to restrictive (e.g., empty or localhost-only) origins if external configuration is absent, explicitly enabling permissive rules only when expressly specified via configuration, and configure different logic for development and production environments.
## 2026-04-06 - Permissive Default CORS Origins

**Vulnerability:** Permissive Default CORS Origins
**Learning:** Hardcoded permissive local addresses (like `http://localhost:3000`, `http://127.0.0.1:3000`) for `ALLOWED_ORIGINS` in development environments are potentially dangerous as they can leave instances unintentionally permissive if not properly managed or if development configurations leak into production.
**Prevention:** Remove hardcoded permissive local addresses and fall back to an empty list `[]` for CORS origins across all environments if `ALLOWED_ORIGINS` is not defined. Ensure that local development origins are only enabled by explicit manual configuration via the `ALLOWED_ORIGINS` environment variable, while logging a warning if it's missing in non-production environments to aid developers.
