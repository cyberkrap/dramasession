export type RedditPostEvent = {
  id?: string;
  title?: string;
  selftext?: string;
  permalink?: string;
  url?: string;
  nsfw?: boolean;
  isSpoiler?: boolean;
  isImage?: boolean;
  isGallery?: boolean;
  isVideo?: boolean;
  mediaUrls?: string[];
  galleryImages?: string[];
  createdAt?: number;
};

export type SnatchyImportPayload = {
  action: 'import';
  source: 'reddit';
  subreddit: string;
  redditPostId: string;
  redditAuthor: string;
  sourcePermalink: string;
  createdUtc?: number;
  title: string;
  body: string;
  over18: boolean;
};

export type SnatchyDeletePayload = {
  action: 'source_deleted';
  source: 'reddit';
  subreddit: string;
  redditPostId: string;
};

export function redditUrl(pathOrUrl: string): string {
  if (/^https?:\/\//i.test(pathOrUrl)) return pathOrUrl;
  const path = pathOrUrl.startsWith('/') ? pathOrUrl : `/${pathOrUrl}`;
  return `https://www.reddit.com${path}`;
}

export function canonicalRedditPostUrl(postId: string): string {
  const id = postId.trim().replace(/^t3_/i, '');
  if (!id) throw new Error('Reddit post has no id');
  return `https://www.reddit.com/comments/${encodeURIComponent(id)}`;
}

function safeMarkdownLabel(value: string): string {
  return value.replace(/[\\[\]]/g, '\\$&');
}

function uniqueUrls(urls: (string | undefined)[]): string[] {
  return urls
    .map((url) => (url || '').trim())
    .filter(Boolean)
    .filter((url, index, all) => all.indexOf(url) === index);
}

export function buildTocBody(args: {
  post: RedditPostEvent;
  authorName: string;
  subredditName: string;
}): string {
  const { post, authorName, subredditName } = args;
  const permalink = redditUrl(post.permalink || `/r/${subredditName}/`);
  const authorUrl = `https://www.reddit.com/user/${encodeURIComponent(authorName)}`;
  const subredditUrl = `https://www.reddit.com/r/${encodeURIComponent(subredditName)}`;

  const credit = `Originally posted by [u/${safeMarkdownLabel(authorName)}](${authorUrl}) on [r/${safeMarkdownLabel(subredditName)}](${subredditUrl}) · [Original Reddit post](${permalink})`;
  const parts = [credit];

  const text = (post.selftext || '').trim();
  if (text) parts.push(text);

  const originalUrl = (post.url || '').trim();
  const media = uniqueUrls([...(post.galleryImages || []), ...(post.mediaUrls || [])]);

  if (post.isImage || post.isGallery) {
    const images = uniqueUrls([originalUrl, ...media]).filter((url) => redditUrl(url) !== permalink);
    if (images.length) parts.push(images.map((url) => `![](${url})`).join('\n\n'));
  } else {
    if (originalUrl && redditUrl(originalUrl) !== permalink) {
      parts.push(`[Linked content](${originalUrl})`);
    }
    const extraMedia = media.filter((url) => url !== originalUrl);
    if (extraMedia.length) {
      parts.push(extraMedia.map((url, index) => `[Media ${index + 1}](${url})`).join('\n'));
    }
  }

  if (post.isSpoiler) parts.push('*Marked as spoiler on Reddit.*');

  return parts.join('\n\n');
}

export function buildImportPayload(args: {
  post: RedditPostEvent;
  authorName: string;
  subredditName: string;
}): SnatchyImportPayload {
  const { post, authorName, subredditName } = args;
  if (!post.title?.trim()) throw new Error('Reddit post has no title');
  if (!post.permalink?.trim()) throw new Error('Reddit post has no permalink');
  if (!post.id?.trim()) throw new Error('Reddit post has no id');

  const payload: SnatchyImportPayload = {
    action: 'import',
    source: 'reddit',
    subreddit: subredditName.trim().replace(/^r\//i, ''),
    redditPostId: post.id.trim(),
    redditAuthor: authorName.trim(),
    sourcePermalink: redditUrl(post.permalink),
    title: post.title.trim(),
    body: buildTocBody({ post, authorName, subredditName }),
    over18: Boolean(post.nsfw),
  };

  if (Number.isFinite(post.createdAt)) {
    payload.createdUtc = post.createdAt;
  }

  return payload;
}

export function buildSourceDeletedPayload(
  postId: string,
  subredditName: string
): SnatchyDeletePayload {
  if (!postId.trim()) throw new Error('Reddit post has no id');
  return {
    action: 'source_deleted',
    source: 'reddit',
    subreddit: subredditName.trim().replace(/^r\//i, ''),
    redditPostId: postId.trim(),
  };
}
