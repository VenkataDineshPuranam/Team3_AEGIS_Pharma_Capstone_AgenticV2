"use client";

import { useEffect, useRef, useState } from "react";
import { Badge, type BadgeTone } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardBody, CardHeader } from "@/components/ui/Card";
import { Notice, SkeletonText } from "@/components/ui/States";
import { ApiError, askAboutRun, type RecordChatResponse, type Workflow } from "@/lib/api";
import { WORKFLOW_LABELS, WORKFLOW_SUBJECT_LABEL } from "@/lib/format";

/**
 * Record Assistant -- a real back-and-forth chat over one record.
 *
 * WHAT "REAL CHATBOT" MEANS HERE, AND WHAT IT DELIBERATELY DOESN'T
 * ------------------------------------------------------------------
 * The visible thread is a genuine conversation: every question you ask and every answer
 * you get stays on screen as you keep asking, exactly like a normal chat product.
 *
 * What it is NOT is a conversation from the model's point of view. Each call to
 * `POST /api/runs/{run_id}/chat` is answered independently by services/api/record_chat.py
 * -- no prior turn is sent back as context, and that is a deliberate, documented choice on
 * the backend (conversation history is a second prompt-injection surface: one poisoned
 * turn would otherwise influence every later turn). This component holds the transcript
 * only in the browser, for the human to read back -- it never becomes part of a future
 * prompt. A follow-up question therefore still needs to name its subject ("the third
 * finding", not "that one") the same way the backend's own guidance already says.
 *
 * WHAT STAYS TRUE FROM THE ORIGINAL DESIGN
 * ------------------------------------------
 * Half of every response is computed from the run and cannot be wrong (the record facts,
 * the next-steps list). The other half is the model's prose and can be. That distinction
 * does not go away just because the UI now reads as a chat -- it is preserved as a small
 * per-message label ("Model" / "Record only" / "Withheld" / "Refused") on every assistant
 * bubble, and the next-steps list stays OUTSIDE the chat log entirely, pinned above it, so
 * it is never just one more thing scrolled past.
 */
export function RecordAssistant({
  runId,
  /**
   * `embedded` drops the Card chrome for use inside an existing container -- the launcher
   * panel and the decision workspace's Assistant tab both already provide their own frame,
   * and a bordered card nested inside a bordered card reads as two separate things when it
   * is one.
   */
  embedded = false,
}: {
  runId: string;
  embedded?: boolean;
}) {
  // Callers key this component by runId (AssistantLauncher, RunDetailView), so a record
  // change remounts it and every hook below starts fresh -- no manual reset logic needed.
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [sending, setSending] = useState(false);
  const [draft, setDraft] = useState("");
  const nextId = useRef(0);
  const threadEndRef = useRef<HTMLDivElement>(null);

  function makeId(): string {
    nextId.current += 1;
    return `turn-${nextId.current}`;
  }

  // The intro call -- "just describe this record", no typing required. Structured to
  // match the accepted shape of an effect-driven fetch already used elsewhere in this
  // codebase (hooks/useApiResource.ts's `load`): the async work and its setState calls
  // live inside a function defined and invoked INSIDE the effect body, not a
  // component-level callback merely referenced from it.
  useEffect(() => {
    const controller = new AbortController();
    let cancelled = false;

    async function loadIntro() {
      setSending(true);
      try {
        const response = await askAboutRun(runId, "", controller.signal);
        if (cancelled) return;
        setTurns((prev) => [...prev, { id: makeId(), role: "assistant", response, isIntro: true }]);
      } catch (e) {
        if (cancelled || (e instanceof DOMException && e.name === "AbortError")) return;
        setTurns((prev) => [
          ...prev,
          { id: makeId(), role: "assistant-error", message: e instanceof ApiError ? e.userMessage : String(e) },
        ]);
      } finally {
        if (!cancelled) setSending(false);
      }
    }

    void loadIntro();
    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [runId]);

  useEffect(() => {
    // Optional-chained on the method too, not just the ref: jsdom (this app's test
    // environment) does not implement scrollIntoView at all, so `?.` on the ref alone
    // still throws "not a function" the moment a turn is added.
    threadEndRef.current?.scrollIntoView?.({ block: "end" });
  }, [turns, sending]);

  async function sendFollowUp(question: string) {
    setSending(true);
    try {
      const response = await askAboutRun(runId, question);
      setTurns((prev) => [...prev, { id: makeId(), role: "assistant", response, isIntro: false }]);
    } catch (e) {
      setTurns((prev) => [
        ...prev,
        { id: makeId(), role: "assistant-error", message: e instanceof ApiError ? e.userMessage : String(e) },
      ]);
    } finally {
      setSending(false);
    }
  }

  function submit(e: React.FormEvent) {
    e.preventDefault();
    const question = draft.trim();
    if (!question || sending) return;
    setDraft("");
    setTurns((prev) => [...prev, { id: makeId(), role: "user", text: question }]);
    void sendFollowUp(question);
  }

  const latest = latestResponse(turns);
  const workflow = str(latest?.record.workflow) as Workflow | null;
  const subjectId = str(latest?.record.subject_id);
  const status = str(latest?.record.status);
  const recordHits = latest?.guard.record_hits ?? [];

  const header = !embedded && (
    <CardHeader
      title="Record Assistant"
      level={3}
      description="Explains this record. It cannot decide anything, and does not try to."
    />
  );

  const Shell = embedded ? EmbeddedShell : Card;
  const Body = embedded ? EmbeddedBody : CardBody;

  return (
    <Shell>
      {header}
      <Body className="flex flex-col gap-3">
        {/* --- context strip: what record this thread is about --------------- */}
        {latest ? (
          <div className="flex flex-wrap items-center gap-2">
            {workflow && (
              <Badge tone="info" size="xs">
                {WORKFLOW_LABELS[workflow] ?? workflow}
              </Badge>
            )}
            {subjectId && (
              <span className="font-mono text-[12px] font-medium text-[var(--text-primary)]">
                {(workflow && WORKFLOW_SUBJECT_LABEL[workflow]) ?? ""} {subjectId}
              </span>
            )}
            <Badge tone={status === "decided" ? "neutral" : "pending"} size="xs">
              {status === "decided" ? "Decided" : "Awaiting decision"}
            </Badge>
          </div>
        ) : (
          sending && turns.length === 0 && <SkeletonText lines={2} />
        )}

        {recordHits.length > 0 && (
          <Notice tone="warning" title="This record contains instruction-like text">
            <p>
              {recordHits.length} field{recordHits.length === 1 ? "" : "s"} in this run
              matched a known prompt-injection pattern. The text was removed before the
              assistant saw it, and is shown here so you can judge it yourself.
            </p>
            <ul className="mt-2 space-y-1.5">
              {recordHits.map((hit, i) => (
                <li key={i} className="flex flex-wrap items-baseline gap-2">
                  <Badge tone="blocked" size="xs">
                    {hit.pattern_id}
                  </Badge>
                  <code className="font-mono text-[12px] break-all">{hit.excerpt}</code>
                </li>
              ))}
            </ul>
          </Notice>
        )}

        {/* --- next steps: computed, pinned above the chat, never scrolled away --- */}
        {latest && latest.next_steps.length > 0 && (
          <details open className="rounded-[var(--radius-md)] border border-[var(--border-subtle)]">
            <summary className="cursor-pointer select-none px-3 py-2 text-[11px] font-semibold uppercase tracking-wider text-[var(--text-tertiary)]">
              What happens next{" "}
              <span className="font-normal normal-case tracking-normal text-[var(--text-tertiary)]">
                — computed, not model-generated
              </span>
            </summary>
            {/* Capped rather than left to grow with the number of steps -- this keeps
                the composer below reliably in view without scrolling the panel, even for
                a run with a long dual-approval or severity-escalation step list. */}
            <ul className="max-h-40 space-y-2 overflow-y-auto border-t border-[var(--border-subtle)] px-3 py-2.5">
              {latest.next_steps.map((step, i) => (
                <li key={i} className="flex flex-wrap items-baseline gap-2 text-[13px] leading-relaxed">
                  {step.blocking && (
                    <Badge tone="pending" size="xs">
                      blocking
                    </Badge>
                  )}
                  <span className="font-medium text-[var(--text-primary)]">{step.owner}:</span>
                  <span className="text-[var(--text-secondary)]">{step.step}</span>
                </li>
              ))}
            </ul>
          </details>
        )}

        {/* --- the conversation ------------------------------------------------ */}
        <div className="max-h-[24rem] min-h-[8rem] flex-1 overflow-y-auto rounded-[var(--radius-md)] border border-[var(--border-subtle)] bg-[var(--surface-sunken)] p-3">
          <div className="space-y-3">
            {turns.map((turn) => (
              <ChatBubble key={turn.id} turn={turn} />
            ))}
            {sending && <TypingBubble />}
            <div ref={threadEndRef} />
          </div>
        </div>

        {/* --- composer ---------------------------------------------------- */}
        <form onSubmit={submit} className="flex gap-2">
          <label htmlFor="assistant-question" className="sr-only">
            Ask a follow-up question about this record
          </label>
          <input
            id="assistant-question"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            maxLength={1000}
            placeholder="Ask a follow-up…"
            className="h-9 min-w-0 flex-1 rounded-[var(--radius-md)] border border-[var(--border-default)] bg-[var(--surface-raised)] px-3 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] focus:border-[var(--border-strong)] focus:outline-none"
          />
          <Button type="submit" variant="secondary" disabled={sending || !draft.trim()}>
            Send
          </Button>
        </form>
        <p className="text-[11px] leading-relaxed text-[var(--text-tertiary)]">
          Each answer is generated independently — earlier turns are shown here for you to
          read, but are not sent back to the model as context. Name what a follow-up is
          about rather than saying &ldquo;that one&rdquo;. It will not tell you what to decide.
        </p>
      </Body>
    </Shell>
  );
}

// ---------------------------------------------------------------------------
// Transcript
// ---------------------------------------------------------------------------

type ChatTurn =
  | { id: string; role: "user"; text: string }
  | { id: string; role: "assistant"; response: RecordChatResponse; isIntro: boolean }
  | { id: string; role: "assistant-error"; message: string };

function latestResponse(turns: ChatTurn[]): RecordChatResponse | null {
  for (let i = turns.length - 1; i >= 0; i -= 1) {
    const turn = turns[i];
    if (turn.role === "assistant") return turn.response;
  }
  return null;
}

function str(value: unknown): string | null {
  return typeof value === "string" ? value : null;
}

/**
 * What an assistant bubble should say and how it should be labelled.
 *
 * Every branch here maps to a distinct reason the operator needs to be able to tell
 * apart: a refusal (nothing was sent to the model), a withheld answer (the model
 * answered, the answer didn't survive the output guard), a degraded answer (no model
 * reachable, these are the deterministic facts), and a normal model answer. Collapsing
 * any two of these into the same label would hide which kind of "not the model's words"
 * situation the operator is looking at.
 */
function describeBubble(response: RecordChatResponse, isIntro: boolean): { text: string; label: string; tone: BadgeTone } {
  if (response.guard.refused) {
    return { text: response.answer, label: "Refused", tone: "blocked" };
  }
  if (response.guard.output_verdict === "blocked") {
    return { text: response.answer, label: "Withheld", tone: "blocked" };
  }
  if (!response.llm_available) {
    // On the intro turn, lead with WHY there's no model prose (the reason an operator
    // actually needs) and keep the deterministic summary underneath -- dropping the
    // reason here would silently regress the degraded-mode explanation this assistant
    // has always given.
    const text = isIntro
      ? [response.summary, response.llm_unavailable_reason].filter((p) => p && p.trim()).join("\n\n")
      : response.llm_unavailable_reason || response.summary;
    return { text, label: "Record only", tone: "abstained" };
  }
  if (isIntro) {
    const parts = [response.summary, response.answer, response.next_steps_explanation].filter(
      (p) => p.trim().length > 0,
    );
    return { text: parts.join("\n\n"), label: "Model", tone: "info" };
  }
  return { text: response.answer || response.summary, label: "Model", tone: "info" };
}

function ChatBubble({ turn }: { turn: ChatTurn }) {
  if (turn.role === "user") {
    return (
      <div className="flex justify-end">
        <p className="max-w-[85%] whitespace-pre-wrap rounded-[var(--radius-lg)] rounded-br-sm bg-[var(--brand)] px-3 py-2 text-[13px] leading-relaxed text-white">
          {turn.text}
        </p>
      </div>
    );
  }

  if (turn.role === "assistant-error") {
    return (
      <div className="flex justify-start">
        <div className="max-w-[85%] rounded-[var(--radius-lg)] rounded-bl-sm border border-[var(--status-blocked-border)] bg-[var(--status-blocked-bg)] px-3 py-2 text-[13px] leading-relaxed text-[var(--status-blocked-fg)]">
          {turn.message}
        </div>
      </div>
    );
  }

  const { text, label, tone } = describeBubble(turn.response, turn.isIntro);
  const cites = turn.response.cites;

  return (
    <div className="flex justify-start">
      <div className="max-w-[85%] space-y-1.5">
        <Badge tone={tone} size="xs">
          {label}
        </Badge>
        <div className="whitespace-pre-wrap rounded-[var(--radius-lg)] rounded-bl-sm border border-[var(--border-subtle)] bg-[var(--surface-raised)] px-3 py-2 text-[13px] leading-relaxed text-[var(--text-primary)]">
          {text}
        </div>
        {cites.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5 px-0.5">
            <span className="text-[10px] uppercase tracking-wider text-[var(--text-tertiary)]">Cites</span>
            {cites.map((id) => (
              <Badge key={id} tone="authoritative" size="xs">
                {id}
              </Badge>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function TypingBubble() {
  return (
    <div className="flex justify-start" aria-live="polite">
      <div className="flex items-center gap-1 rounded-[var(--radius-lg)] rounded-bl-sm border border-[var(--border-subtle)] bg-[var(--surface-raised)] px-3 py-2.5">
        <span className="sr-only">The assistant is answering…</span>
        <Dot delayMs={0} />
        <Dot delayMs={150} />
        <Dot delayMs={300} />
      </div>
    </div>
  );
}

function Dot({ delayMs }: { delayMs: number }) {
  return (
    <span
      aria-hidden="true"
      className="size-1.5 animate-bounce rounded-full bg-[var(--text-tertiary)]"
      style={{ animationDelay: `${delayMs}ms` }}
    />
  );
}

function EmbeddedShell({ children }: { children: React.ReactNode }) {
  return <div>{children}</div>;
}

function EmbeddedBody({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return <div className={className}>{children}</div>;
}
