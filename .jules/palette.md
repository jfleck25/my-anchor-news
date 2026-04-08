## 2025-02-28 - Auto-saving uncommitted tag inputs in modals
**Learning:** Users often type a tag (e.g., a keyword or source) and immediately click "Save Changes" without clicking "Add" or hitting Enter first, leading to frustrating data loss.
**Action:** When saving a modal with tag/list inputs, auto-append any valid uncommitted input values to the final save payload to prevent silent data loss.