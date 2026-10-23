// Измерения: цели Метрики и e-commerce dataLayer. Счётчик (window.ym) появляется только после согласия на cookie,
// поэтому без него цели молча пропускаются, а dataLayer копится — Метрика прочтёт его при подключении.
export {};

const COUNTER_ID = 93915751;

type Ym = (id: number, method: string, goal: string) => void;
type DataLayer = Record<string, unknown>[];

declare global {
  interface Window {
    ym?: Ym;
    dataLayer?: DataLayer;
  }
}

function reachGoal(goal: string): void {
  window.ym?.(COUNTER_ID, 'reachGoal', goal);
}

function pushLayer(payload: Record<string, unknown>): void {
  (window.dataLayer ??= []).push(payload);
}

function readJson<T>(id: string): T | null {
  try {
    return JSON.parse(document.getElementById(id)?.textContent ?? 'null') as T | null;
  } catch {
    return null;
  }
}

// Событие страницы (detail / purchase) и цели, отложенные сервером до следующей страницы.
const pageEvent = readJson<Record<string, unknown>>('datalayer-push');
if (pageEvent) pushLayer(pageEvent);
readJson<string[]>('pending-goals')?.forEach(reachGoal);

// Клики по телефону и мессенджерам: <a data-goal="click_tel">.
document.addEventListener('click', (evt) => {
  const link = (evt.target as Element | null)?.closest<HTMLElement>('a[data-goal]');
  if (link?.dataset.goal) reachGoal(link.dataset.goal);
});

// Любой модуль сообщает цель событием `goal` (например, cart_open из drawer).
document.addEventListener('goal', (evt) => reachGoal((evt as CustomEvent<string>).detail));

// HX-Trigger от cart_add: добавление в корзину.
document.addEventListener('ecommerce:add', (evt) => {
  const detail = (evt as CustomEvent<{ products?: unknown[] }>).detail;
  pushLayer({ ecommerce: { currencyCode: 'RUB', add: { products: detail?.products ?? [] } } });
  reachGoal('cart_add');
});
