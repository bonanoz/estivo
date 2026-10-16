// Main photo + thumbnail strip with a scroll-progress indicator.

export function initGallery(): void {
  const root = document.querySelector<HTMLElement>('[data-gallery]');
  if (!root) return;

  const main = root.querySelector<HTMLImageElement>('[data-gallery-main]');
  const strip = root.querySelector<HTMLElement>('[data-gallery-strip]');
  const bar = root.querySelector<HTMLElement>('[data-gallery-progress]');
  if (!main || !strip) return;

  const thumbs = Array.from(strip.querySelectorAll<HTMLButtonElement>('button[data-full]'));

  thumbs.forEach((thumb) => {
    thumb.addEventListener('click', () => {
      const full = thumb.dataset.full;
      if (full) main.src = full;
      const alt = thumb.dataset.alt;
      if (alt) main.alt = alt;
      thumbs.forEach((t) => t.setAttribute('aria-current', t === thumb ? 'true' : 'false'));
    });
  });

  if (!bar) return;
  const track = bar.parentElement as HTMLElement;
  const update = (): void => {
    const overflow = strip.scrollWidth - strip.clientWidth;
    if (overflow <= 1) {
      track.hidden = true;
      return;
    }
    track.hidden = false;
    const visible = strip.clientWidth / strip.scrollWidth;
    const progress = strip.scrollLeft / overflow;
    bar.style.width = `${Math.round(visible * 100)}%`;
    bar.style.marginLeft = `${Math.round(progress * (1 - visible) * 100)}%`;
  };
  strip.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
  update();
}
