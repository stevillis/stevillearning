# Design System & Styling Guidelines

## Color Strategy

- **Theme**: Saturated Obsidian & Data-Cyan Dark Theme (Tailored for Data Science).
- **Background Root**: `--bg-dark`: `#0b0f19` (Deep Slate / Obsidian)
- **Surface Elevation 1**: `--bg-surface`: `#111827` (Card / Panel background)
- **Surface Elevation 2**: `--bg-surface-hover`: `#1f2937` (Interactive hover state)
- **Border Default**: `--border-subtle`: `rgba(255, 255, 255, 0.08)` / `#1f2937`
- **Text Main (Ink)**: `--text-primary`: `#f3f4f6` (Off-white, 4.5+:1 contrast)
- **Text Muted**: `--text-muted`: `#9ca3af` (Cool gray, 4.5+:1 contrast)
- **Accents**:
  - **Data Cyan (Courses)**: `#06b6d4` / `rgba(6, 182, 212, 0.15)`
  - **Emerald Green (Certifications & Completed)**: `#10b981` / `rgba(16, 185, 129, 0.15)`
  - **Sapphire Blue (Formations)**: `#3b82f6` / `rgba(59, 130, 246, 0.15)`
  - **Electric Amber (In Progress & Projects)**: `#f59e0b` / `rgba(245, 158, 11, 0.15)`

## Typography

- **Display & Headings**: `Plus Jakarta Sans`, `sans-serif` (Modern, geometric, clean)
- **Body & Controls**: `Inter`, `sans-serif` (High-legibility reading experience)
- **Metrics & Code**: `JetBrains Mono` / `ui-monospace`, `monospace` (Data-dense precision feel)

## Components & Visual Tokens

- **Dashboard Stat Metric Cards**: Dark elevated panels with top subtle accent border, monospaced stat numbers, and category labels.
- **Skill & Category Badges**: Micro-pills with low-opacity colored background tints and matching high-contrast text.
- **Career Timeline / Activity List**: Vertical timeline with status indicators, course icons, and smooth card hovers.
- **Course & Certification Cards**: Clean grid layout, image/badge thumbnail header, workload badge, category tags, and action buttons.
- **Navigation Header**: Sticky glassmorphic navbar (`backdrop-blur-md bg-opacity-80`), brand mark with Data Science aesthetic, desktop links + responsive animated mobile menu.

## Anti-Patterns Avoided

- No neon pink `#ff0066` outlines or heavy glowing drop-shadows.
- No tiny unreadable low-contrast light-gray text.
- No plain bullet lists or unstyled Django detail templates.
