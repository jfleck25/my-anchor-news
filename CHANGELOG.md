# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to Semantic Versioning (4-digit format: MAJOR.MINOR.PATCH.MICRO).

## [1.0.0.0] - 2026-04-23

### Added
- Trust-first briefing design system focusing on intelligence over noise.
- Split-pane layout for comparing source perspectives side-by-side.
- DESIGN.md with the official color palette (slate/amber) and typography (Geist Mono/Instrument Serif).
- `generate_demo_audio.py` script for creating sample content.
- Pre-landing code review workflow and auto-fixes.

### Changed
- Migrated all legacy `brand-` UI colors to the new `slate/amber` palette.
- Refactored `index.html` to match the new visual design system.
- Audio script generation now includes single-story groups and corrects formatting.
- Updated `.gitignore` to handle design review artifacts.

### Fixed
- Fixed Python unit tests related to script generation to align with backend changes.
- Fixed stale Tailwind CSS configurations.
