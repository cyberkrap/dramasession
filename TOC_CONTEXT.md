# The Obsession Club — Project Context

This file is the durable handoff/context document for future TOC development chats. It is **not** a conversation transcript and should never become one.

## Future-chat bootstrap instructions

Before making non-trivial changes to TOC:

1. Read this file first.
2. Inspect the current `obsession-rebrand` branch and the files relevant to the requested change.
3. Check recent commits when the request concerns something recently implemented or debugged.
4. Treat the live code/repository as the source of truth when this file and an old chat disagree.
5. Update this file after a major feature, architectural change, important workflow decision, or meaningful change in pending work.
6. Do **not** add every bugfix, chat message, temporary debugging theory, or micro-commit here. Keep this file compact, structured, and useful.

When starting a new TOC chat, the user should not have to re-explain prior TOC chats. Reconstruct the needed technical context from this file + the repository before asking questions that the code can answer.

## Repository / deployment baseline

- Repository: `cyberkrap/dramasession`
- Primary TOC branch: `obsession-rebrand`
- Application: Python/Flask community/forum application with PostgreSQL, Redis, JS/CSS frontend assets, Docker-based setup, and Railway production deployment.
- Current public product name: **The Obsession Club (TOC)**.
- TOC is movie/community-oriented but is not limited to the movie *Obsession*; it supports boards for other topics/movies too.

### Context-source priority

For implementation decisions, use this order:

1. Current code on `obsession-rebrand`.
2. Current database/runtime/deployment behavior and logs supplied by the user.
3. This `TOC_CONTEXT.md`.
4. Recent Git commit history.
5. Screenshots / old chat descriptions.

Do not blindly reimplement something merely because an old screenshot/chat says it existed.

## Working rules / project decisions

- Prefer inspecting and fixing the real implementation over adding CSS/JS band-aids on top of a misunderstood bug.
- Do not redesign unrelated systems while fixing a specific issue.
- Preserve existing TOC-specific behavior unless the user explicitly asks to change it.
- For rDrama-inspired features, **do not independently scrape, reconstruct, or copy current rDrama behavior unless the user explicitly asks for research**. The normal workflow is: the user describes the feature/award, price, behavior/effect/assets/rules, then implement that specification in TOC.
- When the user explicitly supplies rDrama screenshots/source and asks for a sync/comparison, those supplied materials are the source of truth for that requested sync; do not silently substitute unrelated rDrama research.
- When modifying production-facing code, keep changes narrow enough to identify regressions and check the relevant existing implementation first.
- Do not assume a deployment is healthy merely because code was committed; use the deployment/log evidence available at the time.

## Bots and automated accounts

### Crappy

- Crappy is TOC's AI-powered interactive bot/account.
- It is designed to behave as a TOC-native bot rather than a generic detached AI interface.
- On Crappy's own profile wall, users should be able to interact without needing to `@Crappy`; elsewhere normal mention/trigger behavior applies.
- Crappy provider/config code exists under `files/helpers/crappy/`.

### Snappy and other native bots

TOC already contains multiple bot/system identities (including Snappy and other legacy/native bot emitters). Admin bot controls should apply consistently to supported bot profiles.

### Bot admin controls

Implemented starting with commit `9830dd3` and subsequent fixes:

- Admins can enable/disable bot output.
- Admins can set daily post limits.
- Admins can set daily comment limits.
- Usage counts are tracked/enforced for supported bot publication paths.
- Bot profile customization/admin controls are integrated into profile moderation rather than living in a disconnected duplicate admin UI.

## Snatchy — Reddit → TOC importer

Snatchy is the Reddit importer bot for `r/obsessionmovie`.

Initial importer commit: `a5b2b957`.

### Intended V1 behavior

- Mirror new submissions from `r/obsessionmovie` into TOC's Obsession board.
- TOC post is published by the Snatchy system account when no direct user-account mapping is involved.
- Imported content must visibly credit the original Reddit author (`u/...`), subreddit, and original Reddit post.
- Copy Reddit self-text and supported media exposed by the trigger.
- Display Reddit images inline when possible.
- Carry Reddit NSFW state into TOC's `over_18` state.
- Do **not** import Reddit comments.
- Reddit moderator removals do **not** automatically remove the mirrored TOC post. TOC moderation is independent.
- Author deletion/source-deletion handling may remove copied source content while preserving the native TOC discussion thread.
- Imported content must not accidentally trigger normal human progression/reward hooks or unrelated bots.
- Durable deduplication/mapping exists on the TOC side in the later Snatchy implementation.

### Possible future account-link behavior

A later feature may allow a user to connect their TOC and Reddit accounts and explicitly opt in to mirroring their `r/obsessionmovie` submissions directly onto their own TOC account rather than Snatchy. This is a future concept, not the V1 assumption.

### Current external blocker

As of **2026-08-17**, Reddit Developer Portal still shows the HTTP Fetch domain exception for `theobsessionclub.com` as **Pending**. Snatchy's TOC-side work should not be repeatedly rewritten just to poke that review queue. Re-check current Reddit status before assuming this is still pending in a future chat.

Relevant review-preparation commits include `c8d5bf7`, `14220be`, and `0731397`.

## User/profile administration and moderation

Recent work expanded profile-level moderation/admin tooling.

Important behavior:

- Admin profile controls belong inside the existing moderation tools experience rather than a separate unrelated admin section.
- User moderation history is associated with the target user's profile/activity and should show administrative/moderation actions relevant to that user.
- Profile actions include bot controls and profile/identity administration where permissions allow.
- Moderation/audit logging should distinguish meaningful actions (for example editing a bio versus wiping it entirely) rather than recording misleading generic labels.
- Administrator permissions should be kept in sync when new admin/moderation capabilities are introduced.

### Username administration semantics

- Force-changing a username should preserve the user's old username as the reserved/original username where that system expects it.
- Wiping the reserved username should actually clear/release that reserved value, not invent placeholder text such as `None`.
- Username rendering/effects are sensitive to patron/non-patron state and have had regressions across compact renderers; inspect the current renderer/effect engine before modifying it.

Key related commits include `7d3d320`, `79837fe`, `f4b7841`, `23a3437`, `c1cae08`, `ffba35d`, `14df2e6`, `e979803`, and `37251d2`.

## Administrator roles and User Activity

The old inherited numeric rDrama permission thresholds are **not** the intended TOC role definitions anymore. TOC role presets use explicit capability allowlists so low-level staff do not accidentally inherit unrelated privacy, profile, modmail, asset, or site-administration powers.

Current role model:

- **Trial Moderator:** probationary content moderation only — remove/approve/pin/distinguish posts and comments plus public-chat timeout controls.
- **Moderator:** routine moderation — Trial tools plus bans/unbans, Chud/restriction and mute actions, report cleanup, and normal moderator notifications. No Modmail, session/activity data, profile administration, or site administration.
- **Administrator:** advanced moderation/investigation — Moderator tools plus shadowbans, Modmail, alt-account and alt-vote analysis, badge/flair management, forced usernames/reserved-name controls, private-profile visibility, and domain safety controls.
- **Senior Administrator:** operational administration — Administrator tools plus User Activity/session visibility, profile bio/CSS/media administration and wiping, bot controls, action reverts, API-app moderation, submitted/approved asset management, and banner/sidebar asset management.
- **Head Administrator:** every active non-economy TOC admin permission, including site settings/toggles, security/Under Attack controls, DM image audit, age-verification administration, and all normal Admin Home controls.
- **Head Administrator + Economy:** Head access plus explicit Wishcoin/Wishbux economy authority and unlimited-spending/economy permissions.

`files/helpers/admin_role_presets.py` is the canonical explicit preset layer. Existing accounts that exactly matched the old generated Moderator/Administrator/Senior presets are migrated once to the new allowlists; genuinely custom permission sets are left unchanged rather than guessed.

### User Activity semantics

Admin Home exposes **User Activity** as the persistent authenticated-account activity view.

- It includes successful `login` and `signup` events plus normal `visit` events for members who were already authenticated when they opened the site.
- This fixes the old blind spot where year-long sessions never appeared unless the user explicitly logged in again.
- Normal browsing is deduplicated to approximately one `visit` row per account + UTC day + device/browser/IP identity instead of writing a row for every page request.
- Activity metadata can include time, IP, forwarded IP chain, Cloudflare country, device class/name, browser, OS, language header, and User-Agent.
- Passwords, cookies, session tokens, and submitted form contents are never stored in the activity table.
- Anonymous traffic is not attached to an account history because there is no authenticated user identity to associate it with.
- Access is a Senior-or-higher capability through `VIEW_ACTIVE_USERS`; ordinary Moderators and Administrators should not receive session/activity visibility by preset.

The main User Activity page has a responsive scan-oriented event-card UI with compact stats, date/search controls, network/device grouping, source badges, and collapsible request metadata; keep future UI changes responsive and avoid returning to a very wide dense table.

## Economy / gifting

- TOC has Wishcoins/currency, shop/economy behavior, gambling/casino behavior, and admin economy capabilities.
- Admin unlimited-currency behavior should allow sending arbitrary currency gifts without deducting the admin's balance.
- The recipient should still receive the normal gift transaction/statement entry.
- The unlimited admin's own bank statement should not be polluted by normal outgoing purchase/gift deductions that did not actually affect the balance.
- Gambling losses should not reduce an unlimited admin balance, while wins may still increase it according to the implemented rules.
- Username effects can be gifted.
- Hat gifting was added in commits `48a0f22` / `bc95e07`; owned hats can be transferred to another user and arrive unequipped.

## Username effects / patron rendering

A substantial TOC 9 debugging pass fixed patron/non-patron username-effect rendering in compact UI locations such as DMs, tables, lists, popovers, votes/profile viewers, and dynamic usernames.

Important invariant:

- The effect belongs on the username glyph/text span, not on an outer wrapper that can render the animated asset as a rectangular background.
- Do not reintroduce broad page-wide MutationObservers or wrapper styling that causes performance churn or duplicate effect layers.
- Profile-page behavior is a useful reference because it was already rendering correctly while compact renderers were broken.

The duplicate rectangle issue was fixed by ensuring compact usernames resolve to the inner glyph span and clearing duplicate outer-wrapper registrations.

## Media / composer work

Recent fixes include:

- Comment composer media-control cleanup.
- Chat GIF support.
- Duplicate media-control fixes / selector specificity fixes.
- Restored multi-image composer uploads (`55d4276`).

When changing composer media behavior, verify posts, comments, and chat separately instead of assuming they share identical DOM/control paths.

## Awards

TOC's award system is being modernized incrementally from user-provided specifications. Do not automatically sync/research rDrama awards unless the user explicitly requests it.

### rDrama price baseline (explicit sync)

On **2026-08-17**, the user supplied screenshots of the current rDrama Awards Shop and explicitly requested price synchronization for awards TOC already implements.

- The **crossed-out values** in those screenshots are treated as rDrama's base prices.
- The green values are account-specific discounted prices and must **not** be copied as TOC's base prices.
- Overlapping TOC awards are normalized at startup in `files/helpers/award_system_fixes.py` via `rdrama_base_prices`, preserving TOC's existing internal keys/renamed titles.
- This price-only sync does not imply that TOC should automatically copy missing rDrama awards or their mechanics. The user will choose missing awards to add.
- Price-baseline commit: `8326ce2b`.

### Live catalog retirements / Chud restoration

On **2026-08-17**, the user explicitly retired several unwanted legacy awards from TOC's live catalog:

- `shit` / **Spark Trail**
- `marsify` / **Spotlight**
- `beano` / **Beano**
- `offsitementions` / **Y'all Seein' Eye**

These keys are removed from `AWARDS_ENABLED` at startup so they no longer appear in the shop or Give Award flow. Their historical rows/keys are preserved so old awarded content/history is not broken by deletion.

The legacy internal key `agendaposter` must publicly be **Chud**, not `Restrict`. Its intended shop description is **“Chuds the recipient for 24 hours.”** The underlying Chud mechanics in the award route already use the original `agendaposter`/chud behavior and should not be renamed away again.

Catalog cleanup/restoration commit: `bd8f7dff`.

### Emoji Award

The old `Wholesome` award was repurposed/renamed into **Emoji Award**.

Current intended behavior:

- Base price: 100.
- Giver selects an emoji before completing the award.
- Selected emoji becomes the visible award icon on the target post/comment.
- Multiple Emoji Awards can coexist/multiply based on quantity/givers rather than collapsing incorrectly.
- Tooltip should identify the selected emoji name as well as giver/date information.
- Emoji picker is stacked over the Give Award modal; closing/selecting in the emoji picker should not incorrectly close/reset the award modal.

Relevant commits: `473c15b`, `8c9db35`, `08756eb`, `df141c4`.

### Ricardo Award

The old `Celebration` award was repurposed/renamed into **Ricardo**.

Current intended visual behavior is the animated Ricardo/Ricardo-TV effect described by the user rather than the old fixed corner placement. Ricardo is a **small decorative/dancing effect** and is allowed to coexist with Furry, Emoji, and the currently-active large/full-body effect.

### Gold Award

Gold was added from the user's supplied rDrama reference/source rather than independently researched.

Current intended behavior:

- Base price: 500.
- Gold is a first-class enabled award catalog entry so it appears normally in the Awards Shop and Give Award picker instead of depending only on runtime injection order.
- The catalog description should match the user-supplied rDrama wording, including its Reddit wording unless the user later asks to adapt it for TOC.
- Each Gold award pays the recipient **250 Wishcoins** when another user gives it; self-awarding does not produce the recipient payout.
- Quantity/batch giving scales the payout by 250 per Gold and summarizes the total payout in the recipient notification.
- The visual effect is deliberately the normal Gold effect: **gild the awarded post/comment text only**. It does not bathe the whole card in a large golden glow; that broader treatment belongs to a separate Giga Gold-style effect if added later.
- Gold uses the normal Font Awesome vector icon system (`fas fa-coins`, warning/gold color) so it stays visually consistent and crisp in the shop, Give Award picker, and awarded-content metadata.

Implementation commits: `ee4ae80a`, `7e51d97f`, `7b48adda`, `518db91e`, `d78d126b`, `e7136bbc`, `cd2af16b`.

### Requested awards / effect semantics

By **2026-08-18**, the requested-award pass added/restored Furry, Shit, Truth Nuke, Love Bomb, Truth Nova, Giga Pin, and Giga Unpin, with their user-specified pricing/mechanics/assets.

Important effect rules:

- Large/full-body animation effects are clipped to the exact post body/comment text container and must never cover the metadata/action rows (Votes, Give Award, Copy Link, Save, Report, etc.).
- Large effects are **mutually exclusive**. If several large animation awards exist on the same target, only the **most recently awarded large effect** plays.
- Truth Nuke, Truth Nova, Love Bomb, Shit and equivalent legacy large effects participate in that newest-large-effect arbitration.
- **Furry, Ricardo, and Emoji are exceptions**: they are small decorative/dancing effects, may coexist with each other, and may overlap the currently-active large effect. They are still clipped to the exact awarded content container so they cannot leak into replies/action rows.
- Truth Nuke/Nova/Love Bomb use one proportional `object-fit: cover` media layer rather than stretched/tiled copies.
- Award timestamps and encoded giver metadata are emitted in award icon classes so client behavior does not depend on mutable Bootstrap tooltip attributes.

Key commits for the latest semantics include `a2cf47f`, `510b4e4`, and `64e6560`.

### Pin / Giga Pin semantics

- Pin, Unpin, Giga Pin, and Giga Unpin belong under **Effect on Content**, not Effect on Author.
- Giga Pin must remain visually distinct from the ordinary/admin pin (purple/violet treatment).
- Generic pin tooltip format should identify both source and expiry, e.g. `Pinned by @username (Giga pin award) until <date>` or `Pinned by @username (Pin award) until <date>`.
- The tooltip must not alternate between source-only and expiry-only states on repeated hover.
- When a Pin/Giga Pin is awarded through AJAX, the tooltip must recompute from persisted award metadata rather than keeping a stale cached admin/source value.

### Award-effect lifecycle invariant

Opening/giving/closing an award must not destroy, hide, duplicate, or permanently pause effects already active on the post/comment. The current renderer separates **small decorative effects** from the **single active large effect** so modal/AJAX lifecycle updates can reconcile each layer independently.

## Current checkpoint / pending work

Current award-system checkpoint as of **2026-08-18**:

- Spark Trail, Spotlight, Beano, and Y'all Seein' Eye are retired from the live award catalog while historical award records remain intact.
- `agendaposter` is publicly Chud again, with the original 24-hour Chud semantics preserved.
- Overlapping active awards use the user-supplied rDrama shop's crossed-out/base prices; discounted green prices were intentionally ignored.
- Gold costs 500, is present in the normal award catalog/shop, uses the normal vector coin icon, gilds only the exact awarded target's text, and pays a fixed 250 Wishcoins per award to a non-self recipient.
- Large award animations now use newest-effect arbitration and body-only containment; Furry/Ricardo/Emoji intentionally coexist as small decorations.
- Pin/Giga Pin are content effects and their tooltip/source metadata is being kept explicit and durable.
- The user is choosing which rDrama awards missing from TOC should be implemented next; do not add the rest automatically.
- Snatchy domain exception is externally pending with Reddit as of 2026-08-17.

## How to maintain this file

Update this document when one of these happens:

- A major feature is completed or fundamentally redesigned.
- A persistent architectural rule/invariant is discovered.
- A major pending blocker changes state.
- A project workflow decision changes.
- A feature's intended semantics change in a way future chats need to know.

Do **not** update it for:

- Every commit hash.
- Every CSS tweak.
- Temporary debugging guesses.
- Railway build noise that was subsequently resolved.
- Raw conversation summaries.
- Long chronological chat recaps.

Keep sections organized by subsystem. Replace stale statements instead of endlessly appending contradictory history. If a section gets too large, summarize the stable final behavior and retain only the most useful checkpoint commits.