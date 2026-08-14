import assert from 'node:assert/strict';
import test from 'node:test';
import {
  buildImportPayload,
  buildSourceDeletedPayload,
  buildTocBody,
  canonicalRedditPostUrl,
  redditUrl,
} from './importer.ts';

test('normalizes Reddit permalinks without mangling external URLs', () => {
  assert.equal(redditUrl('/r/obsessionmovie/comments/abc/test/'), 'https://www.reddit.com/r/obsessionmovie/comments/abc/test/');
  assert.equal(redditUrl('https://redd.it/abc'), 'https://redd.it/abc');
  assert.equal(redditUrl('http://example.com/a'), 'http://example.com/a');
});

test('derives a stable source URL from the Reddit post id', () => {
  assert.equal(canonicalRedditPostUrl('t3_abc123'), 'https://www.reddit.com/comments/abc123');
});

test('credits author, subreddit and original post', () => {
  const body = buildTocBody({
    post: {
      id: 't3_abc',
      title: 'Theory',
      selftext: 'My actual theory.',
      permalink: '/r/obsessionmovie/comments/abc/theory/',
      url: 'https://example.com/article',
    },
    authorName: 'myusername',
    subredditName: 'obsessionmovie',
  });

  assert.match(body, /u\/myusername/);
  assert.match(body, /r\/obsessionmovie/);
  assert.match(body, /Original Reddit post/);
  assert.match(body, /My actual theory\./);
  assert.match(body, /\[Linked content\]\(https:\/\/example\.com\/article\)/);
});

test('renders Reddit images inline in TOC markdown', () => {
  const body = buildTocBody({
    post: {
      id: 't3_img',
      title: 'Image',
      permalink: '/r/obsessionmovie/comments/img/image/',
      url: 'https://i.redd.it/main.jpg',
      isImage: true,
      mediaUrls: ['https://i.redd.it/main.jpg'],
    },
    authorName: 'poster',
    subredditName: 'obsessionmovie',
  });

  assert.match(body, /!\[\]\(https:\/\/i\.redd\.it\/main\.jpg\)/);
  assert.doesNotMatch(body, /\[Linked content\]/);
});

test('builds a signed-webhook payload with the fixed Reddit source metadata', () => {
  const payload = buildImportPayload({
    post: {
      id: 't3_abc',
      title: 'Image post',
      permalink: '/r/obsessionmovie/comments/abc/image_post/',
      url: 'https://i.redd.it/example.jpg',
      nsfw: true,
      createdAt: 1760000000,
    },
    authorName: 'poster',
    subredditName: 'r/obsessionmovie',
  });

  assert.equal(payload.action, 'import');
  assert.equal(payload.source, 'reddit');
  assert.equal(payload.subreddit, 'obsessionmovie');
  assert.equal(payload.redditPostId, 't3_abc');
  assert.equal(payload.redditAuthor, 'poster');
  assert.equal(payload.over18, true);
  assert.equal(payload.createdUtc, 1760000000);
  assert.equal(payload.sourcePermalink, 'https://www.reddit.com/r/obsessionmovie/comments/abc/image_post/');
});

test('source deletion payload contains no copied Reddit content', () => {
  const payload = buildSourceDeletedPayload('t3_abc', 'obsessionmovie');
  assert.deepEqual(payload, {
    action: 'source_deleted',
    source: 'reddit',
    subreddit: 'obsessionmovie',
    redditPostId: 't3_abc',
  });
  assert.equal('title' in payload, false);
  assert.equal('body' in payload, false);
});

test('import payload has no TOC board or bot access token fields', () => {
  const payload = buildImportPayload({
    post: {
      id: 't3_abc',
      title: 'Theory',
      permalink: '/r/obsessionmovie/comments/abc/theory/',
    },
    authorName: 'poster',
    subredditName: 'obsessionmovie',
  });

  assert.equal('tocBoard' in payload, false);
  assert.equal('tocAccessToken' in payload, false);
});
