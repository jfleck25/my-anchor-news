## 🧪 [testing improvement] Add unit tests for anonymize_user function

### 🎯 What
Added missing test coverage for the pure helper function `anonymize_user` located in `main.py`.

### 📊 Coverage
Implemented tests to verify the following behaviors:
* Handling of `None` email input (returns 'anonymous').
* Handling of an empty string email input (returns 'anonymous').
* Hashing mechanism for a valid email input utilizing `app.secret_key`.
* Consistency of hash generation across multiple calls with the exact same input.

### ✨ Result
100% path and branch coverage is achieved for the `anonymize_user` method, ensuring it operates reliably and predictably under both expected and edge-case inputs.
