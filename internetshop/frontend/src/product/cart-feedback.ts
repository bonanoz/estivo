// Error state for the add-to-cart buttons (loading state comes from htmx's .htmx-request class).

export function initCartFeedback(): void {
  const onError = (event: Event): void => {
    const el = (event as CustomEvent<{ elt?: HTMLElement }>).detail?.elt;
    if (!el?.matches('[data-add-to-cart]')) return;
    el.dataset.state = 'error';
    const status = document.querySelector<HTMLElement>('[data-add-status]');
    if (status) status.textContent = 'Не удалось добавить товар. Попробуйте ещё раз.';
    window.setTimeout(() => {
      delete el.dataset.state;
      if (status) status.textContent = '';
    }, 4000);
  };
  document.body.addEventListener('htmx:responseError', onError);
  document.body.addEventListener('htmx:sendError', onError);
}
