// Catalog behaviour: filter panel, focus trap (also used by the header search overlay), search suggestions.
// Owned by the catalog epic. Everything here is progressive enhancement: without JS the filters are a plain GET form.
import Alpine from 'alpinejs';

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), summary, [tabindex]:not([tabindex="-1"])';

function focusableIn(root: HTMLElement): HTMLElement[] {
  return Array.from(root.querySelectorAll<HTMLElement>(FOCUSABLE)).filter(
    (el) => el.offsetParent !== null || el === document.activeElement,
  );
}

// x-focus-trap="<expression>": while the expression is truthy, Tab / Shift+Tab cycle inside the element.
// Focus placement and focus return stay with the owner of the open/close state.
Alpine.directive('focus-trap', (el, { expression }, { effect, evaluateLater, cleanup }) => {
  const root = el as HTMLElement;
  const isActive = evaluateLater(expression);
  let active = false;

  const onKeydown = (event: KeyboardEvent): void => {
    if (!active || event.key !== 'Tab') return;
    const items = focusableIn(root);
    if (items.length === 0) {
      event.preventDefault();
      return;
    }
    const first = items[0];
    const last = items[items.length - 1];
    const current = document.activeElement as HTMLElement | null;
    if (event.shiftKey && (current === first || !root.contains(current))) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && (current === last || !root.contains(current))) {
      event.preventDefault();
      first.focus();
    }
  };

  root.addEventListener('keydown', onKeydown);
  effect(() => {
    isActive((value: unknown) => {
      active = Boolean(value);
    });
  });
  cleanup(() => root.removeEventListener('keydown', onKeydown));
});

interface CatalogFilters {
  open: boolean;
  trigger: HTMLElement | null;
  show(trigger: HTMLElement): void;
  hide(): void;
  $el: HTMLElement;
  $refs: Record<string, HTMLElement>;
  $nextTick(callback: () => void): void;
}

Alpine.data(
  'catalogFilters',
  () =>
    ({
      open: false,
      trigger: null,
      show(this: CatalogFilters, trigger: HTMLElement) {
        this.trigger = trigger;
        this.open = true;
        this.$nextTick(() => {
          const sheet = this.$refs.sheet;
          const first = sheet && focusableIn(sheet)[0];
          if (first) first.focus();
        });
      },
      hide(this: CatalogFilters) {
        if (!this.open) return;
        this.open = false;
        // The panel is apply-based: closing without "Применить" discards unsaved changes.
        const form = this.$el.querySelector<HTMLFormElement>('#catalog-form');
        form?.reset();
        form?.dispatchEvent(new Event('change', { bubbles: true }));
        const trigger = this.trigger;
        this.$nextTick(() => trigger?.focus());
      },
    }) as unknown as Record<string, unknown>,
);

// Keep the catalog bar right below the sticky header (the header height changes with the promo bar and breakpoints).
function syncStickyOffset(): void {
  const header = document.querySelector<HTMLElement>('body > header');
  if (!header) return;
  const height = header.getBoundingClientRect().height;
  document.documentElement.style.setProperty('--catalog-sticky-top', `${Math.round(height)}px`);
}
syncStickyOffset();
window.addEventListener('resize', syncStickyOffset);
window.addEventListener('load', syncStickyOffset);

// Search suggestions: the input is named "search" for the plain GET form; the suggest endpoint expects "q".
document.body.addEventListener('htmx:configRequest', (event) => {
  const detail = (event as CustomEvent).detail as {
    path: string;
    parameters: Record<string, string>;
  };
  if (!detail.path.startsWith('/search/suggest/')) return;
  detail.parameters.q = detail.parameters.search;
  delete detail.parameters.search;
});

// Do not put empty fields or the default sort into the URL when the filter form is submitted.
document.addEventListener('formdata', (event) => {
  const form = (event.target as HTMLFormElement | null)?.id;
  if (form !== 'catalog-form') return;
  const data = (event as FormDataEvent).formData;
  for (const [key, value] of Array.from(data.entries())) {
    if (value === '' || (key === 'sort' && value === 'recommended')) data.delete(key);
  }
});
