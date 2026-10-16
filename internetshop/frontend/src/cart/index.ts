// Cart drawer and checkout form niceties. Owned by the cart epic.
//
// The drawer is a server fragment (partials/htmx/_cart_drawer.html) returned by POST /cart/add/<id>/.
// Whatever hx-target the "add to cart" button declares, the fragment is redirected here into
// #cart-drawer-root (created on demand), so the product page does not need a mount point.
import Alpine from 'alpinejs';

const ROOT_ID = 'cart-drawer-root';
const CLOSE_MS = 300;
const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

let lastTrigger: HTMLElement | null = null;

interface HtmxDetail {
  elt?: HTMLElement;
  pathInfo?: { requestPath?: string };
  xhr?: XMLHttpRequest;
  target?: HTMLElement;
  swapOverride?: string;
  shouldSwap?: boolean;
}

interface DrawerScope {
  $refs: Record<string, HTMLElement>;
  $nextTick: (cb: () => void) => void;
}

function isCartAdd(path: string | undefined): boolean {
  return !!path && /\/cart\/add\/\d+\/?$/.test(path.split('?')[0]);
}

function getRoot(): HTMLElement {
  let root = document.getElementById(ROOT_ID);
  if (!root) {
    root = document.createElement('div');
    root.id = ROOT_ID;
    document.body.appendChild(root);
  }
  return root;
}

// Remember who opened the drawer so focus can return there on close.
document.addEventListener('htmx:beforeRequest', (evt) => {
  const detail = (evt as CustomEvent<HtmxDetail>).detail;
  if (isCartAdd(detail.pathInfo?.requestPath)) {
    lastTrigger = detail.elt ?? (document.activeElement as HTMLElement | null);
  }
});

// Redirect the drawer fragment into the drawer root, regardless of the trigger's hx-target / hx-swap.
document.addEventListener('htmx:beforeSwap', (evt) => {
  const detail = (evt as CustomEvent<HtmxDetail>).detail;
  if (!isCartAdd(detail.pathInfo?.requestPath)) return;
  const body = detail.xhr?.responseText ?? '';
  if (detail.xhr?.status !== 200 || !body.includes('data-cart-drawer')) return;
  detail.target = getRoot();
  detail.swapOverride = 'innerHTML';
  detail.shouldSwap = true;
});

// After a stepper / remove swap inside the open drawer, the focused button is gone: keep focus in the dialog.
document.addEventListener('htmx:afterSwap', (evt) => {
  const detail = (evt as CustomEvent<HtmxDetail>).detail;
  const isLines = detail.target?.id === 'cart-lines' || /\/cart\/(update|remove|undo)\/?$/.test(detail.pathInfo?.requestPath ?? '');
  if (!isLines) return;
  const panel = document.querySelector<HTMLElement>('[data-cart-drawer] .cart-drawer');
  if (panel && (document.activeElement === document.body || document.activeElement === null)) panel.focus();
});

Alpine.data('cartDrawer', () => ({
  open: false,
  returnTo: null as HTMLElement | null,
  hiddenSiblings: [] as HTMLElement[],

  init() {
    // Wait one frame so the closed state is painted and the slide-in can transition.
    requestAnimationFrame(() => this.show());
  },

  show() {
    const scope = this as unknown as DrawerScope;
    this.returnTo = lastTrigger ?? (document.activeElement as HTMLElement | null);
    this.open = true;
    document.documentElement.style.overflow = 'hidden';
    // Everything behind the dialog becomes inert (screen readers and Tab skip it).
    this.hiddenSiblings = Array.from(document.body.children).filter(
      (el): el is HTMLElement => el instanceof HTMLElement && el.id !== ROOT_ID,
    );
    this.hiddenSiblings.forEach((el) => el.setAttribute('inert', ''));
    scope.$nextTick(() => scope.$refs.panel?.focus());
  },

  release() {
    document.documentElement.style.overflow = '';
    this.hiddenSiblings.forEach((el) => el.removeAttribute('inert'));
    this.hiddenSiblings = [];
  },

  close() {
    if (!this.open) return;
    const el = (this as unknown as { $el: HTMLElement }).$el;
    this.open = false;
    this.release();
    const target = this.returnTo;
    window.setTimeout(() => {
      // Only remove our own element: a newer drawer may already occupy the root.
      if (el.isConnected) el.remove();
      const another = document.querySelector('[data-cart-drawer]');
      if (!another && target && document.contains(target)) target.focus();
    }, CLOSE_MS);
  },

  // Replaced by a newer drawer while open: do not leave the page inert.
  destroy() {
    if (this.open) this.release();
  },

  // Keep Tab inside the dialog.
  trap(event: KeyboardEvent) {
    const panel = (this as unknown as DrawerScope).$refs.panel;
    if (!panel) return;
    const items = Array.from(panel.querySelectorAll<HTMLElement>(FOCUSABLE)).filter((el) => el.offsetParent !== null);
    if (items.length === 0) {
      event.preventDefault();
      panel.focus();
      return;
    }
    const first = items[0];
    const last = items[items.length - 1];
    const active = document.activeElement;
    if (event.shiftKey && (active === first || active === panel)) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && active === last) {
      event.preventDefault();
      first.focus();
    }
  },
}));

// Checkout form: phone mask and double-submit guard (scoped, so it does not depend on the legacy forms.js).
function formatPhone(raw: string): string {
  let digits = raw.replace(/\D/g, '');
  if (digits.startsWith('8')) digits = '7' + digits.slice(1);
  if (!digits.startsWith('7')) digits = '7' + digits;
  digits = digits.slice(0, 11);
  let out = '+7';
  if (digits.length > 1) out += ' ' + digits.slice(1, 4);
  if (digits.length >= 5) out += ' ' + digits.slice(4, 7);
  if (digits.length >= 8) out += '-' + digits.slice(7, 9);
  if (digits.length >= 10) out += '-' + digits.slice(9, 11);
  return out;
}

function initCheckoutForm(): void {
  const form = document.querySelector<HTMLFormElement>('form[data-checkout-form]');
  if (!form) return;
  form.querySelectorAll<HTMLInputElement>('input[name="customer_phone"]').forEach((input) => {
    input.addEventListener('input', () => {
      input.value = formatPhone(input.value);
    });
  });
  form.addEventListener('submit', () => {
    const btn = form.querySelector<HTMLButtonElement>('button[type="submit"]');
    if (!btn) return;
    window.setTimeout(() => {
      btn.setAttribute('aria-busy', 'true');
      btn.disabled = true;
    }, 0);
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initCheckoutForm);
} else {
  initCheckoutForm();
}
