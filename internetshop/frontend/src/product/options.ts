// Выбор варианта в два шага: группы «Размер» и «Столешница» поверх нативного списка вариантов.
// Источник правды — исходные радиокнопки input[name="variant"]: форма отправляет именно их.
import { formatPrice } from '../lib/format';

interface Variant {
  input: HTMLInputElement;
  size: string;
  top: string;
  price: string;
}

function buildGroup(title: string, name: string, values: string[]): HTMLFieldSetElement {
  const fieldset = document.createElement('fieldset');
  fieldset.className = 'pdp-options';
  const legend = document.createElement('legend');
  legend.textContent = title;
  const list = document.createElement('div');
  list.className = 'pdp-options__list';
  values.forEach((value) => {
    const label = document.createElement('label');
    label.className = 'pdp-option';
    const input = document.createElement('input');
    input.type = 'radio';
    input.name = name;
    input.value = value;
    // form указывает на несуществующую форму: выбор групп не уходит ни в POST, ни в htmx.
    input.setAttribute('form', 'variant-ui');
    const text = document.createElement('span');
    text.textContent = value;
    label.append(input, text);
    list.append(label);
  });
  fieldset.append(legend, list);
  return fieldset;
}

export function initOptions(): void {
  const list = document.querySelector<HTMLElement>('[data-variant-list]');
  if (!list) return;
  const variants: Variant[] = Array.from(
    list.querySelectorAll<HTMLInputElement>('input[type="radio"][name="variant"]'),
  ).map((input) => ({
    input,
    size: input.dataset.size ?? '',
    top: input.dataset.top ?? '',
    price: input.dataset.price ?? '',
  }));
  if (!variants.length) return;

  const sizes = [...new Set(variants.map((v) => v.size))];
  const tops = [...new Set(variants.map((v) => v.top).filter(Boolean))];
  const sizeGroup = buildGroup('Размер', 'variant_size', sizes);
  const topGroup = tops.length ? buildGroup('Столешница', 'variant_top', tops) : null;
  const sizeRadios = Array.from(sizeGroup.querySelectorAll<HTMLInputElement>('input'));
  const topRadios = topGroup ? Array.from(topGroup.querySelectorAll<HTMLInputElement>('input')) : [];

  const current = (): Variant => variants.find((v) => v.input.checked) ?? variants[0];

  function render(): void {
    const v = current();
    sizeRadios.forEach((r) => (r.checked = r.value === v.size));
    topRadios.forEach((r) => {
      r.checked = r.value === v.top;
      r.disabled = !variants.some((x) => x.size === v.size && x.top === r.value);
    });
    document.querySelectorAll('[data-variant-price]').forEach((el) => {
      el.textContent = formatPrice(v.price);
    });
  }

  function select(v: Variant): void {
    v.input.checked = true;
    render();
    try {
      const url = new URL(window.location.href);
      url.searchParams.set('variant', v.input.value);
      window.history.replaceState(null, '', url);
    } catch {
      /* адрес — удобство, страницу из-за него не ломаем */
    }
  }

  sizeGroup.addEventListener('change', (event) => {
    const size = (event.target as HTMLInputElement).value;
    const keepTop = variants.find((v) => v.size === size && v.top === current().top);
    select(keepTop ?? variants.find((v) => v.size === size) ?? variants[0]);
  });
  topGroup?.addEventListener('change', (event) => {
    const top = (event.target as HTMLInputElement).value;
    const match = variants.find((v) => v.size === current().size && v.top === top);
    if (match) select(match);
  });

  list.after(sizeGroup);
  if (topGroup) sizeGroup.after(topGroup);
  list.hidden = true;
  render();
}
