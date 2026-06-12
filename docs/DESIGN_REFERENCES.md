# Design References

## Project visual identity

Dark productivity platform with a warm brown accent.
Feels like a premium tool — not a startup marketing site.
Confident, focused, data-dense where needed, spacious where not.

## Reference sites

- dub.co — primary dashboard reference. Clean dark UI, excellent data
  table density, sharp link/row components, warm neutral palette,
  confident sans-serif typography. Study the dashboard sidebar,
  table rows, and stat cards closely.
- tab.co — secondary reference. Minimal dark SaaS, strong typographic
  hierarchy, lots of breathing room, subtle borders, no noise.
- linear.app — tertiary reference for interaction patterns.
  Keyboard-first, fast, no unnecessary decoration.

## What we take from each

- From dub.co: data table structure, stat card layout, sidebar nav style,
  how to show status badges without being noisy
- From tab.co: landing page typography scale, hero section confidence,
  whitespace discipline, how to introduce a product visually
- From linear.app: interaction speed, minimal hover states, how to
  handle dense lists without visual fatigue

## Color system

### Backgrounds (darkest to lightest)

- Page background: #0c0a09 (very dark warm black, not cold)
- App shell/sidebar: #111009 (slightly warm dark)
- Card surface: #1a1713 (warm dark brown-tinted surface)
- Card hover/elevated: #211e19 (subtle lift)
- Border default: #2a2520 (warm very subtle border)
- Border emphasis: #3d3830 (visible but not harsh)

### Text

- Primary: #f5f0eb (warm off-white, not stark white)
- Secondary: #a89b8c (warm muted, readable)
- Muted: #6b5e52 (deemphasized, metadata)
- Disabled: #3d3328 (barely visible)

### Accent — brown

- Primary accent: #a0673a (warm medium brown, main CTA color)
- Accent hover: #b8784a (slightly lighter on hover)
- Accent muted: #7a4d2b (for secondary accent use)
- Accent subtle: #2a1a0e (background tint for accent areas)
- Accent border: #5c3820 (border when accent context needed)

### Status colors (warm-shifted to not clash with brown)

- Success: #4a7c59 (muted green)
- Warning: #8a6a2a (warm amber, close to accent family)
- Error: #8a3a2a (warm red-brown)
- Info: #2a5a7a (cool blue for contrast)

### Semantic CSS variable names for Tailwind

--color-bg: #0c0a09
--color-surface: #1a1713
--color-surface-hover:#211e19
--color-border: #2a2520
--color-border-em: #3d3830
--color-text: #f5f0eb
--color-text-muted: #a89b8c
--color-text-faint: #6b5e52
--color-accent: #a0673a
--color-accent-hover: #b8784a
--color-accent-subtle:#2a1a0e

## Typography

### Fonts

- UI font: Geist (already in Nova preset) — clean, confident, modern
- Mono font: Geist Mono — for job IDs, scores, technical metadata
- No serif fonts anywhere

### Scale (follow Nova preset defaults, override where noted)

- Page title (h1): 24px, weight 600, tracking -0.02em
- Section title (h2): 18px, weight 500, tracking -0.01em
- Card title: 14px, weight 500, tracking 0
- Body: 14px, weight 400, line-height 1.5
- Small/meta: 12px, weight 400, color text-muted
- Stat numbers: 28px, weight 600, tabular-nums, mono font
- Badge/label: 11px, weight 500, uppercase, tracking 0.05em

## Spacing and layout

### Page structure

- Sidebar width: 220px (collapsed: 48px)
- Main content max-width: 1200px
- Page padding: 24px horizontal, 20px vertical
- Section gap: 24px
- Card padding: 16px

### Border radius (Nova preset — keep tight)

- Cards: 8px
- Buttons: 6px
- Badges: 4px
- Inputs: 6px
- Modals: 10px
- Never use fully rounded (pill) on data components

## Component patterns

### Job cards / list rows (most common component)

- Inspired by dub.co link rows
- Left: company favicon (20px) + job title + company name
- Right: match score (NumberTicker, mono font, accent color) + status badge
- Bottom meta row: location · salary · posted date — all muted text, 12px
- Hover: surface-hover background, accent-border left border (2px)
- No heavy shadow — border only

### Stat cards (dashboard overview)

- Inspired by dub.co stat cards
- Large number (NumberTicker animation on mount)
- Label below in muted text
- Subtle accent-subtle background tint
- No icon unless functionally necessary

### Status badges

- Applied: accent-subtle bg, accent-border border, accent text
- Interview: success-tinted
- Rejected: error-tinted
- Saved: border only, muted text
- Never use solid filled badges on dark — tinted only

### Sidebar navigation

- Inspired by dub.co sidebar
- Active item: accent-subtle bg, accent left border 2px, accent text
- Inactive: muted text, no bg
- Icons: 16px, same color as text
- Section labels: 11px uppercase muted, tracking wide

### Data tables

- Header: border-bottom only, muted text, 11px uppercase
- Row: border-bottom only (border default color)
- Row hover: surface-hover bg
- No zebra striping
- Pagination: minimal, text-based, not button-heavy

## Animations — Magic UI usage rules

### Where to use animation

- Landing/hero page: yes, freely
- Dashboard data pages: minimal — only on mount, never on interaction
- Never animate tables, lists, or form inputs

### Specific Magic UI components and where

- BlurFade: page section entry on landing only
- NumberTicker: stat card numbers on mount (dashboard)
- GradualSpacing or TypingAnimation: hero headline only
- Particles: hero background only, opacity 0.3, very slow movement
- ShimmerButton: primary CTA on landing page only
- BorderBeam: hero feature card accent only
- Never use Sparkles, Confetti, or other celebratory effects

### Animation rules

- Max duration: 300ms for UI interactions, 600ms for entry animations
- Easing: ease-out always
- Never block interaction with animation
- Reduced motion: always respect prefers-reduced-motion

## What NOT to do

- No bright white anywhere — use #f5f0eb max
- No cold/blue-tinted grays — all neutrals must be warm
- No multiple accent colors — brown only, everywhere
- No gradient text in data views — landing page only
- No card shadows — borders only
- No rounded pill buttons on data pages
- No skeleton loaders that flash bright white
- No animations longer than 600ms
- No decorative icons that don't mean anything
- No empty state illustrations — use clean text + single CTA

---
