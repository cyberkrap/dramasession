# Snatchy Privacy Policy

Last updated: August 14, 2026

Snatchy is a Reddit-to-The Obsession Club bridge for r/obsessionmovie. It copies new subreddit submissions into /b/obsession so discussion can continue on The Obsession Club (TOC).

## Data Snatchy processes

For a Reddit submission Snatchy may process the Reddit post ID, Reddit username, subreddit name, title, self-text, permalink, linked/media URLs, creation time, and NSFW/spoiler metadata exposed by Reddit's Devvit trigger.

Snatchy does not import Reddit comments, Reddit private messages, passwords, email addresses, or private account data.

## How the data is used

The copied submission is used only to create and maintain the corresponding TOC thread. TOC displays attribution to the original Reddit author and links back to the original Reddit submission.

TOC stores a small source mapping containing the Reddit post ID, the corresponding TOC submission ID, source author name, source permalink, and timestamps so duplicate deliveries can be ignored and source deletions can be honored.

## Deletions

If Reddit reports that the source submission was deleted by its author, Snatchy removes the copied Reddit title, body, source URL, and stored source attribution from TOC while preserving TOC-native comments already made on the discussion thread.

Subreddit moderator removals are not treated as author deletions and do not automatically delete the independent TOC discussion.

## Sharing and sale

Snatchy does not sell Reddit user data. The copied submission is sent only from Reddit Devvit to The Obsession Club at theobsessionclub.com for the bridge described above.

## Security

Requests from the Devvit app to TOC are authenticated with an HMAC-SHA256 signature and a short replay window. The shared signing secret is not included in the public source code.

## Contact

Questions about Snatchy or this policy can be raised through The Obsession Club's normal site moderation/contact channels.
