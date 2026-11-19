# Codex: OpenShorts and GTA clip operations

Scope: `tools/clip_business.py`, `tests/test_clip_business.py`, `docs/GTA_CLIP_OPS.md` and optional pinned `integrations/gtavi-claudecode` git submodule. Do NOT merge into main without human review.

Goal: zero-additional-cost legal editing business using Apple M1 and existing Codex. Make the first authorized, locally rendered 9:16 clip, document performance, then test paid creator trials. Do not promise passive income or CPM approval.

1. Inspect first; run `python3 -m unittest discover -s tests -p test_clip_business.py -v`.
2. Use local, creator-supplied footage only with recorded permission. Do not automatically scrape/download/republish other people's streams. Verify publisher and soundtrack rights separately.
3. Do not sign up to services, connect social accounts, send messages, post, spend funds, store secrets in Git or claim payout confirmation without human approval.
4. Never edit the pinned vendor submodule in place; make customizations in separate wrapper code and propose an upstream PR if appropriate.
5. Prefer stdlib + FFmpeg first; paid OpenShorts Gemini/ElevenLabs/Upload-Post services are not part of zero-cash MVP. `Codex` subscription access does not imply free API credits.
6. Do not claim `scripts/check.py` PASS proves rights, compliance, acceptance or funding. Check actual campaign rules and eligible payout route separately.
7. Keep customer and payout records locally in the app data directory. Don't expose them to Github Actions or public logs.
8. Prioritize quality of captions, creator consent, source attribution, natural hooks, accessibility, duration, retention and stable video/audio over automated volume.

Next development milestone: test a 60-second, creator-supplied video on Apple Silicon; compare vendor `cut.py` against OpenShorts crop/subtitles; remove optional paid APIs for the direct-service path; build human-review publication packages. Bring real benchmarks, not guesses.
