// Shared helpers exposed to Alpine templates.
import Alpine from 'alpinejs';
import { setScrollLock } from './scroll-lock';

// Usage in a template: x-effect="$scrollLock('filters', open)".
Alpine.magic('scrollLock', () => setScrollLock);
