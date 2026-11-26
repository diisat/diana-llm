# Verification — 26 November 2026

## Local automated checks

- Python 3.11: 17 pytest checks passed, with the provider mocked (no API quota consumed).
- Portfolio Next.js production build passed with the `/api/chat` route.
- Five dedicated Playwright chat checks passed: request/history contract, retry, text escaping and source filtering, mobile/keyboard behaviour, gateway rejection of malformed or cross-origin requests, and long-conversation limits.
- Four existing editorial checks passed. Eleven work-journey checks passed; the short car-animation check initially missed a transient state under parallel browser load and passed when rerun by itself. The map implementation was not changed for this chatbot integration.
- Desktop and mobile sidebar screenshots were inspected locally.

## Real provider checks

Model: `openai/gpt-oss-20b` hosted by Groq, invoked through LangChain and FastAPI.

| Question | Observed result |
| --- | --- |
| Covéa tools (English) | JavaScript, Playwright, Jenkins, Jira, XRay, matching the CV |
| TransUnion role in 2023 (French) | Backend Developer; recurring payments and REST API integration |
| Assura dates (Spanish) | 2022 within Leanovia; no invented mission months |
| Salary expectations (English) | Unknown; suggested contacting Diana |
| Covéa tools from the real French portfolio sidebar | HTTP 200 through Next.js `/api/chat`, correct tools and portfolio links |

The initially selected Llama model was unavailable in this account; the default now uses the accessible GPT-OSS model. Provider rate limiting was observed during rapid tests. It is handled as HTTP 429 with a retry message, rather than a fake answer. The live smoke script spaces requests to reduce bursts; actual quotas remain account-dependent.

These are bounded smoke checks, not proof of general factual accuracy or resistance to every prompt injection. The deployment Docker stack and production hosting have not been executed/provisioned during this verification. PostgreSQL remains the portfolio's production database; the existing local Java development service may use H2.

## Update — 27 November 2026

Token selection and public FAQ caching were added. All 37 Python tests and five dedicated portfolio chat tests passed. Live Groq outputs and the running portfolio gateway were checked after restarting FastAPI. See [optimization measurements](optimization.md) for the exact token counts, cache results and limitations.
