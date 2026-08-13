import assert from 'node:assert/strict';
import test from 'node:test';
import {
  buildDeletedSourceEditForm,
  buildTocBody,
  buildTocForm,
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

test('uses the Reddit id URL as the unique TOC URL and carries NSFW', () => {
  const form = buildTocForm({
    post: {
      id: 't3_abc',
      title: 'Image post',
      permalink: '/r/obsessionmovie/comments/abc/image_post/',
      url: 'https://i.redd.it/example.jpg',
      nsfw: true,
    },
    authorName: 'poster',
    subredditName: 'obsessionmovie',
    tocBoard: 'obsession',
  });

  assert.equal(form.get('url'), 'https://www.reddit.com/comments/abc');
  assert.equal(form.get('sub'), 'obsession');
  assert.equal(form.get('over_18'), '1');
});

test('author deletion edit keeps the TOC thread but removes copied content', () => {
  const form = buildDeletedSourceEditForm();
  assert.equal(form.get('title'), '[Deleted Reddit post]');
  assert.doesNotMatch(form.get('body') || '', /u\//);
  assert.match(form.get('body') || '', /TOC discussion is preserved/);
});
