// Colour swatches: label update, URL state (history.replaceState) and 3D recolor via model-viewer.

interface ViewerMaterial {
  name: string;
  pbrMetallicRoughness: { setBaseColorFactor(rgba: [number, number, number, number]): void };
}
interface ModelViewerElement extends HTMLElement {
  model?: { materials: ViewerMaterial[] };
}

function hexToRgba(hex: string): [number, number, number, number] {
  let h = (hex || '').replace('#', '');
  if (h.length === 3) h = h.split('').map((c) => c + c).join('');
  const n = parseInt(h, 16);
  if (Number.isNaN(n)) return [0.8, 0.8, 0.8, 1];
  return [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255, 1];
}

const finishOf = (input: HTMLInputElement): string => input.name.replace(/^color_/, '');

export function initVariants(): void {
  const form = document.querySelector<HTMLFormElement>('[data-pdp-form]');
  if (!form) return;
  const viewer = document.querySelector<ModelViewerElement>('[data-model-3d] model-viewer');

  const radios = (): HTMLInputElement[] =>
    Array.from(form.querySelectorAll<HTMLInputElement>('input[type="radio"][name^="color_"]'));

  function paint(input: HTMLInputElement): void {
    if (!viewer?.model) return;
    const material = viewer.model.materials.find((m) => m.name === finishOf(input));
    material?.pbrMetallicRoughness.setBaseColorFactor(hexToRgba(input.dataset.hex ?? ''));
  }

  function syncLabel(input: HTMLInputElement): void {
    const label = input.closest('fieldset')?.querySelector<HTMLElement>('[data-color-label]');
    if (label) label.textContent = input.dataset.name ?? '';
  }

  function writeUrl(): void {
    try {
      const url = new URL(window.location.href);
      radios()
        .filter((r) => r.checked)
        .forEach((r) => url.searchParams.set(finishOf(r), r.value));
      window.history.replaceState(null, '', url);
    } catch {
      /* URL state is a nicety; never break the page over it */
    }
  }

  form.addEventListener('change', (event) => {
    const input = event.target as HTMLInputElement;
    if (!input.matches('input[type="radio"][name^="color_"]') || !input.checked) return;
    syncLabel(input);
    paint(input);
    writeUrl();
  });

  radios().filter((r) => r.checked).forEach(syncLabel);
  viewer?.addEventListener('load', () => radios().filter((r) => r.checked).forEach(paint));
}
