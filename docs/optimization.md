# Groq token optimization — 27 November 2026

## Changes

- Select public profile facts locally by employer, project or topic in English, French and Spanish. Keep source precedence and uncertainty notes; exclude unrelated missions and document hashes. Context is limited to 6,500 characters without cutting a fact in half.
- Send at most four recent messages, each limited to 500 characters, instead of forwarding all eight accepted history turns. Keep the latest question intact (up to 1,500 characters).
- Ask for concise answers, normally under 100 words. Limit completion plus reasoning to 1,024 tokens instead of 2,048; retain the current Groq model and low reasoning setting.
- Cache only approved public FAQ questions with empty history. `app/faq.py` contains eight categories in three languages, including the sidebar suggestions. Case, whitespace, accents and punctuation are normalized; paraphrases require an explicit alias.
- Reuse FAQ answers for 24 hours, up to 128 entries per process. Coalesce simultaneous misses for the same FAQ. A hit uses no Groq request or tokens and does not consume the Python provider budget. Errors and visitor conversations are not cached.

## Live measurements

Model: `openai/gpt-oss-20b`, temperature 0, low reasoning. Token counts were collected from LangChain's provider usage metadata, not estimated from characters. The baseline used the full-profile prompt from commit `f894fed`; optimized rows used the final selected-context prompt. No history was supplied.

| Request | Input tokens | Output tokens (including reasoning) | Total |
| --- | ---: | ---: | ---: |
| Full profile: “What languages does Diana speak?” | 3,804 | 52 | 3,856 |
| Selected facts: same English language question | 585 | 43 | 628 |
| Selected facts: Covéa technologies, French | 759 | 85 | 844 |
| Selected facts: Assura dates, Spanish | 750 | 74 | 824 |

The language question submitted **84.6% fewer input tokens**. Both versions identified French, English and Spanish. Covéa retained the CV's JavaScript/Playwright/Jenkins/Jira/XRay; Assura remained in 2022 without invented mission months. All three final optimized outputs used valid catalogue source IDs.

The baseline provider metadata also reported 3,584 cached input tokens. Therefore the raw input reduction above is **not a measured reduction in quota usage or billing**, and cannot establish a fixed number of extra free questions. Groq's own prompt cache and account-specific request/token limits apply separately. Application answer-cache hits avoid the provider entirely.

Two identical FAQ requests against the real FastAPI handler were instrumented: exactly one call reached the real generation function, and the answers matched. Through the running portfolio's `/api/chat`, a French languages question then returned HTTP 200 in 0.504 seconds; its repeat returned the identical answer and source link in 0.029 seconds. These timings are individual observations, not a latency guarantee.

## Automated verification

- 37 pytest checks passed without provider calls: multilingual selection, CV precedence, follow-up topic resolution, context/history bounds, citation allowlisting, FAQ isolation, profile/model invalidation, TTL, LRU, defensive copies, errors, concurrent coalescing/cancellation, authentication and cache hits after the provider budget is exhausted.
- Five existing Playwright chat checks passed through the local portfolio, including history handling, retry/reset, text/source safety, mobile/keyboard behaviour and gateway validation.
- FastAPI was restarted with the final code; the portfolio gateway continued using the same API contract and service token.

## Operation and limits

Set `CHAT_CACHE_TTL_SECONDS` and `CHAT_CACHE_MAX_ENTRIES` in `.env`; defaults are 86400 and 128. Set either to 0 to disable. Restart after editing environment, profile or code. Cache keys include locale, profile, system prompt, model and retrieval revision. RAM entries disappear on restart. Run one worker; multiple workers/replicas would have independent cache and rate-limit state.

To add a common question, add reviewed public phrasing to the relevant language in `app/faq.py`, then test its retrieval result. Do not broadly cache arbitrary conversation text. The selector is lexical, so unfamiliar wording or a topic change without an explicit employer/project can miss relevant detail. Shortened history may lose older context; naming the company/project in a follow-up helps. The context selection and a few live checks do not prove general model accuracy.

Groq can still return 429 for requests that need a new answer. This change does not expand the account quota or switch to a paid plan. See [Groq rate limits](https://console.groq.com/docs/rate-limits) and [LangChain ChatGroq usage metadata](https://docs.langchain.com/oss/python/integrations/chat/groq).
