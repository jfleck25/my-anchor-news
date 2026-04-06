## 2024-05-30 - Fix overly permissive CORS configuration
**Vulnerability:** The application defaulted to allowing all origins (`CORS(app)`) when the `ALLOWED_ORIGINS` environment variable was missing, enabling any site to interact with the backend API.
**Learning:** Defaulting to a wide-open CORS configuration (`*`) when an environment variable isn't present introduces a significant Cross-Origin Resource Sharing vulnerability, especially dangerous given that the API handles authenticated requests.
**Prevention:** Always default to restrictive (e.g., empty or localhost-only) origins if external configuration is absent, explicitly enabling permissive rules only when expressly specified via configuration, and configure different logic for development and production environments.
## 2024-06-05 - Raw Error Traceback Exposure in /login Route
**Vulnerability:** Returning raw exception strings (`str(e)`) in HTTP error responses (specifically in the `/login` route) can inadvertently expose sensitive variable states, internal paths, or OAuth configuration data to an attacker or end-user.
**Learning:** Error handlers should always decouple internal system errors from user-facing messages. Raw exception outputs are useful for debugging but represent an information disclosure risk in production endpoints.
**Prevention:** Always use generic error messages (e.g., "Login failed. Please try again.") and ensure detail fields are set to `None` or safely truncated in both global and route-specific error handlers.
