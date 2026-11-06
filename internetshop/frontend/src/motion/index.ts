// Restrained site-wide motion: blocks fade up on scroll, header counters and the wishlist heart bump on change.
// Progressive enhancement: without JS or with reduced motion nothing is hidden and nothing moves.

import { formatPrice } from '../lib/format';

const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Card grids reveal card by card; their wrapper stays put so opacity does not stack.
const TARGETS = 'main section > :not(:has(.product-card)), .product-card';
const seen = new WeakSet<Element>();

const observer = reduced
  ? null
  : new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-in');
          observer?.unobserve(entry.target);
        });
      },
      { rootMargin: '0px 0px -10% 0px' },
    );

function reveal(root: ParentNode, onlyBelowFold: boolean, selector = TARGETS): void {
  if (!observer) return;
  const nodes = [...(root instanceof Element && root.matches(selector) ? [root] : []), ...root.querySelectorAll(selector)];
  nodes.forEach((el, i) => {
    if (seen.has(el)) return;
    seen.add(el);
    // The first screen is already painted: hiding it now would flicker.
    if (onlyBelowFold && el.getBoundingClientRect().top < window.innerHeight) return;
    if (el.classList.contains('product-card')) (el as HTMLElement).style.transitionDelay = `${(i % 4) * 60}ms`;
    el.setAttribute('data-reveal', '');
    observer.observe(el);
  });
}

function bump(el: Element): void {
  if (reduced) return;
  el.classList.remove('is-bumped');
  void (el as HTMLElement).offsetWidth; // restart the animation on repeated changes
  el.classList.add('is-bumped');
  el.addEventListener('animationend', () => el.classList.remove('is-bumped'), { once: true });
}

// The cart total runs from the old sum to the new one, then shows the server's own text again.
function countTo(el: HTMLElement, from: number): void {
  const to = Number(el.dataset.cartTotal);
  if (reduced || !from || from === to) return;
  const final = el.textContent;
  el.textContent = formatPrice(from); // the swapped-in fragment must not flash the new sum first
  const start = performance.now();
  const frame = (now: number) => {
    const t = Math.min((now - start) / 400, 1);
    el.textContent = t < 1 ? formatPrice(Math.round(from + (to - from) * (1 - (1 - t) ** 3))) : final;
    if (t < 1) requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);
}

// #cart-lines is swapped whole (outerHTML): read the old total before it is gone, start right after the swap
// (htmx:load waits for settle, and the new sum would show for a frame).
let prevTotal = 0;
document.addEventListener('htmx:beforeSwap', (event) => {
  const target = (event as CustomEvent<{ target?: Element }>).detail?.target;
  prevTotal = Number(target?.querySelector<HTMLElement>('[data-cart-total]')?.dataset.cartTotal ?? 0);
});
document.addEventListener('htmx:afterSwap', (event) => {
  if ((event as CustomEvent<{ target?: Element }>).detail?.target?.id !== 'cart-lines') return;
  const total = document.querySelector<HTMLElement>('#cart-lines [data-cart-total]');
  if (total) countTo(total, prevTotal);
});

const COUNTERS = '[data-cart-count], [data-wishlist-count]';
document.querySelectorAll<HTMLElement>(COUNTERS).forEach((el) => {
  el.dataset.prev = (el.textContent ?? '').trim();
});

reveal(document, true);

// Swapped-in product cards (cart drawer picks) fade in even on screen; other swaps such as
// #cart-lines on every quantity change must not re-animate.
document.body.addEventListener('htmx:load', (event) => {
  const elt = (event as CustomEvent<{ elt?: Element }>).detail?.elt;
  if (!elt) return;
  reveal(elt, false, '.product-card');
  if (elt.matches('.product-card__heart[aria-pressed="true"]')) bump(elt);
});

document.body.addEventListener('htmx:oobAfterSwap', () => {
  document.querySelectorAll<HTMLElement>(COUNTERS).forEach((el) => {
    const now = (el.textContent ?? '').trim();
    if (now !== el.dataset.prev) bump(el);
    el.dataset.prev = now;
  });
});
