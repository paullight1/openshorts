# GTA VI clipping — Zero-extra-spend revenue pilot (19 Nov 2026)

Owner: paullight1. State: implementation prototype. Nobody has earned or withdrawn money from this branch. No posts, DMs or paid subscriptions have been created on the user's behalf.

## What is in this branch?

1. Existing OpenShorts code is preserved; do not merge to main without review.
2. integrations/gtavi-claudecode is an MIT-licensed **git submodule** pointing to Bodila51/gtavi-claudecode at commit dd95d393c6f74fe2ac14b0239f8826691e5dcb0e. This pins the original upstream source; it is NOT a separate GitHub fork, and the submodule contents require a separate checkout.
3. tools/clip_business.py is a Python standard-library, local-first source permission / campaign / video rendering / lead / payment ledger tool. It never downloads content, publishes, sends DMs, spends money or claims a view estimate is a receipt.
4. tests/test_clip_business.py tests relevant blocking and accounting behavior offline.
5. AGENTS.md explains the safety limits and Codex workflow.

## Our commercial strategy

**Fastest plausible cash path: fixed-price creator work.** Offer to turn an already-produced creator-owned interview, podcast or authorized stream into 5 professionally edited vertical clips. A test offer to Nigerian clients is ₦25,000–₦50,000 for five clips, with 50% deposit before a batch and two correction rounds. This is an experimental offer, not a verified market rate. Five short clips at ₦10,000 each means ₦50,000 gross revenue **only if a customer actually pays**. With international customers, test a $50–$100 entry package only after confirming a legally supported receiving method.

**Second path: paid campaigns.** Find campaigns only on their authoritative pages, read the full briefs, verify approved media/source, and check the real Nigerian payout route before producing. Content Rewards relies on Whop for withdrawals. Nigeria was not found on Whop's public payout-country list at the time of review; DO NOT use fake location or bank details. Rates, minimum qualifying views, per-clip caps, fees and budgets change. An example campaign page: https://contentrewards.com/c/campaigns/051002dd-5c46-43d0-a446-43f2957ba3a9 — its brief may contain locked requirements and the visible rate can change. Never treat gross CPM estimates as cash received.

**Third path: a long-term original GTA commentary channel.** Use YouTube Shorts, TikTok and Instagram Reels for real audience growth. Create genuinely new commentary, explanation, critique and useful tutorials from properly licensed media. Do not build an ad-revenue forecast on duplicate gameplay or passive reposting. YouTube's reused-content rules and gaming publisher rights still apply, and ad monetization thresholds are significant.

### First 72 hours

**Day 1:** use current M1 + Codex; choose a portfolio brand and create one genuine creator-service page. Test local clipping on properly authorized footage. Search for 10-15 content creators who publish long streams or interviews but few strong Shorts. Confirm the creator's permission, sources, music, and commercial-use rights; obtain clear agreement in writing. Verify a legitimate way to get paid.

**Day 2:** create 2-3 clean sample clips for one permission-granting creator with different hooks, accurate subtitles, credit and clean audio. Offer an affordable five-clip fixed-price trial and invoice before bulk work. Use real, non-manipulated engagement; send targeted outreach manually. Do not mass spam creators.

**Day 3:** approach 20 more suitable creators. Publish only content you have rights to and human approval for. Track outreach attempts, replies, trial orders, completed clips, hours spent and **received** revenue. Improve creative quality and target fit before increasing posting volume.

Target funnel to test, not a guarantee: 30 personalized introductions -> 5 replies -> 2 trials. If two customers each buy a ₦30,000 trial, that is ₦60,000 gross, before costs and taxes. Report zero cash until funds are actually received.

### M1 installation

~~~
git clone --recurse-submodules https://github.com/paullight1/openshorts.git
cd openshorts
git checkout feat/gta6-clip-ops-20261119
git submodule update --init --recursive
brew install ffmpeg                  # only if it is not already installed
python3 -m unittest discover -s tests -p test_clip_business.py -v
python3 tools/clip_business.py report
~~~

To experiment with upstream trend discovery after you have the required Python environment, work inside integrations/gtavi-claudecode, create a .venv and install requirements.txt. Do NOT run upstream moment downloading or live recording against unlicensed streams. You can use local authorized media.

### Zero-cost local proof of workflow

~~~
python3 tools/clip_business.py source-add \
  --file "$HOME/Movies/creator-authorized.mp4" \
  --creator "Creator Example" --permission-ref "signed-creator-email-001" \
  --scope clip-service

# Replace YOUR_SOURCE_ID with the ID printed above.
python3 tools/clip_business.py render \
  --source YOUR_SOURCE_ID --start 12 --seconds 20 \
  --title "Moment explained" --platform instagram

python3 tools/clip_business.py lead-add \
  --handle "@example" --platform instagram --offer 30000

python3 tools/clip_business.py payment-record \
  --party "Actual customer" --amount 15000 --currency NGN \
  --reference "actual-bank-payment-reference" --status received

python3 tools/clip_business.py report
~~~

The CLI's FFmpeg renderer letterboxes into 1080x1920 / 30fps and outputs local MP4 and metadata for HUMAN review. It does not yet create burned word-by-word captions. For finished content, use the existing OpenShorts editor or the pinned upstream subtitle/cut scripts after authorized source processing. Only mark a payment received after checking the bank/provider. Data is stored outside the repo under ~/.local/share/openshorts-ops; never commit receipts, ID, tokens or source recordings.

## Upstream code audit

- Good foundation: 16 instruction skills and scripts for YouTube trends, stream discovery, scoring energetic moments, subtitle/caption rendering, media checks and projected payouts. Repo is MIT; respect its copyright notice.
- Unverified: claimed automatic 10-minute setup, native M1 performance, real viral hit rate, successful Nigerian withdrawals, monetization and author authorization.
- Important gap: scripts/moments.py may download video from URL without a rights gate; scripts/check.py can pass its **technical default** checks without a real campaign brief; scripts/payouts.py records **estimated**, not settled payouts; not all campaign terms are accessible without joining. The new wrapper explicitly blocks campaign-linked renders unless operator records payout eligibility and verified rules.
- A creator's permission to use their recording does NOT automatically clear Rockstar game rights, soundtrack rights or platform rules.
- OpenShorts' full app uses external Gemini/voice/publishing APIs and is not necessarily cost-free in every mode; this pilot is Python standard library + FFmpeg.

## Non-negotiables

No leaks, spoiler dishonesty, copyrighted soundtracks without rights, impersonation, fake reviews or bought views. Never auto-publish or run DMs without human authorization. Keep eligibility and campaign rules separately confirmed. Apply sponsored-content disclosures where required. YouTube YPP policies prohibit minimally modified reused content. Rockstar's ordinary fan policy expressly covers non-commercial material and reserves takedown rights, so commercial uses require independent legal review/permissions.

## Monitoring questions before reinvestment

- Can the user verify an accepted Nigerian withdrawal method (without falsification) before clipping paid campaigns?
- How many personalized outreach attempts produced genuine replies and paid trials?
- What is the processing time and quality on the real M1 (CPU, RAM, storage, sync, caption accuracy)?
- Did the client approve final deliverables and did cleared payment arrive?
- Does a clip add substantial original value, and are its underlying footage and audio actually authorized?

## Source links to recheck before acting

- Upstream toolkit: https://github.com/Bodila51/gtavi-claudecode
- Rockstar commercial-content position: https://support.rockstargames.com/articles/7bNaeoMFTV0iUDGhStTXvz/policy-on-posting-copyrighted-rockstar-games-material
- YouTube gaming rights: https://support.google.com/youtube/answer/138161
- YouTube reused content: https://support.google.com/youtube/answer/1311392
- YouTube YPP requirements: https://support.google.com/youtube/answer/72851
- Whop supported payout-country list: https://docs.whop.com/manage-your-business/manage-payouts/set-up-payouts
- Content Rewards withdrawal steps: https://help.contentrewards.com/en/articles/16817239-withdraw-your-earnings
