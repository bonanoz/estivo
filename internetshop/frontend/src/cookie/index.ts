// The cookie banner sits at the bottom above the floating contact button (higher z-index): lift the button
// by the banner's height while it is shown, so the two never overlap (Lighthouse target-size).
export {};

const banner = document.querySelector<HTMLElement>('[data-cookie-banner]');
if (banner) {
  const sync = (): void => {
    const h = banner.isConnected ? banner.offsetHeight : 0;
    document.documentElement.style.setProperty('--cookie-offset', `${h}px`);
  };
  sync();
  new ResizeObserver(sync).observe(banner);
  // The consent answer swaps the banner out via htmx (outerHTML); its swap events fire on the detached node.
  if (banner.parentElement) new MutationObserver(sync).observe(banner.parentElement, { childList: true });
}
