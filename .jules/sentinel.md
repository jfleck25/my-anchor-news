## 2024-05-30 - Fix overly permissive CORS configuration
**Vulnerability:** The application defaulted to allowing all origins (`CORS(app)`) when the `ALLOWED_ORIGINS` environment variable was missing, enabling any site to interact with the backend API.
**Learning:** Defaulting to a wide-open CORS configuration (`*`) when an environment variable isn't present introduces a significant Cross-Origin Resource Sharing vulnerability, especially dangerous given that the API handles authenticated requests.
**Prevention:** Always default to restrictive (e.g., empty or localhost-only) origins if external configuration is absent, explicitly enabling permissive rules only when expressly specified via configuration, and configure different logic for development and production environments.

## 2024-05-31 - Fix XSS in PDF Generation
**Vulnerability:** The application was using manual HTML string concatenation (`document.write()`) in `generatePDFHtml` using unsanitized output directly from the LLM, leaving the PDF generation vulnerable to XSS.
**Learning:** Directly interpolating unstructured or potentially malicious string content from an LLM into an executable browser context like `document.write` creates a severe Cross-Site Scripting (XSS) vector.
**Prevention:** Always implement an `escapeHtml` or similar HTML entity escaping utility when dealing with string-concatenated HTML interpolation, particularly when the data source (like an LLM) is not explicitly trusted.
