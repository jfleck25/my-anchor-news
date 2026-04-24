## 2025-02-28 - Auto-saving uncommitted tag inputs in modals
**Learning:** Users often type a tag (e.g., a keyword or source) and immediately click "Save Changes" without clicking "Add" or hitting Enter first, leading to frustrating data loss.
**Action:** When saving a modal with tag/list inputs, auto-append any valid uncommitted input values to the final save payload to prevent silent data loss.
## 2025-04-15 - Async modal submission loading states
**Learning:** Users who submit a modal that triggers an async network request (like saving settings) often experience confusion or make multiple click attempts if the submit button lacks a loading state and isn't disabled during the operation. Even if the modal closes upon success, the delay before closing is noticeable.
**Action:** Always provide an `isSaving` (or similar) state for async modal submissions to disable the submit button and show a visual loading indicator (e.g., a spinner) while the network request is pending.
