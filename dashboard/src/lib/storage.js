// Thin localStorage wrapper — every call is guarded so a private-browsing tab or a
// blocked storage API degrades to "nothing persists" instead of throwing.
const PREFIX = "growthops:";

export function loadJSON(key, fallback) {
  try {
    const raw = window.localStorage.getItem(PREFIX + key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

export function saveJSON(key, value) {
  try {
    window.localStorage.setItem(PREFIX + key, JSON.stringify(value));
  } catch {
    // storage full / unavailable — silently no-op, dashboard still works in-memory
  }
}

export function clearKey(key) {
  try {
    window.localStorage.removeItem(PREFIX + key);
  } catch {
    /* no-op */
  }
}
