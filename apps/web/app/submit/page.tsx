"use client";

import { AppShell } from "@/components/AppShell";
import { SubmitForm } from "@/components/SubmitForm";

export default function SubmitPage() {
  return (
    <AppShell title="Submit a run">
      <p className="mb-4 text-sm text-muted">
        Prefer submitting from a workflow workspace. This form remains for operators.
      </p>
      <SubmitForm />
    </AppShell>
  );
}
