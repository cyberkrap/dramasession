# The Obsession Club — Project Context

This is the durable handoff document for future TOC development chats. It is intentionally **not** a transcript. Keep it compact, current, structured, and useful.

## Future-chat bootstrap instructions

Before making a non-trivial TOC change:

1. Read this file.
2. Inspect the current `obsession-rebrand` branch and the files relevant to the request.
3. Check recent commits/runtime logs when the issue concerns something recently changed.
4. Treat current code and runtime evidence as the source of truth when this file or an old chat disagrees.
5. Update this file after a major feature, architectural/workflow decision, or meaningful change in pending work.
6. Do not add every CSS tweak, temporary debugging theory, or micro-bugfix.

The user should not have to re-explain TOC history when a chat reaches the length limit. Reconstruct technical context from this file + the repository first.

## Repository / deployment baseline

- Repository: `cyberkrap/dramasession`
- Primary TOC branch: `obsession-rebrand`
- Stack: Python/Flask, PostgreSQL, Redis, JS/CSS frontend, Railway deployment.
- Current product name: **The Obsession Club (TOC)**.
- TOC is movie/community-oriented but supports boards for movies/topics beyond *Obsession*.

### Source priority

Use this order when resolving ambiguity:

1. Current branch code.
2. Current runtime/deployment/log evidence supplied by the user.
3. This file.
4. Recent commit history.
5. Old screenshots/chat descriptions.

For rDrama-inspired work, do not independently clone/scrape current rDrama behavior unless the user explicitly asks for research. When the user supplies rDrama screenshots/source as a reference, use those supplied materials for that requested comparison/sync.

## Working conventions

- Fix the real implementation instead of stacking blind CSS/JS band-aids on top of an unknown cause.
- Preserve TOC-specific behavior while fixing narrow bugs.
- Inspect current file content before writing.
- Prefer a single consolidated commit for one requested fix batch; avoid bursts of tiny Railway-triggering commits.
- Verify production-facing changes after committing and check Railway status rather than assuming a commit deployed successfully.
- Runtime source-repair helpers exist because this fork still contains large legacy files. Do not reactivate an older competing implementation merely because a helper looks unusual; first understand why it exists.

## Identity, profiles, houses, hats and username effects

### Houses

House membership is a real stored user property (`User.house`). Current base houses are Furry, Femboy, Vampire and Racist, with `... Founder` variants stored on users where applicable.

Canonical house artwork is present in the repository under `files/assets/images/rDrama/houses/`. TOC also carries the four base house assets under `files/assets/images/Obsession/houses/` so the existing `house_icon` filter can serve real TOC URLs instead of silently falling back to the default profile image.

Current intended identity UI:

- House identity behaves like another small account badge/checkmark: it is visible with post/comment author identity.
- **All post surfaces use the same `post_meta` house marker**: homepage, board feeds, profile post listings and full post threads. Do not create a separate listing-only/in-avatar house implementation.
- The house icon sits with the other metadata badges immediately before the verified checkmark; keep that pair compact and do not leave an oversized gap.
- The avatar and username remain a single contiguous author link. Never reserve a house slot between the avatar and username.
- Compact post-author profile pictures are intentionally nudged slightly upward to align with the username baseline; preserve that small alignment adjustment when changing metadata layout.
- Comments use the same house/checkmark badge concept.
- The profile identity header also shows the user's house icon alongside the other identity icons/checkmark.
- **Do not put the house icon in the navbar.**
- `install_toc_ui_fixes()` mutates legacy templates before route/template use and must clear Jinja's compiled template/bytecode caches afterward. Otherwise a listing can retain an older compiled `post_meta` import while a full thread compiles the repaired macro, producing the exact bug where the house badge appears only after opening a post.

### House-exclusive awards

`files/helpers/house_system.py` is installed during startup and is the canonical house-award mapping layer.

Intended access:

- **Furry → OwOify**
- **Femboy → Rainbow**
- **Racist → Early Life**
- **Vampire → no house-exclusive award currently**

Founder variants get the same house award with the existing founder discount. OwOify/Rainbow are not supposed to remain globally available to users outside the corresponding house. The Racist house-facing award title is **Early Life**.

### Username effects / patron rendering

Username effects belong on the username glyph/text span, not an outer wrapper. Compact UI locations previously produced rectangular duplicate animation layers when effects were applied to wrappers. Avoid broad page-wide mutation observers or duplicate outer registrations.

### Profile administration

Profile-level admin actions belong inside the existing profile moderation experience. Force username/reserved username, bio/CSS/media actions, bot controls and audit history are permission-gated. Wiping a reserved username should clear it rather than substituting placeholder text.

## Bots and automated accounts

### Crappy

Crappy is TOC's AI-powered native bot/account. On Crappy's own profile wall, users can interact without needing to `@Crappy`; normal mention/trigger behavior applies elsewhere. Provider/config code is under `files/helpers/crappy/`.

### Snatchy

Snatchy is the Reddit importer for `r/obsessionmovie`.

Intended V1 behavior:

- Mirror new submissions into TOC's Obsession board.
- Credit the Reddit author (`u/...`), subreddit and original Reddit post.
- Copy supported self-text/media and preserve NSFW state.
- Do not import Reddit comments.
- Reddit moderator removal does not automatically remove the TOC mirror; TOC moderation stays independent.
- Imported content must not accidentally trigger ordinary human progression/reward hooks or unrelated bots.
- TOC-side deduplication/mapping exists.

External blocker at the last confirmed checkpoint: Reddit Developer Portal still showed the HTTP Fetch domain exception for `theobsessionclub.com` as pending. Re-check the real status before assuming this remains pending later.

Possible later account-link behavior: a user may connect Reddit to TOC and explicitly opt in to mirroring their `r/obsessionmovie` posts directly onto their own TOC account instead of Snatchy.

## Admin roles and permissions

TOC role presets use explicit capability allowlists. Do not fall back to old inherited rDrama numeric thresholds as the intended role design.

Current preset hierarchy:

- **Trial Moderator:** remove/approve/pin/distinguish posts/comments and basic public-chat timeout moderation.
- **Moderator:** Trial tools plus routine bans/unbans, Chud/Unchud, mute/unmute, reports and ordinary content moderation. No Modmail, session/activity visibility, profile administration or site administration.
- **Administrator:** advanced moderation/investigation including shadowban, Modmail, alt-account/alt-vote tools, badge/flair tools, forced usernames/reserved names, private-profile visibility and domain safety controls.
- **Senior Administrator:** Administrator tools plus User Activity/session visibility, profile bio/CSS/media administration and wiping, bot controls, action reverts, API-app moderation, submitted/approved asset management, banners/sidebars and related operational tools.
- **Head Administrator:** effectively every active non-economy admin capability, including Admin Home toggles, security/Under Attack, DM-image audit, age-verification administration and site settings.
- **Head Administrator + Economy:** Head plus explicit Wishcoin/Wishbux economy authority and unlimited-spending/economy permissions.

`files/helpers/admin_role_presets.py` is the canonical explicit preset layer. Changing a user's current preset must never erase or hide their historical moderation-action total on `/admins`; mod-action totals are historical and role-independent.

## Chud terminology

**Chud** is canonical TOC terminology. Do not rename it to Restrict/Restriction again.

Canonical UI language:

- `Chud user`
- `Unchud`
- `Chudded Users`
- `Chud ends`
- `This account is chudded.`

The underlying legacy internal `agendaposter` field/key remains for compatibility. Admin Chud must also work from profile-wall comments, where `comment.post` can be `None`.

## User Activity

Admin Home exposes persistent authenticated **User Activity**.

- Records successful login/signup events and deduplicated authenticated `visit` events for already-logged-in users.
- A normal visit is approximately one row per account + UTC day + device/browser/IP identity, not every page click.
- Metadata can include exact time, IP, forwarded chain, Cloudflare country, device class/name, browser, OS, language and User-Agent.
- Never store passwords, cookies, session tokens or submitted form contents.
- Anonymous traffic is not assigned to an account history.
- Session/activity visibility is Senior-or-higher by preset.

The user rejected a large card-style redesign of the activity list; the simpler table-oriented UI was restored.

## Economy, Bank Statement and gifting

TOC uses Wishcoins and Wishbux, with shop, awards, gifts, gambling/casino and admin economy behavior.

Important invariants:

- Unlimited-spending admins can perform supported purchases/gifts without losing their own balance.
- Recipients still receive the real payout/gift and normal ledger entry.
- Gambling losses should not reduce an unlimited admin balance; wins may still increase it according to current mechanics.
- Hat and username-effect gifting are supported.
- `/transfers` formats amounts with thousands separators, including historical rendered rows.

### Bank Statement

The PostgreSQL `economy_ledger` trigger is authoritative for meaningful balance changes.

Automatic **+1 Wishcoin contribution/vote bookkeeping credits** are not meaningful user-facing banking transactions. The live balance change may remain, but those rows must not clutter Bank Statement. Historical matching rows are purged/hidden and future statement queries exclude them.

### Economy-history reset — 2026-08-22

The user explicitly requested a clean historical baseline after development/testing transfers and casino play polluted public stats.

Canonical reset behavior is defined through `files/helpers/bank_statement_noise_fixes.py` with UTC cutoff **1787360340**:

- This is **not a balance wipe**. Current user Wishcoin/Wishbux balances remain real.
- Current circulation rows on `/stats` therefore remain current-state totals.
- Cumulative shop spend and hat spend use persisted database baselines so public stats can start from the clean baseline without destroying users' underlying lifetime counters.
- Casino stats on `/stats` only include completed Blackjack, Slots and Roulette games at/after the reset cutoff.
- Casino `paid out` stats count positive player winnings only; old code incorrectly summed negative losses into payout totals and could display negative payouts.
- `@banman`'s pre-reset `economy_ledger` rows are deleted once via a migration key, so his Bank Statement starts clean while his balance is unchanged and future transactions continue recording normally.
- The reset/baseline mechanism is implementation detail: **public `/stats` labels must not say “since reset.”**
- Stats cache versioning must be bumped when changing reset semantics so stale snapshots do not survive deployment.

### Casino winner/loser reset

`files/helpers/casino.py` uses the same 2026-08-22 cutoff for **all three games**: Blackjack, Slots and Roulette.

- All-Time biggest winner / biggest loser cards start fresh from the reset cutoff.
- 24-hour cards also respect the reset cutoff.
- Historical `CasinoGame` rows are retained for audit/history/user stats; the reset is eligibility/filtering, not destructive deletion.
- Do not accidentally revert Roulette to lifetime history while Slots/Blackjack use the reset.

## Site Statistics and Houses pages

The live TOC stats controller is `files/routes/site_stats.py`; it intentionally replaces the legacy `/stats` endpoint after `static.py` registers the old route. `files/routes/house_pages.py` registers `/houses`, `/house/<house>` and `/houses/<house>`.

These modules must remain imported from `files/routes/__init__.py`. A previous failure created the files but never imported them, leaving `/stats` on the legacy controller.

`files/helpers/community_stats.py` is the structured stats source. When economy reset rules change, preserve the distinction between current-state metrics (circulation) and resettable historical counters, while keeping reset bookkeeping out of user-facing labels.

The activity charts use daily buckets for **30 days** and weekly buckets for **26 weeks**. They are interactive: moving the pointer across a chart snaps to the nearest bucket, shows a crosshair/point, and displays a compact tooltip with the full UTC date, exact value, and change versus the previous day/week. Keep this interaction lightweight and site-native rather than replacing Stats with oversized dashboard-card UI.

## Leaderboards

Leaderboards follow the rDrama-style interaction pattern supplied by the user: **one leaderboard per page**, not every leaderboard stacked vertically on one giant page.

Canonical structure:

- `/leaderboard` redirects to `/leaderboard/coins`.
- Individual metrics use `/leaderboard/<metric>`.
- A compact horizontal/wrapping metric navigation sits above one Top-25 table.
- Numeric values use thousands separators.
- The viewer's own row is shown below the Top 25 when they are outside the ranking.

Current TOC metrics include the existing Coins/Spent/Truescore/Followers/Posts/Comments/Awards/Badges/Blocked/Hats boards plus Wishbux, Designed hats, Emojis made, Upvotes given and Downvotes received. `/leaderboard/marseybux` may remain as a compatibility alias but TOC's public currency name is Wishbux.

## Awards

TOC awards are modernized incrementally from user specifications. Preserve internal legacy keys where required for historical rows/mechanics while exposing TOC-facing names.

### Naming

- User-facing `ban` / `unban` titles are **Ban** / **Unban**.
- Legacy `agendaposter` is publicly **Chud** with the intended 24-hour Chud behavior.

### Award effect renderer

`files/assets/js/award_effects.js` is intentionally disabled/no-op. `files/assets/js/award_effects_requested.js` is the sole current renderer. Do not casually reactivate the legacy renderer.

Effect rules:

- Large body effects such as Truth Nuke, Truth Nova and Love Bomb are clipped to post body/comment text, never metadata/action rows.
- Only the most recently awarded large animation plays.
- Furry, Ricardo, Emoji, Shit, Fireflies, Fireworks and Confetti are decorative exceptions and may coexist.
- Decorative roaming effects can use the whole awarded card where specified; large effects stay body-only.
- Large media uses proportional `object-fit: cover`, not stretched/tiled copies.
- Shit uses the fly sprite sheet and roaming flies; Fireflies roam across the card; Fireworks must never show broken-image placeholders.
- Giga Pin is visually distinct from ordinary/admin Pin (purple/violet).

### Emoji / Ricardo / Gold

- Emoji Award uses the legacy `wholesome` key, base price 100, with a selected emoji stored separately and rendered as the visible award effect.
- Ricardo uses the legacy `ricardo` key and is a small dancing/decorative effect.
- Gold is enabled at base price 500. It gilds awarded text and pays the recipient 250 Wishcoins per award when given by someone else. Batch quantities multiply the payout.

### Pin / Giga Pin

- Pin/Giga Pin/Unpin/Giga Unpin are content effects, not author effects.
- Award pin tooltip attribution must identify the actual giver and stable expiry/source, e.g. `Pinned by @name (Giga pin award) until ...`.
- Manual/admin pin attribution should identify the admin rather than degrading to `Pinned by (a site admin)`.
- Admin actions expose explicit `Pin for 1 hour` and `Pin permanently` choices.
- Pin awards stack by duration. Each normal Pin adds its configured duration; each Giga Pin adds another full Giga duration. For posts, 4 Giga Pins means 48 hours.

### Clear Awards

Admins have a **Clear Awards** moderation action for posts/comments. It removes every award relationship on that exact target, does not refund historical payouts, clears an award-created live pin where appropriate, invalidates relevant caches and records a mod action. Use the supported `fa-broom` icon in both dropdown and moderation log.

## Media / composer

Recent work includes comment composer media cleanup, chat GIF support, multi-image uploads and duplicate-control fixes. Test posts, comments and chat independently; they do not always share the same DOM/control path.

## Future plans / pending implementation

### Bleed-inspired TOC activity/utility bot — planned concept

The user wants to return to an all-in-one activity/utility/entertainment bot inspired by Bleed's breadth, not another moderation bot. Do not copy Bleed's private code/branding/assets; recreate useful capabilities as TOC-native features.

Candidate scope includes Last.fm/Spotify-style activity, trivia/chat games, levels/streaks, snipe/edit-history utilities with sensible retention/privacy, general media/utility commands, social integrations, automated activity feeds, giveaways/counters/scheduled activity and custom response/command concepts.

This is deferred until current site fixes are complete.

### Snatchy external approval

Reddit HTTP Fetch approval/domain exception was pending at the last confirmed checkpoint. Do not churn TOC importer code merely to poke the external review; re-check current status when resuming.

### Reddit account linking / opt-in mirroring

Potential Connections feature: link a TOC account to Reddit and let users opt in so their `r/obsessionmovie` posts mirror onto their own TOC identity instead of Snatchy.

### Shared media/chat ideas

Earlier roadmap ideas include richer public-chat media/music experiences and movie-streaming/watch-party style features. They are concepts, not assumptions about current production functionality; inspect current code before treating any of them as implemented.

## Maintenance note

When a future change materially alters one of these systems, update the relevant section rather than appending a chronological diary entry. Keep current code > this document whenever they disagree.
