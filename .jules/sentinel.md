## 2024-05-30 - Fix overly permissive CORS configuration
**Vulnerability:** The application defaulted to allowing all origins (`CORS(app)`) when the `ALLOWED_ORIGINS` environment variable was missing, enabling any site to interact with the backend API.
**Learning:** Defaulting to a wide-open CORS configuration (`*`) when an environment variable isn't present introduces a significant Cross-Origin Resource Sharing vulnerability, especially dangerous given that the API handles authenticated requests.
**Prevention:** Always default to restrictive (e.g., empty or localhost-only) origins if external configuration is absent, explicitly enabling permissive rules only when expressly specified via configuration, and configure different logic for development and production environments.
## 2025-04-06 - Insufficient Data Validation in Share Endpoint

**Vulnerability:** The `/api/share` endpoint was accepting arbitrary JSON payloads via `request.get_json()` and directly serializing them into PostgreSQL using `json.dumps()` without any schema or type validation. This could allow attackers to store malformed data or cause storage exhaustion by submitting oversized or incorrectly structured payloads.

**Learning:** Missing schema validation on incoming JSON data exposes the application to data integrity issues and potential denial-of-service (storage exhaustion) if attackers submit massive or unexpected structures. Validating the core structure limits the attack surface and ensures expected downstream parsing.

**Prevention:** Always perform type validation (e.g., `isinstance(data, dict)`) and key presence verification (`'expected_key' in data`) for endpoints accepting JSON data before processing or storing it.

## 2024-06-03 - Prevent XSS in manual HTML string concatenation for PDF generation
**Vulnerability:** The frontend application manually concatenated unescaped JSON properties from an LLM response (based on email contents) into an HTML string for PDF generation, which was then loaded into a new window.
**Learning:** Even when the data displayed in the UI is safely rendered (e.g., by React), secondary outputs like printable PDFs or exported documents constructed via manual string concatenation (`html += ...`) bypass these safety mechanisms. When the data originates from an LLM processing untrusted external input (like emails), this creates a severe XSS vector where prompt injection can lead to script execution in the context of the application's origin (via `window.open`).
**Prevention:** Always sanitize or HTML-escape dynamic data before concatenating it into raw HTML strings, regardless of whether the primary UI rendering mechanism is considered safe. Do not trust LLM output to be benign, especially when it digests arbitrary external data.
