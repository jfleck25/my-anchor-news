## 2024-05-30 - Fix overly permissive CORS configuration
**Vulnerability:** The application defaulted to allowing all origins (`CORS(app)`) when the `ALLOWED_ORIGINS` environment variable was missing, enabling any site to interact with the backend API.
**Learning:** Defaulting to a wide-open CORS configuration (`*`) when an environment variable isn't present introduces a significant Cross-Origin Resource Sharing vulnerability, especially dangerous given that the API handles authenticated requests.
**Prevention:** Always default to restrictive (e.g., empty or localhost-only) origins if external configuration is absent, explicitly enabling permissive rules only when expressly specified via configuration, and configure different logic for development and production environments.

## 2024-05-24 - Fix DOM-based XSS in PDF Generation
**Vulnerability:** The `generatePDFHtml` function in `templates/index.html` dynamically constructed an HTML string for PDF generation by manually concatenating LLM-generated JSON variables (`group_headline`, `group_summary`, etc.) without sanitization, leading to a DOM-based Cross-Site Scripting (XSS) vulnerability.
**Learning:** Manual HTML string concatenation in client-side code bypasses standard framework protections (like React's automatic escaping or Jinja2's `|safe`). Data originating from LLMs must always be treated as untrusted user input, even if it has undergone server-side "sanitization" for token optimization, because malicious input can still be reflected back perfectly.
**Prevention:** Always use dedicated sanitization libraries (like DOMPurify) or define strict HTML escaping utility functions (e.g., escaping `&`, `<`, `>`, `"`, `'`) when manually building HTML strings that incorporate any external or LLM-generated data.
