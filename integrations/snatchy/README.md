# Snatchy

Snatchy mirrors every new submission from `r/obsessionmovie` into `/b/obsession` on The Obsession Club.

The TOC web process bootstraps the `Snatchy` system account automatically. The Reddit app never logs in as a normal TOC user and never needs a TOC access token. Instead, Devvit sends a signed JSON webhook to TOC, and TOC creates the native post as `@Snatchy`.

## V1 behavior

- Mirrors new Reddit submissions from `r/obsessionmovie` to `/b/obsession`.
- Credits the original Reddit author and links the original submission.
- Copies self-text and attached/linked media exposed by the trigger.
- Displays Reddit images inline in the TOC body.
- Maps Reddit NSFW to TOC's `over_18` flag.
- Does not import Reddit comments.
- Does not sync TOC comments back to Reddit.
- Uses a TOC-side `snatchy_imports` mapping table for durable deduplication.
- On Reddit `PostDelete`, removes the copied Reddit title/body/URLs from TOC while preserving the TOC thread and its native comments.
- Does not call the normal human post hooks, so imported content does not accidentally award human progression/rewards or invoke Snappy/Crappy.

## Security

Devvit signs the exact JSON request body with HMAC-SHA256:

`HMAC(secret, "<unix timestamp>.<raw request body>")`

TOC checks the signature and rejects requests outside a five-minute replay window. The shared secret is never committed.

TOC environment:

- `SNATCHY_WEBHOOK_SECRET` — required before imports can run.
- `SNATCHY_BOARD` — optional destination override; defaults to `obsession`.

Devvit global app setting:

- `toc_webhook_secret` — must equal `SNATCHY_WEBHOOK_SECRET`.
- `enabled` — optional; `0`, `false`, `off`, or `disabled` disables imports.

## Human setup still required

1. Put a long random value in Railway as `SNATCHY_WEBHOOK_SECRET`.
2. From this directory, create/login to the Devvit app and set the same value with `npx devvit settings set toc_webhook_secret`.
3. Playtest/install the app on `r/obsessionmovie`.
4. Complete Reddit's external HTTP/domain review for `theobsessionclub.com` if prompted.

There is no manual Snatchy account creation, TOC bot token, or board-name setting.
