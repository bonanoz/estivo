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
- Product surface: public lead-generation storefront (Django templates + vanilla CSS/JS), not a dashboard

## Style Foundations
Source of truth for values is `internetshop/shop/static/css/variables.css`; the full guide is `docs/design-system.md`.
Read both before writing guidance — never invent token values. (Values previously here were scraped from the
Tilda page and were wrong: Times New Roman, 0px font size, black surface.)
- Visual style: quiet premium — warm light background, large serif headings, photos as hero, terracotta only as accent
- Fonts: headings `--font-display` (Cormorant Garamond, weight 500); body `--font-body` (Gilroy) with ONLY `--weight-body-regular` (300) and `--weight-body-bold` (800) — other body weights are forbidden (font license)
- Type scale: h1 `clamp(2.6rem,6vw,5rem)`, h2 `clamp(2rem,4vw,3.2rem)`, h3 `clamp(1.4rem,2.5vw,1.9rem)`, body `1rem`, small text not below `0.8rem`
- Colors: `--color-bg #faf8f5`, `--color-surface #fff`, `--color-surface-alt #f2ede6`, `--color-ink #1c1a17`, `--color-ink-soft #55504a`, `--color-ink-muted #6e675e`, `--color-line #e4ddd3`, `--color-accent rgb(217,120,62)`, `--color-accent-dark rgb(179,92,42)`, `--color-dark #23201c`, `--color-dark-ink #f4efe8`
- Contrast caveat: `--color-accent` fails AA for small text on light backgrounds (2.95:1 on bg); use proposed `--color-accent-text #a1592e` for terracotta text, `--color-line-strong #948f88` for control borders, `--color-error #b3261e` for errors (see docs/design-system.md §2.1)
- Spacing: `--space-1..8` = 4, 8, 16, 24, 40, 64, 96, 128px
- Radius/shadow/motion: `--radius-sm 6px`, `--radius-md 12px`, `--radius-lg 20px`; `--shadow-sm`, `--shadow-md` (multi-layer); easing `--ease cubic-bezier(0.22,0.61,0.36,1)`; breakpoints mobile <640, tablet 640–960, desktop >960

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
