/**
 * Class-name joiner. Deliberately ~10 lines rather than a dependency: the app needs
 * conditional classes, not the conflict-resolution `tailwind-merge` provides, and Phase 27
 * says not to add libraries that aren't genuinely needed.
 */
export type ClassValue = string | number | false | null | undefined | ClassValue[];

export function cn(...values: ClassValue[]): string {
  const out: string[] = [];
  for (const value of values) {
    if (!value) continue;
    if (Array.isArray(value)) {
      const nested = cn(...value);
      if (nested) out.push(nested);
    } else {
      out.push(String(value));
    }
  }
  return out.join(" ");
}
