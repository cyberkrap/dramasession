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

Reddit installation settings:

- `toc_webhook_secret` — must equal `SNATCHY_WEBHOOK_SECRET`.
- `enabled` — optional; defaults to enabled.

## Fetch Domains

Snatchy makes outbound HTTPS requests only to `theobsessionclub.com`, specifically the TOC Snatchy ingestion endpoint used to deliver signed Reddit submission events.

## Data handling

See [PRIVACY.md](./PRIVACY.md) and [TERMS.md](./TERMS.md).

## Deployment

Unpublished Devvit uploads can only be installed on small test subreddits. Because `r/obsessionmovie` is over that limit, Snatchy must be published and reviewed by Reddit before it can be installed there.

1. Keep `SNATCHY_WEBHOOK_SECRET` configured on TOC.
2. Upload the current app version with `npx devvit upload`.
3. Add the Terms and Privacy URLs from this repository to the app details in the Reddit Developer Portal.
4. Run `npx devvit publish` to submit the unlisted app for review. Do not use `--public`; Snatchy is intended for `r/obsessionmovie`, not the public App Directory.
5. After approval, install with `npx devvit install obsessionmovie`.
6. Open the installation settings for `r/obsessionmovie`, set `toc_webhook_secret` to the same TOC secret, and leave `enabled` on.

There is no manual Snatchy account creation, TOC bot token, or board-name setting.
