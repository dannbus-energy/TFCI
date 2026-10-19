# ADR-0006: One UI codebase on Next.js, deployed to Cloudflare Workers

Status: Accepted
Context: Mockups through v0.9.7 proved the UX contract but embed data in
HTML; patch-layer drift was a recurring cost.
Decision: A single Next.js 16 app (shadcn/ui, TanStack Table, MapLibre)
renders materialized payloads from the API; it never computes. Mockup
lineage retires after parity is achieved.
Consequences: Local dev and production differ only by deployment.
