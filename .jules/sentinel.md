## 2024-05-30 - Fix overly permissive CORS configuration
**Vulnerability:** The application defaulted to allowing all origins (`CORS(app)`) when the `ALLOWED_ORIGINS` environment variable was missing, enabling any site to interact with the backend API.
**Learning:** Defaulting to a wide-open CORS configuration (`*`) when an environment variable isn't present introduces a significant Cross-Origin Resource Sharing vulnerability, especially dangerous given that the API handles authenticated requests.
**Prevention:** Always default to restrictive (e.g., empty or localhost-only) origins if external configuration is absent, explicitly enabling permissive rules only when expressly specified via configuration, and configure different logic for development and production environments.
## 2024-06-05 - Raw Error Traceback Exposure in /login Route
**Vulnerability:** Returning raw exception strings (`str(e)`) in HTTP error responses (specifically in the `/login` route) can inadvertently expose sensitive variable states, internal paths, or OAuth configuration data to an attacker or end-user.
**Learning:** Error handlers should always decouple internal system errors from user-facing messages. Raw exception outputs are useful for debugging but represent an information disclosure risk in production endpoints.
**Prevention:** Always use generic error messages (e.g., "Login failed. Please try again.") and ensure detail fields are set to `None` or safely truncated in both global and route-specific error handlers.
## 2026-04-06 - Permissive Default CORS Origins

**Vulnerability:** Permissive Default CORS Origins
**Learning:** Hardcoded permissive local addresses (like `http://localhost:3000`, `http://127.0.0.1:3000`) for `ALLOWED_ORIGINS` in development environments are potentially dangerous as they can leave instances unintentionally permissive if not properly managed or if development configurations leak into production.
**Prevention:** Remove hardcoded permissive local addresses and fall back to an empty list `[]` for CORS origins across all environments if `ALLOWED_ORIGINS` is not defined. Ensure that local development origins are only enabled by explicit manual configuration via the `ALLOWED_ORIGINS` environment variable, while logging a warning if it's missing in non-production environments to aid developers.
## 2025-04-06 - Insufficient Data Validation in Share Endpoint

**Vulnerability:** The `/api/share` endpoint was accepting arbitrary JSON payloads via `request.get_json()` and directly serializing them into PostgreSQL using `json.dumps()` without any schema or type validation. This could allow attackers to store malformed data or cause storage exhaustion by submitting oversized or incorrectly structured payloads.

**Learning:** Missing schema validation on incoming JSON data exposes the application to data integrity issues and potential denial-of-service (storage exhaustion) if attackers submit massive or unexpected structures. Validating the core structure limits the attack surface and ensures expected downstream parsing.

**Prevention:** Always perform type validation (e.g., `isinstance(data, dict)`) and key presence verification (`'expected_key' in data`) for endpoints accepting JSON data before processing or storing it.

## 2024-06-03 - Prevent XSS in manual HTML string concatenation for PDF generation
**Vulnerability:** The frontend application manually concatenated unescaped JSON properties from an LLM response (based on email contents) into an HTML string for PDF generation, which was then loaded into a new window.
**Learning:** Even when the data displayed in the UI is safely rendered (e.g., by React), secondary outputs like printable PDFs or exported documents constructed via manual string concatenation (`html += ...`) bypass these safety mechanisms. When the data originates from an LLM processing untrusted external input (like emails), this creates a severe XSS vector where prompt injection can lead to script execution in the context of the application's origin (via `window.open`).
**Prevention:** Always sanitize or HTML-escape dynamic data before concatenating it into raw HTML strings, regardless of whether the primary UI rendering mechanism is considered safe. Do not trust LLM output to be benign, especially when it digests arbitrary external data.
## 2024-04-07 - Insufficient Data Validation in Share Endpoint
**Vulnerability:** The `/api/share` endpoint accepted arbitrarily large or malicious JSON dictionaries containing unvalidated keys and inserted them directly into PostgreSQL. This could lead to database bloat or unexpected downstream parsing issues.
**Learning:** Checking for the presence of required keys is not the same as ensuring *only* those keys are present. An attacker can append extra arbitrary data if the input is not strictly filtered.
**Prevention:** Always validate and filter user-provided JSON structures to an explicit allowlist of known keys before serialization and storage.

## 2025-04-06 - Insufficient Data Validation in Share Endpoint

**Vulnerability:** The `/api/share` endpoint failed to enforce a strict schema on the incoming JSON payload before storing it in the `shared_briefings` PostgreSQL table. It only checked that the expected keys (`story_groups` or `remaining_stories`) existed somewhere in the JSON payload, leaving it vulnerable to mass assignment or abusive storage if an attacker injected arbitrary, large, or malicious keys into the JSON payload alongside the expected ones.

**Learning:** When interacting with schemaless database fields like JSONB or when directly dumping JSON objects, it's not enough to just verify the presence of required keys. Explicitly constructing a new dictionary with only the expected keys prevents uncontrolled data inclusion and reduces the attack surface.

**Prevention:** Always sanitize input by plucking only the explicitly allowed fields from user-provided objects rather than inserting the entire object directly into the database, even if some initial validation passed.

## 2026-04-07 - Mass Assignment Vulnerability in Settings Endpoint

**Vulnerability:** The `/api/settings` endpoint was previously accepting arbitrary JSON payloads via `request.get_json()` and passing them directly to `save_settings()`. This resulted in a mass assignment vulnerability where attackers could supply extraneous or large data payloads (e.g., `"malicious_key": "some_bad_data"`, `"huge_payload": "..."`), which were then blindly serialized and stored in PostgreSQL or the settings file.

**Learning:** When APIs accept JSON data for update operations, directly saving the entire raw payload exposes the application to mass assignment. Attackers could bloat the database, overwrite unintended fields, or store configurations outside expected parameters.

**Prevention:** To prevent mass assignment, always enforce a strict schema on incoming JSON payloads. Before saving or processing updates, explicitly extract only the allowed, expected keys into a new, sanitized dictionary rather than trusting the raw user input.
## 2025-04-06 - Cross-Tenant Data Leak in Ephemeral Cache

**Vulnerability:** The application used an ephemeral, file-based cache (`cache.json`) to store generated email briefings (`cache['analysis']`) and synthesized audio (`cache['audio']`). However, the cache was global and only keyed by the user's `settings_hash` and the audio's `script_hash`. If two distinct users shared the same settings configuration (e.g., the default settings), a subsequent user could hit the cache and receive the private, sensitive email analysis or generated audio of the previous user.
**Learning:** Storing private data in a global cache that is only keyed by configuration parameters (like settings hashes) instead of explicit user identifiers creates a severe Cross-Tenant Data Leak (Information Disclosure) vulnerability.
**Prevention:** Always partition or scope cached data using a strong, unique user identifier (e.g., `user_id` or `email`) to ensure that one tenant's sensitive information is completely isolated and inaccessible to another, even if they share identical application states or configurations.

## 2024-06-06 - Denial of Service via Missing Payload Limit
**Vulnerability:** The application accepted unconstrained incoming JSON payloads without imposing a `MAX_CONTENT_LENGTH` on the Flask configuration.
**Learning:** Without setting a global upper bound on request content length, attackers can submit excessively large payloads to endpoints like `/api/share` or `/api/settings` causing resource exhaustion, memory out-of-bounds, and application unavailability (Denial of Service).
**Prevention:** Always configure `app.config['MAX_CONTENT_LENGTH']` in Flask to limit incoming request sizes according to acceptable use cases (e.g., 2MB).
## 2026-04-08 - OAuth State Replay Vulnerability
**Vulnerability:** The `oauth2callback` endpoint retrieved the OAuth `state` parameter from the user's session using `state = session['state']` but failed to pop it from the session. This leaves the `state` parameter in the session, allowing it to potentially be reused.
**Learning:** Failing to remove single-use tokens (like OAuth state) from session storage after their first use leaves them vulnerable to replay attacks if an attacker intercepts an authorization response.
**Prevention:** Always use `session.pop('key')` instead of `session['key']` when retrieving single-use security tokens from session storage to ensure they are immediately invalidated.

## $(date +%Y-%m-%d) - Missing Content Security Policy (CSP) Header
**Vulnerability:** The application was setting several security headers (like HSTS and X-Frame-Options) but failed to set a Content-Security-Policy (CSP) header, leaving it vulnerable to Cross-Site Scripting (XSS) and other injection attacks.
**Learning:** Even if a modern frontend framework (like React) is used, relying solely on it to prevent XSS is insufficient. A CSP acts as a crucial defense-in-depth layer, restricting the sources from which scripts, styles, and other resources can be loaded or executed, significantly mitigating the impact of any potential injection flaws.
**Prevention:** Always implement a restrictive Content-Security-Policy header, explicitly defining allowlists for trusted sources and avoiding permissive directives like `unsafe-inline` or `unsafe-eval` unless strictly necessary and carefully reviewed.
## 2026-04-24 - Fix Insecure Transport Allowed for OAuth
**Vulnerability:** Setting `OAUTHLIB_INSECURE_TRANSPORT="1"` globally based solely on `FLASK_ENV != 'production'` risks unintentionally enabling insecure OAuth transport in intermediate environments (like staging or CI/CD test suites).
**Learning:** Security-degrading developer conveniences must be strictly opt-in using explicitly named feature flags, rather than relying on broad environment negations.
**Prevention:** Require specific override environment variables (e.g., `ALLOW_INSECURE_OAUTH=1`) for local development conveniences that weaken security, and explicitly unset dangerous flags if the override is not provided.
