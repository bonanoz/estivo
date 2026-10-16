// Product page behaviour (gallery, colour variants, 3D recolor, sticky buy bar). Owned by the product epic.
import { initGallery } from './gallery';
import { initVariants } from './variants';
import { initStickyBar } from './sticky-bar';
import { initCartFeedback } from './cart-feedback';

function init(): void {
  if (!document.querySelector('[data-pdp]')) return;
  initGallery();
  initVariants();
  initStickyBar();
  initCartFeedback();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
