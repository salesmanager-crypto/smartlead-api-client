// Dynamic greeting engine — spec section 2. Hour is resolved in the user's chosen
// timezone (profile setting) so the greeting matches their actual working day, not
// the server's or browser default's.
export function hourInTimezone(timezone) {
  try {
    const parts = new Intl.DateTimeFormat("en-US", {
      hour: "numeric",
      hour12: false,
      timeZone: timezone,
    }).formatToParts(new Date());
    const hourPart = parts.find((p) => p.type === "hour");
    return hourPart ? Number(hourPart.value) % 24 : new Date().getHours();
  } catch {
    return new Date().getHours();
  }
}

export function greetingFor(hour, firstName) {
  if (hour >= 5 && hour < 12) return { text: `Good morning, ${firstName}!`, emoji: "☕" };
  if (hour >= 12 && hour < 17) return { text: `Good afternoon, ${firstName}!`, emoji: "⚡" };
  if (hour >= 17 && hour < 22) return { text: `Good evening, ${firstName}!`, emoji: "🌙" };
  return { text: `Burning the midnight oil, ${firstName}?`, emoji: "🚀" };
}

export function relativeTime(iso) {
  if (!iso) return "";
  const diffMs = Date.now() - new Date(iso).getTime();
  const mins = Math.round(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.round(hours / 24);
  return `${days}d ago`;
}

export const TIMEZONES = [
  "America/New_York",
  "America/Chicago",
  "America/Denver",
  "America/Los_Angeles",
  "America/Sao_Paulo",
  "Europe/London",
  "Europe/Berlin",
  "Asia/Jerusalem",
  "Asia/Dubai",
  "Asia/Kolkata",
  "Asia/Singapore",
  "Australia/Sydney",
];
