# Muuto storefront — merged DESIGN.md

Merged from three extractor runs on muuto.com: home (`/`), category (`/products/tables/dining/`) and product page (`/product/Linear-Wood-Table/`). Values seen on two or three pages are treated as core tokens. Values seen on one page only are listed separately and must not be used as core styling until confirmed. Layout and behavior come from UX.md, not from this file.

## Mission
Create implementation-ready, token-driven UI for an e-commerce storefront in the Muuto visual language: quiet, neutral, typography-led, with large product imagery and pill-shaped controls. Optimize for consistency, accessibility and fast delivery.

## Brand
- Product/brand: Muuto-inspired storefront (reference: https://www.muuto.com/)
- Audience: online shoppers and consumers
- Product surface: e-commerce storefront
- Do not reuse Muuto logo, photography, product names or copy.

## Style Foundations

### Typography
- Font family: `font.family.primary=EuclidFlex`, `font.family.stack=EuclidFlex, Helvetica, Arial, sans-serif` (same on all three pages). EuclidFlex is a licensed font: substitute a free grotesque sans (e.g. Inter) unless a license is obtained, and keep the Helvetica/Arial fallbacks.
- Base: `font.size.base=16px`, `font.weight.base=400`, `font.lineHeight.base=23px` (same on all three pages, line-height about 1.44).
- Scale (merged): `font.size.xs=12px`, `font.size.sm=14px`, `font.size.md=16px`, `font.size.lg=20px`, `font.size.xl=26px`, `font.size.2xl=40px`.
- Seen on one page only: 10px (home, small labels), 24px (category), 38px (product page). Treat 24px as an optional heading step and 38px as the same role as `2xl`.
- Dropped as sub-pixel noise: 16.14px, 16.64px, 18.47px (round to 16px / 20px).

### Color
Core (seen on two or more pages):
- `color.text.primary=#282828` (appears on all three pages; body text).
- `color.text.strong=#111111` (home `#111111`, category `#020202`; near-black for headings and key actions).
- `color.surface.page=#ffffff` (white; home text on dark, product page surface).
- `color.surface.neutral=#eeecea` (warm light gray; category and product page).
- `color.neutral.black=#000000` (all three pages; the extractor labeled it "surface.base", but the site pages are light, so this is most likely overlay, header or button black. Role not confirmed.)

One page only (campaign or accent, not core):
- Home: `#b7d692` (sage green), `#dee2a1` (pale lime), `#4f3d3a` (dark brown).
- Category: `#e5f5e4` (pale mint).
- Product page: `#7f7f7f` (mid gray; the extractor called it "text.inverse").

Contrast notes (must be checked in the real build):
- `#7f7f7f` on white is about 4.0:1, which fails WCAG AA for normal text. Use it only for non-text elements, large text, or on dark surfaces.
- `#dee2a1` on `#4f3d3a` is about 7.5:1 and passes.

### Spacing
- Extracted (rounded, all pages): 2px, 4px, 5px, 8px, 10px, 11px, 13px. The values 3px, 9px and 9.01px are measurement noise and are dropped.
- Important: no extracted value is above 13px. These are component paddings and gaps, not layout rhythm. Section and grid spacing were not captured.
- Proposed (not extracted) layout scale on a 4px base: `space.4=4px`, `space.8=8px`, `space.12=12px`, `space.16=16px`, `space.24=24px`, `space.32=32px`, `space.48=48px`, `space.64=64px`. Confirm against the live site before treating these as Muuto's real values.

### Radius, shadow, motion
- Radius: `radius.pill=50px` (all three pages; on controls this behaves as fully rounded), plus `radius.pill-lg=60px` (home only). No smaller radius was captured, so cards and images are assumed square until confirmed.
- Shadow: none captured. Do not add shadows by default.
- Motion durations (merged): `motion.duration.instant=150ms`, `motion.duration.fast=200ms`, `motion.duration.normal=300ms`, `motion.duration.slow=400ms`, `motion.duration.slower=550ms`. Also seen: 250ms and 350ms.

## Page density (from extractor)
| Page | Links | Buttons | Inputs | Lists | Cards | Navigation | Tables |
|---|---|---|---|---|---|---|---|
| Home | 175 | 64 | 11 | 24 | 77 | 7 | – |
| Category | 153 | 57 | 42 | 31 | 15 | 8 | – |
| Product | 140 | 80 | 11 | 29 | 2 | 9 | 2 |

Reading: the home page is card-heavy, the category page is input-heavy (filters), and the product page is button-heavy (options, add to cart) and has two tables (probably dimensions/specs).

## Accessibility
- Target: WCAG 2.2 AA.
- Keyboard-first interactions are required for every control.
- Focus-visible indicators must be present on all interactive elements and must meet 3:1 contrast against adjacent colors.
- Text contrast must be at least 4.5:1 (3:1 for large text).
- Pill controls must keep a touch target of at least 44px in height.

## Writing Tone
Concise, calm, product-first. Short labels, specific actions ("Add to cart", not "Submit").

## Rules: Do
- Use semantic tokens, not raw hex values, in component guidance.
- Every component must define states for default, hover, focus-visible, active, disabled, loading and error.
- Component behavior should specify responsive and edge-case handling.
- Interactive components must document keyboard, pointer and touch behavior.
- Accessibility acceptance criteria must be testable in implementation.
- Core tokens should come from the "Core" lists above; accent colors should be used only in campaign blocks.

## Rules: Don't
- Do not allow low-contrast text or hidden focus indicators.
- Do not introduce one-off spacing or typography exceptions.
- Do not use `#7f7f7f` for normal-size text on light surfaces.
- Do not use ambiguous labels or non-descriptive actions.
- Do not ship component guidance without explicit state rules.

## Known gaps (not captured by the extractor)
- Component specs: button variants, product card, filter chips, form fields, header/navigation. Only counts are known, not styles.
- Layout: container width, grid columns, section spacing, breakpoints.
- Page background color on each page (the extractor reported black, which is probably wrong).
- Shadows, borders, image aspect ratios.
Fill these by inspecting computed styles of the real buttons, cards and containers before building components.

## Guideline Authoring Workflow
1. Restate design intent in one sentence.
2. Define foundations and semantic tokens.
3. Define component anatomy, variants, interactions and state behavior.
4. Add accessibility acceptance criteria with pass/fail checks.
5. Add anti-patterns, migration notes and edge-case handling.
6. End with a QA checklist.

## Required Output Structure
- Context and goals.
- Design tokens and foundations.
- Component-level rules (anatomy, variants, states, responsive behavior).
- Accessibility requirements and testable acceptance criteria.
- Content and tone standards with examples.
- Anti-patterns and prohibited implementations.
- QA checklist.

## Component Rule Expectations
- Include keyboard, pointer and touch behavior.
- Include spacing and typography token requirements.
- Include long-content, overflow and empty-state handling.

## Quality Gates
- Every non-negotiable rule must use "must".
- Every recommendation should use "should".
- Every accessibility rule must be testable in implementation.
- Teams should prefer system consistency over local visual exceptions.
