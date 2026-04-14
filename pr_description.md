💡 What: Added visual loading states and prevented inappropriate button scaling when disabled. Specifically:
- Added a spinning icon indicator to the "Refresh" and "Play Briefing" buttons when async operations are running.
- Hid keyboard shortcut `<kbd>` hints on these buttons while in a loading state to reduce visual noise.
- Added `disabled:hover:scale-100` and `disabled:cursor-not-allowed` to interactive buttons with scale effects (like the main "Get my briefing" button) to prevent them from visually scaling up when hovered in a disabled state.

🎯 Why: To provide better feedback during async operations (loading/fetching states) and to avoid misleading visual hover scaling on disabled buttons.

📸 Before/After: Visual improvements on loading states and disabled hovering.

♿ Accessibility: The buttons now offer clear cursor-not-allowed indications when disabled, alongside screen reader compatible dynamic loading text.
