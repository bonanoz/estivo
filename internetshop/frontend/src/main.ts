import './styles/main.css';
import htmx from 'htmx.org';
import Alpine from 'alpinejs';

declare global {
  interface Window {
    htmx: typeof htmx;
    Alpine: typeof Alpine;
  }
}

window.htmx = htmx;
window.Alpine = Alpine;

// Feature modules register themselves: every `src/<feature>/index.ts` is imported
// automatically, so new epics add a folder without editing this file.
import.meta.glob('./*/index.ts', { eager: true });

Alpine.start();
