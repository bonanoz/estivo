import './styles/main.css';
import htmx from 'htmx.org';
import Alpine from 'alpinejs';

declare global {
  interface Window {
    htmx: typeof htmx;
    Alpine: typeof Alpine;
  }
}

// Шаблоны используют только JSON в hx-vals/hx-headers, без "js:" и hx-on — eval не нужен.
htmx.config.allowEval = false;
window.htmx = htmx;
window.Alpine = Alpine;

// Feature modules register themselves: every `src/<feature>/index.ts` is imported
// automatically, so new epics add a folder without editing this file.
import.meta.glob('./*/index.ts', { eager: true });

// Counter badges in the header are hidden at 0; HTMX swaps their text (OOB), so keep `hidden` in sync.
function syncCounters(root: ParentNode = document): void {
  root.querySelectorAll<HTMLElement>('[data-cart-count], [data-wishlist-count]').forEach((el) => {
    el.hidden = (el.textContent ?? '').trim() === '0' || (el.textContent ?? '').trim() === '';
  });
}
document.body.addEventListener('htmx:afterSettle', () => syncCounters());
document.body.addEventListener('htmx:oobAfterSwap', () => syncCounters());

Alpine.start();
