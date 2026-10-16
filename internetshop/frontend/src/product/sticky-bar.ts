// Sticky mobile buy bar: appears once the main buy button has scrolled out of view.

export function initStickyBar(): void {
  const bar = document.querySelector<HTMLElement>('[data-sticky-bar]');
  const anchor = document.querySelector<HTMLElement>('[data-buy-anchor]');
  if (!bar || !anchor || !('IntersectionObserver' in window)) return;

  const setVisible = (visible: boolean): void => {
    bar.classList.toggle('is-visible', visible);
    if (visible) bar.removeAttribute('inert');
    else bar.setAttribute('inert', '');
  };

  new IntersectionObserver(
    ([entry]) => {
      // Show only after the button went above the viewport, not while it is still below the fold.
      setVisible(!entry.isIntersecting && entry.boundingClientRect.top < 0);
    },
    { threshold: 0 },
  ).observe(anchor);
}
