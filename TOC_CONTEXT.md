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
- Inspect current file content before writing; GitHub content writes require the current blob SHA and complete replacement content.
- Verify production-facing changes after committing and check Railway status rather than assuming a commit deployed successfully.
- Runtime source-repair helpers exist because this fork still contains large legacy files. Do not reactivate an older competing implementation merely because a helper looks unusual; first understand why it exists.

## Identity, profiles, houses, hats and username effects

### Houses

House membership is a real stored user property (`User.house`) and TOC has house assets under `files/assets/images/Obsession/houses/` for Femboy, Furry, Racist and Vampire. House UI must remain enabled; disabling the `HOUSES` feature flag hides existing memberships without deleting them.

Current intended UI:

- House icons render beside users where house identity is shown.
- The logged-in navbar identity block also shows the user's house icon beside the username.
- The navbar profile picture is aligned slightly upward so the avatar/hat stack lines up visually with the username plate.

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

External blocker: as of 2026-08-17, Reddit Developer Portal still showed the HTTP Fetch domain exception for `theobsessionclub.com` as **Pending**. Re-check the real status before assuming this remains pending later.

Possible later account-link behavior: a user may connect Reddit to TOC and explicitly opt in to mirroring their `r/obsessionmovie` posts directly onto their own TOC account instead of Snatchy.

### Bot admin controls

Supported native bots can be enabled/disabled and given daily post/comment limits. Usage counting is enforced on supported publication paths, and bot profile controls live with profile moderation rather than in a disconnected duplicate UI.

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

The user rejected a large card-style redesign of the activity list; the simpler table-oriented UI was restored. Avoid reintroducing oversized sparse activity cards without an explicit request.

## Economy, Bank Statement and gifting

TOC uses Wishcoins and Wishbux, with shop, awards, gifts, gambling/casino and admin economy behavior.

Important invariants:

- Unlimited-spending admins can perform supported purchases/gifts without losing their own balance.
- Recipients still receive the real payout/gift and normal ledger entry.
- Gambling losses should not reduce an unlimited admin balance; wins may still increase it according to current mechanics.
- Hat and username-effect gifting are supported.
- `/transfers` formats amounts with thousands separators, including historical rendered rows.

### Bank Statement noise rule

Automatic **+1 Wishcoin contribution credits** associated with creating a post/comment are not meaningful user-facing banking transactions. The real +1 reward may still affect the live balance, but those rows must not clutter Bank Statement. Historical matching contribution-credit rows are removed/hidden and future statement queries exclude them. Do not convert them back into generic `Balance credit` rows.

The immutable economy ledger remains authoritative for meaningful balance changes; caller/request metadata is used to classify awards, gifts, shop purchases, casino activity, patron rewards, etc.

## Leaderboards

Leaderboards follow the rDrama-style interaction pattern supplied by the user: **one leaderboard per page**, not every leaderboard stacked vertically on one giant page.

Canonical structure:

- `/leaderboard` redirects to `/leaderboard/coins`.
- Individual metrics use `/leaderboard/<metric>`.
- A compact horizontal/wrapping metric navigation sits above one Top-25 table.
- Numeric values use thousands separators.
- The viewer's own row is shown below the Top 25 when they are outside the ranking.

Current TOC metrics include the existing Coins/Spent/Truescore/Followers/Posts/Comments/Awards/Badges/Blocked/Hats boards plus:

- **Wishbux**
- **Designed hats**
- **Emojis made** (approved authored emotes)
- **Upvotes given** (post + comment upvotes)
- **Downvotes received** (post + comment downvotes received)

`/leaderboard/marseybux` may remain as a compatibility alias but TOC's public currency name is Wishbux.

## Awards

TOC awards are modernized incrementally from user specifications. Preserve internal legacy keys where they are required for historical rows/mechanics while exposing TOC-facing names.

### Shop naming

The user-facing `ban` and `unban` award titles are simply **Ban** and **Unban**. Their internal keys and 1-day mechanics remain unchanged; do not rename the internal ban-reason strings used to recognize award-issued bans unless the mechanic itself is being migrated.

The legacy `agendaposter` award is publicly **Chud** with the intended 24-hour Chud behavior.

### Award effect renderer

`files/assets/js/award_effects.js` is intentionally disabled/no-op. `files/assets/js/award_effects_requested.js` is the sole current renderer. Do not casually reactivate the legacy renderer; competing renderers previously moved/deleted one another's nodes and broke effects.

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
- Pin awards stack by duration. Each normal Pin adds its configured duration; each Giga Pin adds another full Giga duration. For posts, 4 Giga Pins means 4 × 12 hours = 48 hours. Concurrent/batched awards must not lose increments.

### Clear Awards

Admins have a **Clear Awards** moderation action for posts/comments. It removes every award relationship on that exact target, does not refund historical payouts, clears an award-created live pin where appropriate, invalidates relevant caches and records a mod action. The supported broom icon (`fa-broom`) is used in both the dropdown and moderation log.

## Media / composer

Recent work includes comment composer media cleanup, chat GIF support, multi-image uploads and duplicate-control fixes. Test posts, comments and chat independently; they do not always share the same DOM/control path.

## Future plans / pending implementation

This section is for unresolved future work only. Move/remove entries when implemented or abandoned.

### Bleed-inspired TOC activity/utility bot — planned concept

The user wants to return to an all-in-one **activity/utility/entertainment bot inspired by Bleed's breadth**, not another moderation bot. Do not copy Bleed's private code/branding/assets; recreate useful capabilities as TOC-native features.

Candidate scope discussed so far:

- Last.fm / Spotify-style music activity and now-playing/profile stats.
- Trivia and chat games.
- Levels/streaks/leaderboards tied into TOC where appropriate.
- Snipe/edit-history style chat utilities subject to sensible retention/privacy boundaries.
- General utility/media commands.
- Social/account integrations and automated activity feeds.
- Giveaways, counters, scheduled activity and custom response/command concepts.

This is explicitly deferred for now; the user said to return to it after current site fixes.

### Snatchy external approval — pending external dependency

Reddit HTTP Fetch approval/domain exception was still pending at last check. Do not churn TOC-side importer code merely to poke the external review. Re-check current status when resuming Snatchy work.

### Reddit account linking / opt-in mirroring — future

Potential Connections feature: link a TOC account to Reddit and let users opt in so their `r/obsessionmovie` posts mirror onto their own TOC identity instead of the Snatchy bot.

### Shared media/chat ideas — future concept

Earlier roadmap ideas include richer public-chat media/music experiences and movie-streaming/watch-party style features. They are concepts, not assumptions about current production functionality; inspect current code before treating any of them as implemented.

## Maintenance note

When a future change materially alters one of these systems, update the relevant section rather than appending a chronological diary entry. Keep current code > this document whenever they disagree.
