## 2025-02-28 - Auto-saving uncommitted tag inputs in modals
**Learning:** Users often type a tag (e.g., a keyword or source) and immediately click "Save Changes" without clicking "Add" or hitting Enter first, leading to frustrating data loss.
**Action:** When saving a modal with tag/list inputs, auto-append any valid uncommitted input values to the final save payload to prevent silent data loss.

## 2026-04-16 - Modal Dialog Roles and Disabled Button Titles
**Learning:** Fixed portals or backdrop wrappers acting as modals in React often lack native dialog semantics. Simply using `z-index` and focus-traps isn't enough; screen readers need explicit `role="dialog"`, `aria-modal="true"`, and `aria-labelledby` attributes to correctly announce the modal and constrain reading to its contents. Furthermore, `disabled` buttons swallow focus and context, confusing users navigating via keyboard. Using the `title` attribute to explicitly explain why a button is disabled (e.g., "Enter a keyword to add") provides a native browser tooltip as a simple UX fallback for both mouse and screen reader users when more complex accessible tooltips aren't available. Also, dynamic loading states like "Preparing audio..." need `role="status"` and `aria-live="polite"` to be announced without disrupting the current task.
**Action:** Always add `role="dialog"`, `aria-modal="true"`, and `aria-labelledby` to custom modal wrapper divs. Always consider adding dynamic `title` attributes to disabled interactive elements to explain the disabled state constraint, and use `aria-live` for dynamic textual status indicators.

## 2026-04-18 - Implicit Dismissals
**Learning:** Fixed or persistent UI elements (like a sticky audio player) and modal dialogs require explicit and implicit dismiss interactions. Users naturally attempt to click backdrops or look for close buttons to reclaim screen real estate, rather than relying strictly on the active process ending.
**Action:** Always implement `onClick={onClose}` on modal backdrops (with `e.stopPropagation()` on the inner container) and add explicit close buttons to persistent components that overlay content.

## 2026-04-22 - Skip Links and Keyboard Accessibility
**Learning:** When implementing 'skip-to-content' links, relying on standard 'sr-only' classes can sometimes cause unintended layout shifts or lack necessary interactivity when focused. Furthermore, the target container must be able to receive programmatic focus for screen readers to correctly resume context.
**Action:** Use a reliable Tailwind positioning pattern (`absolute -translate-y-[200%] focus:translate-y-0`) to hide the link visually while ensuring it appears on focus. Always pair this with `id="content"`, `tabIndex="-1"`, and `focus:outline-none` on the target container (like `<main>`) to cleanly receive focus without a jarring visual ring.

## 2026-04-23 - Scroll Restoration on Layout Collapse
**Learning:** When users interact with actions that replace long, tall content (like a full news briefing) with short, compact content (like a loading skeleton), they are often left stranded at the bottom of the page, disoriented and unable to see the new loading state.
**Action:** Always implement a `window.scrollTo({ top: 0, behavior: 'smooth' })` when initiating a major layout collapse or data refresh that replaces a tall container with a significantly shorter one, ensuring the user's viewport follows the UI context.

## 2026-04-24 - Dynamic ARIA Labels on Toggle Controls
**Learning:** When adding `aria-label` to toggle controls (like a Play/Pause button or Share/Sharing button), statically assigning an aria-label isn't enough; the `aria-label` must dynamically reflect the active state of the button (e.g., `aria-label={isPlaying ? "Pause" : "Play"}`) to accurately inform screen reader users of the action the button will perform, just like visual users interpret the changing icon. Also, be careful when adding `aria-label` to elements that have important visible text (like a Playback Speed "1.0x" button), as the `aria-label` completely overrides the visible text for screen readers; in those cases, either rely on the `title` attribute or concatenate the label with the dynamic value (e.g., `aria-label={"Playback speed: " + playbackRate + "x"}`).
**Action:** Always map toggle states dynamically to `aria-label` attributes for icon-only buttons, and concatenate dynamic visible text values into the aria-label if overriding a button that contains meaningful dynamic text.

## 2025-02-12 - Added loading state to Settings modal
**Learning:** Adding an `isSaving` state to modals that trigger asynchronous network requests (like saving settings) prevents multiple simultaneous submissions and provides crucial visual feedback (e.g., a loading spinner and disabled buttons) to avoid user confusion.
**Action:** Always include an `isSaving` state, disable submit buttons, and display a visual loading indicator while the request is pending when implementing or modifying modals in React.

## 2026-04-29 - Accessible Custom Sliders
**Learning:** When implementing a custom interactive element like an audio progress bar using a `div` with `role="slider"` and `tabIndex="0"`, simply making it focusable isn't enough. Screen reader users need accurate context (via `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, and `aria-valuetext`), and keyboard users need explicit event handlers (like `onKeyDown`) to manipulate the value using arrow keys. Without this, the slider is completely inaccessible to anyone not using a mouse. Furthermore, focus rings on dark backgrounds might need offset colors (e.g., `focus-visible:ring-offset-slate-900`) to be visible.
**Action:** Always pair `role="slider"` and `tabIndex="0"` with keyboard event handlers (`onKeyDown` for Arrow keys), complete ARIA state attributes (including `aria-valuetext` if the value is formatted, like time), and ensure focus rings have sufficient contrast against their background.
