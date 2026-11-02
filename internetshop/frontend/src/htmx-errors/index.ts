// htmx does not swap 4xx/5xx responses, so without this a failed review, cart stepper or wishlist heart does nothing.
// The add-to-cart button shows its own error next to it (product/cart-feedback.ts).

// 0 — запрос не дошёл до сервера (htmx:sendError).
const MESSAGES: Record<number, string> = {
  0: 'Нет связи с сервером. Проверьте интернет и попробуйте ещё раз.',
  429: 'Слишком много отправок подряд. Попробуйте через 10 минут.',
  403: 'Страница устарела. Обновите её и повторите.',
};
const FALLBACK = 'Не получилось. Обновите страницу и попробуйте ещё раз.';

let timer = 0;

function show(text: string): void {
  let toast = document.querySelector<HTMLElement>('[data-htmx-error]');
  if (!toast) {
    toast = document.createElement('div');
    toast.className = 'site-toast';
    toast.dataset.htmxError = '';
    toast.setAttribute('role', 'alert');
    document.body.append(toast);
  }
  toast.textContent = text;
  toast.hidden = false;
  window.clearTimeout(timer);
  timer = window.setTimeout(() => {
    if (toast) toast.hidden = true;
  }, 6000);
}

const onError = (event: Event): void => {
  const detail = (event as CustomEvent<{ elt?: HTMLElement; xhr?: XMLHttpRequest }>).detail;
  if (detail?.elt?.matches('[data-add-to-cart]')) return;
  show(MESSAGES[detail?.xhr?.status ?? 0] ?? FALLBACK);
};
document.body.addEventListener('htmx:responseError', onError);
document.body.addEventListener('htmx:sendError', onError);
