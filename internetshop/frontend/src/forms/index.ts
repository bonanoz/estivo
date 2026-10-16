// Form niceties for every form on the site: Russian phone mask and a double-submit guard.
// Both are progressive enhancement; the server validates the phone number on its own.

export function formatPhone(raw: string): string {
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

const PHONE_SELECTOR = 'input[name="phone"], input[name="customer_phone"]';

function initForms(): void {
  document.querySelectorAll<HTMLInputElement>(PHONE_SELECTOR).forEach((input) => {
    input.addEventListener('input', () => {
      input.value = formatPhone(input.value);
    });
  });

  document.querySelectorAll<HTMLFormElement>('form[data-once]').forEach((form) => {
    form.addEventListener('submit', () => {
      const btn = form.querySelector<HTMLButtonElement>('button[type="submit"]');
      if (!btn) return;
      // Disable after the submit has been dispatched, otherwise the browser drops the click.
      window.setTimeout(() => {
        btn.setAttribute('aria-busy', 'true');
        btn.disabled = true;
      }, 0);
    });
  });
}

// Coming back through the bfcache must not leave the button stuck in the busy state.
window.addEventListener('pageshow', (event) => {
  if (!event.persisted) return;
  document.querySelectorAll<HTMLButtonElement>('form[data-once] button[aria-busy="true"]').forEach((btn) => {
    btn.removeAttribute('aria-busy');
    btn.disabled = false;
  });
});

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initForms);
} else {
  initForms();
}
