---
id: 011
title: Crystal Clear Cyberpunk Dark Mode Setup
stage: green
date: 2025-12-27
surface: agent
model: claude-opus-4-5-20251101
feature: ui-redesign
branch: main
user: tahiraibrahim7
command: /sp.implement
labels: ["ui", "dark-mode", "css", "tailwind", "design-system"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/app/globals.css
  - frontend/app/layout.tsx
  - frontend/app/dashboard/layout.tsx
tests:
  - N/A (visual implementation)
---

## Prompt

Act as a Lead UI/UX Designer. We need a "High-Contrast Dark Mode" redesign for our Todo App.
**Context:** Dependencies (framer-motion, lucide-react) are installed.

**Goal:** Create a "Crystal Clear Cyberpunk" look.
**CRITICAL:** Prioritize READABILITY. No blurry text.

**Action 1: Setup Global Styles**
Update `app/globals.css` to define the base theme:
1.  **Background:** Deep Void Navy (`#0B0F19` or `bg-slate-950`).
2.  **Glass Effect:** Create a utility class for cards using `bg-slate-900/70`, `backdrop-blur-xl`, and `border-white/10`.
3.  **Typography:** Headings must be Pure White (`text-white`). Body text must be Light Gray (`text-slate-200`).
4.  **Inputs:** Dark background (`bg-slate-800`), Light text, and distinct borders.

Start by updating `app/globals.css` and the main Layout.

## Response snapshot

Implemented Crystal Clear Cyberpunk High-Contrast Dark Mode theme with the following key changes:

**globals.css Updates:**
- Set Deep Void Navy background (`#0B0F19`)
- Created CSS custom properties for theme colors (background, foreground, glass, inputs, accents)
- Added crisp text rendering properties to prevent blur
- Created `.glass-card` and `.glass-card-solid` utility classes with backdrop-blur
- Created `.input-dark`, `.textarea-dark`, `.select-dark` classes for form inputs
- Created `.btn-primary`, `.btn-secondary`, `.btn-ghost` button variants
- Added status badge classes (success, warning, danger, info, neutral)
- Updated scrollbar styles to match theme

**layout.tsx Updates:**
- Added `dark` class to html element
- Set body background to `#0B0F19` with `text-slate-50`

**dashboard/layout.tsx Updates:**
- Changed from light gradient background to Deep Void Navy (`#0B0F19`)
- Updated animated background elements to use subtle blue/cyan/purple glows (10% opacity)

## Outcome

- Impact: Established foundational dark mode design system for Todo App
- Tests: N/A (visual CSS changes)
- Files: 3 files modified (globals.css, layout.tsx, dashboard/layout.tsx)
- Next prompts: Apply glass-card classes to components, update Sidebar and Navbar components
- Reflection: Prioritized readability with high-contrast colors and crisp text rendering

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment: Test glass-card classes on actual components for visual verification
