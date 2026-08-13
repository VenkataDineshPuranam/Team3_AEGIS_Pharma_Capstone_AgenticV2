"use client";

export function JustificationField({
  value,
  onChange,
  disabled,
}: {
  value: string;
  onChange: (v: string) => void;
  disabled?: boolean;
}) {
  return (
    <label className="block text-sm">
      <span className="font-medium text-navy">Justification (required)</span>
      <p className="text-xs text-muted">
        Recorded against the role, not a personal name. Empty silence is never treated as approval.
      </p>
      <textarea
        className="mt-1 w-full rounded border border-line bg-white px-3 py-2 text-sm"
        rows={4}
        required
        minLength={8}
        disabled={disabled}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  );
}
