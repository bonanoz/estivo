---
name: design-system-
description: Creates implementation-ready design-system guidance with tokens, component behavior, and accessibility standards. Use when creating or updating UI rules, component specifications, or design-system documentation.
---

<!-- TYPEUI_SH_MANAGED_START -->

# Плетёная мебель ручной работы

## Mission
Deliver implementation-ready design-system guidance for ESTIVO (плетёная мебель ручной работы) that can be applied consistently across the public storefront site.

## Brand
- Product/brand: ESTIVO — плетёная мебель ручной работы (роуп, ротанг, шпон, HPL)
- URL: https://estivo63.ru
- Audience: public visitors — private buyers, interior designers, B2B (hotels, restaurants); mobile-heavy
- Product surface: public lead-generation storefront (Django templates + Tailwind v4 + htmx + Alpine), not a dashboard

## Style Foundations
Style source is `docs/design-system/estivo-tilda/` (README, tokens, components; `MAPPING.md` maps it onto the
project); values in code are the `@theme` block in `internetshop/frontend/src/styles/main.css`; the applied guide is
`docs/design-system.md`. Read them before writing guidance — never invent token values, never copy them here.
- Visual style: quiet, light, editorial — near-white ground, dark-brown text, big uppercase serif headings, `brand` rust for small signals, `accent` terracotta only for the request button and the sale strip
- Fonts: headings Cormorant Garamond 400; body Gilroy ONLY 300/800 via `--weight-body-regular`/`--weight-body-bold` (font license); nothing below 14px
- No shadows, no gradients, square photos and cards, controls `--radius-md`, hover = opacity 0.85, focus 2px `--color-brand`, tap targets ≥ `--tap-min` (44px)

## Accessibility
- Target: WCAG 2.2 AA
- Keyboard-first interactions required.
- Focus-visible rules required.
- Contrast constraints required.

## Writing Tone
concise, confident, implementation-focused

## Rules: Do
- Use semantic tokens, not raw hex values in component guidance.
- Every component must define required states: default, hover, focus-visible, active, disabled, loading, error.
- Responsive behavior and edge-case handling should be specified for every component family.
- Accessibility acceptance criteria must be testable in implementation.

## Rules: Don't
- Do not allow low-contrast text or hidden focus indicators.
- Do not introduce one-off spacing or typography exceptions.
- Do not use ambiguous labels or non-descriptive actions.

## Guideline Authoring Workflow
1. Restate design intent in one sentence.
2. Define foundations and tokens.
3. Define component anatomy, variants, and interactions.
4. Add accessibility acceptance criteria.
5. Add anti-patterns and migration notes.
6. End with QA checklist.

## Required Output Structure
- Context and goals
- Design tokens and foundations
- Component-level rules (anatomy, variants, states, responsive behavior)
- Accessibility requirements and testable acceptance criteria
- Content and tone standards with examples
- Anti-patterns and prohibited implementations
- QA checklist

## Component Rule Expectations
- Include keyboard, pointer, and touch behavior.
- Include spacing and typography token requirements.
- Include long-content, overflow, and empty-state handling.

## Quality Gates
- Every non-negotiable rule must use "must".
- Every recommendation should use "should".
- Every accessibility rule must be testable in implementation.
- Prefer system consistency over local visual exceptions.

<!-- TYPEUI_SH_MANAGED_END -->
