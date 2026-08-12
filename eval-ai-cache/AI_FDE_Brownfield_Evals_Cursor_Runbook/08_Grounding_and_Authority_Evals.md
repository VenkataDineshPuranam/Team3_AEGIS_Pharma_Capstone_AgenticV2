# Prompt 08 — Grounding + Authority Evals

```text
If Grounding or Authority is applicable, implement them.

GROUNDING

Evaluate:

retrieval relevance
required evidence availability
claim-to-evidence support
citation validity
citation correctness
unsupported material claims
contradiction of evidence
fabricated evidence

AUTHORITY

Identify hierarchy from repository evidence such as:

regulation
policy
approved standard
procedure
KB
FAQ
informal content

Create conflict tests.

Evaluate:

correct source precedence
effective dates
versions
approved vs unapproved sources
conflicting sources
missing authoritative evidence.

Do not treat vector similarity as authority.

If these capabilities are not present:

mark NOT_APPLICABLE.

Generate separate reports.
```
