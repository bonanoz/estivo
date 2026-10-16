// Page scroll lock shared by every overlay (filter panel, search overlay, mobile menu, cart drawer).
// Locks are keyed: the page unlocks only when no overlay holds a lock, so closing one overlay
// while another is still open does not give the page its scroll back.
const holders = new Set<string>();

function apply(): void {
  document.documentElement.style.overflow = holders.size > 0 ? 'hidden' : '';
}

export function setScrollLock(key: string, locked: boolean): void {
  if (locked) holders.add(key);
  else holders.delete(key);
  apply();
}
