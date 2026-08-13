# Snatchy

Snatchy mirrors every new submission from `r/obsessionmovie` into a configured board on The Obsession Club.

It intentionally uses TOC's existing authenticated `/submit` route instead of creating a second posting system. Posts are published by the Snatchy TOC account, but the body always credits the Reddit author, `r/obsessionmovie`, and the original Reddit post.

## V1 behavior

- Mirrors new Reddit submissions to one TOC board.
- Copies self-text and attached/linked media where the trigger exposes it.
- Displays Reddit images inline in the TOC body.
- Maps Reddit NSFW to TOC's `over_18` flag.
- Does not import Reddit comments.
- Does not mirror subreddit moderator removals. TOC moderation stays independent.
- Handles author deletion separately: Snatchy edits the mirrored post to remove the copied Reddit title/body while preserving the TOC comment thread.
- Stores the created TOC post id in Devvit Redis for deduplication and author-deletion handling.

## Required settings

Snatchy reads these global app settings with `@devvit/web/server`:

- `toc_access_token` — access token for the Snatchy TOC bot/application.
- `toc_board` — destination board name only, without `/b/` or `/h/`.
- `enabled` — optional; `0`, `false`, `off`, or `disabled` disables imports. Any other/missing value enables them.

The source is deliberately hard-coded to `r/obsessionmovie` for V1.

## Human setup still required

1. Create/configure the `Snatchy` TOC account and issue an app/access token for it.
2. Create the Reddit Devvit app from this directory.
3. Set `toc_access_token` and `toc_board` with the Devvit CLI/settings UI.
4. Playtest/install the app and approve `theobsessionclub.com` for HTTP Fetch if Reddit asks for domain review.

## Known V1 limitation

TOC currently limits normal user post edits after one week. Because author-deletion cleanup reuses TOC's existing edit route, deleting a Reddit source more than one week later may require TOC-side cleanup or a future narrowly scoped Snatchy cleanup endpoint. This does not affect normal importing.
