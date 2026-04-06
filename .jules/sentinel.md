## 2024-05-30 - Fix overly permissive CORS configuration
**Vulnerability:** The application defaulted to allowing all origins (`CORS(app)`) when the `ALLOWED_ORIGINS` environment variable was missing, enabling any site to interact with the backend API.
**Learning:** Defaulting to a wide-open CORS configuration (`*`) when an environment variable isn't present introduces a significant Cross-Origin Resource Sharing vulnerability, especially dangerous given that the API handles authenticated requests.
**Prevention:** Always default to restrictive (e.g., empty or localhost-only) origins if external configuration is absent, explicitly enabling permissive rules only when expressly specified via configuration, and configure different logic for development and production environments.

## 2024-05-18 - Fix XSS Vulnerability in PDF Generation
**Vulnerability:** The `generatePDFHtml` function in `templates/index.html` manually concatenated LLM-provided outputs (`group_headline`, `group_summary`, `angle`, `source`, `headline`) into an HTML string without sanitization. If an LLM generated malicious HTML (e.g. `<script>alert(1)</script>`), it would be executed when the user downloads/views the PDF via the `window.open` approach.
**Learning:** Manual HTML string concatenation in JavaScript is highly prone to XSS, even if the data comes from an LLM. Any untrusted data inserted directly into HTML using template literals needs to be escaped.
**Prevention:** Use an `escapeHtml` utility function to sanitize strings by replacing characters like `<`, `>`, `&`, `"`, and `'` with their corresponding HTML entities before injecting them into raw HTML strings.
