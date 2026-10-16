// Sticky mobile buy bar: appears once the main buy button has scrolled out of view.

export function initStickyBar(): void {
  const bar = document.querySelector<HTMLElement>('[data-sticky-bar]');
  const anchor = document.querySelector<HTMLElement>('[data-buy-anchor]');
  if (!bar || !anchor || !('IntersectionObserver' in window)) return;

  const setVisible = (visible: boolean): void => {
    bar.classList.toggle('is-visible', visible);
    if (visible) bar.removeAttribute('inert');
    else bar.setAttribute('inert', '');
    // Lift the floating contact button above the bar and keep the footer readable (bar is display:none on desktop).
    const h = visible ? bar.offsetHeight : 0;
    document.documentElement.style.setProperty('--contact-offset', `${h}px`);
    document.body.style.paddingBottom = h ? `${h + 16}px` : '';
  };

  // Visible only after the main button went above the viewport, and hidden again once the footer
  // scrolls in, so the bar never sits on top of the footer content.
  let anchorAbove = false;
  let footerInView = false;
  const update = (): void => setVisible(anchorAbove && !footerInView);

  new IntersectionObserver(
    ([entry]) => {
      anchorAbove = !entry.isIntersecting && entry.boundingClientRect.top < 0;
      update();
    },
    { threshold: 0 },
  ).observe(anchor);

  const footer = document.querySelector<HTMLElement>('footer');
  if (footer) {
    new IntersectionObserver(
      ([entry]) => {
        footerInView = entry.isIntersecting;
        update();
      },
      { threshold: 0 },
    ).observe(footer);
  }
}
