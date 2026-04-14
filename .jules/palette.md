## 2025-02-28 - Auto-saving uncommitted tag inputs in modals
**Learning:** Users often type a tag (e.g., a keyword or source) and immediately click "Save Changes" without clicking "Add" or hitting Enter first, leading to frustrating data loss.
**Action:** When saving a modal with tag/list inputs, auto-append any valid uncommitted input values to the final save payload to prevent silent data loss.
## 2025-02-28 - Prevent hover effects on disabled scaling elements
**Learning:** Adding `hover:scale` utilities to elements like buttons looks great, but causes confusing UX when those elements are disabled. The user visually expects interactivity because the element scales on hover, even though `cursor-not-allowed` and `opacity-50` might be applied.
**Action:** When using `hover:scale` or similar transform effects on interactive elements, always pair it with the corresponding `disabled:hover:scale-100` (or base value) so the element remains static when disabled.
