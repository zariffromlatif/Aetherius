# Open Source Policy

## Purpose

Aetherius is open sourced to provide transparent, evidence-backed risk intelligence infrastructure for the community while preserving a managed commercial layer for pilot operations.

## Project Model

Aetherius follows an open-core model:

- Community Edition (Public): core engine, replay framework, benchmark protocol, documentation, and development tooling.
- Managed Pilot Edition (Private/Commercial): production operations, premium connectors, client-specific workflows, and SLA-backed delivery.

## What Is Public

The following are intended for the public repository:

- Core simulation and orchestration code
- Generic ingestion, mapping, and scoring logic
- Documentation and benchmark specifications
- Synthetic sample outputs and replay artifacts
- CI, lint, and test configuration
- Non-sensitive setup templates (for example, `.env.example`)

## What Is Not Public

The following must never be committed to public repositories:

- Secrets, API keys, tokens, and credentials
- Real `.env` files and production configs
- Client watchlists, customer data, and private mappings
- Internal operational runbooks containing customer-specific procedures
- Sensitive logs, traces, and telemetry with identifying metadata
- Proprietary commercial rules where disclosure harms service differentiation

## Data and Privacy Rules

- Do not commit real client data.
- Use synthetic or anonymized data in examples.
- Remove identifiers from screenshots and artifacts before publishing.
- Follow least-privilege access principles for all integrations.

## Security and Disclosure

- Security vulnerabilities must be reported privately via `SECURITY.md` contact instructions.
- Do not disclose exploitable details in public issues before remediation.
- Patch priority: credential leaks, auth bypass, data boundary violations, and delivery misrouting.

## Contribution Boundaries

External contributors may submit improvements to public modules.
Maintainers reserve the right to reject contributions that:

- Introduce legal or compliance risk
- Weaken tenant or data boundaries
- Expose private or commercial implementation details
- Add dependencies without operational justification

## Release Hygiene Requirements

Before each public release:

1. Run secret scanning and dependency checks.
2. Verify `.gitignore` excludes secrets, logs, caches, and generated artifacts.
3. Confirm samples are synthetic and safe.
4. Ensure docs reflect current architecture and limitations.
5. Validate benchmark reproducibility instructions.

## Legal and Licensing

- Source code is released under the repository license.
- Trademarks, brand assets, and managed-service materials remain restricted unless explicitly licensed.
- Open-source use does not include investment advisory rights or guarantees.

## Responsible Use Disclaimer

Aetherius is a decision-support and research system.
It does not provide investment advice, execution guarantees, or fiduciary services.
