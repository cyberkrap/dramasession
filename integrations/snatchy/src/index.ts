import { Hono } from 'hono';
import { serve } from '@hono/node-server';
import { createServer, getServerPort, redis, settings } from '@devvit/web/server';
import type { OnPostDeleteRequest, OnPostSubmitRequest, TriggerResponse } from '@devvit/web/shared';
import { buildDeletedSourceEditForm, buildTocForm } from './importer';

const TOC_ORIGIN = 'https://theobsessionclub.com';
const TOC_SUBMIT_URL = `${TOC_ORIGIN}/submit`;
const SOURCE_SUBREDDIT = 'obsessionmovie';
const app = new Hono();

function normalizedSubreddit(name: string | undefined): string {
  return (name || '').trim().replace(/^r\//i, '').toLowerCase();
}

async function getConfig(): Promise<{
  enabled: boolean;
  tocBoard: string;
  tocAccessToken: string;
}> {
  const enabledSetting = await settings.get<string>('enabled');
  return {
    enabled: !enabledSetting || !['0', 'false', 'off', 'disabled'].includes(enabledSetting.toLowerCase()),
    tocBoard: ((await settings.get<string>('toc_board')) || '')
      .trim()
      .replace(/^\/(?:b|h)\//i, ''),
    tocAccessToken: ((await settings.get<string>('toc_access_token')) || '').trim(),
  };
}

app.post('/internal/triggers/on-post-submit', async (c) => {
  const input = await c.req.json<OnPostSubmitRequest>();
  const post = input.post;
  const authorName = input.author?.name?.trim();
  const subredditName = input.subreddit?.name?.trim();

  if (!post?.id || !post.title || !post.permalink || !authorName || !subredditName) {
    console.warn('Snatchy ignored incomplete post-submit event');
    return c.json<TriggerResponse>({ status: 'ignored' });
  }

  if (normalizedSubreddit(subredditName) !== SOURCE_SUBREDDIT) {
    return c.json<TriggerResponse>({ status: 'ignored' });
  }

  const config = await getConfig();
  if (!config.enabled) return c.json<TriggerResponse>({ status: 'ignored' });
  if (!config.tocBoard || !config.tocAccessToken) {
    console.error('Snatchy is missing toc_board or toc_access_token');
    return c.json<TriggerResponse>({ status: 'error' }, 500);
  }

  const dedupeKey = `snatchy:toc-post:${post.id}`;
  if (await redis.get(dedupeKey)) {
    return c.json<TriggerResponse>({ status: 'ok' });
  }

  const form = buildTocForm({
    post,
    authorName,
    subredditName,
    tocBoard: config.tocBoard,
  });

  try {
    const response = await fetch(TOC_SUBMIT_URL, {
      method: 'POST',
      headers: {
        Authorization: config.tocAccessToken,
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        Accept: 'application/json',
        'User-Agent': 'Snatchy/0.1 (The Obsession Club Reddit bridge)',
      },
      body: form.toString(),
    });

    if (!response.ok) {
      const detail = (await response.text().catch(() => '')).slice(0, 500);
      console.error(`Snatchy TOC import failed (${response.status}): ${detail}`);
      return c.json<TriggerResponse>({ status: 'error' }, 502);
    }

    const created = (await response.json().catch(() => null)) as { id?: number } | null;
    if (!created?.id || !Number.isInteger(created.id)) {
      console.error('Snatchy TOC import succeeded but did not return a post id');
      return c.json<TriggerResponse>({ status: 'error' }, 502);
    }

    await redis.set(dedupeKey, String(created.id));
    console.log(`Snatchy imported Reddit post ${post.id} as TOC post ${created.id}`);
    return c.json<TriggerResponse>({ status: 'ok' });
  } catch (error) {
    console.error('Snatchy TOC import request failed', error);
    return c.json<TriggerResponse>({ status: 'error' }, 502);
  }
});

// Devvit uses onPostDelete for author deletions. Moderator removals are separate
// moderator actions, so removing a submission from r/obsessionmovie does not
// remove or hide the independent TOC thread.
app.post('/internal/triggers/on-post-delete', async (c) => {
  const input = await c.req.json<OnPostDeleteRequest>();
  if (!input.postId) return c.json<TriggerResponse>({ status: 'ignored' });

  const dedupeKey = `snatchy:toc-post:${input.postId}`;
  const tocPostId = await redis.get(dedupeKey);
  if (!tocPostId || !/^\d+$/.test(tocPostId)) {
    return c.json<TriggerResponse>({ status: 'ignored' });
  }

  const config = await getConfig();
  if (!config.tocAccessToken) {
    console.error('Snatchy is missing toc_access_token for source deletion handling');
    return c.json<TriggerResponse>({ status: 'error' }, 500);
  }

  try {
    const response = await fetch(`${TOC_ORIGIN}/edit_post/${tocPostId}`, {
      method: 'POST',
      headers: {
        Authorization: config.tocAccessToken,
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'User-Agent': 'Snatchy/0.1 (The Obsession Club Reddit bridge)',
      },
      body: buildDeletedSourceEditForm().toString(),
      redirect: 'follow',
    });

    if (!response.ok) {
      const detail = (await response.text().catch(() => '')).slice(0, 500);
      console.error(`Snatchy TOC source scrub failed (${response.status}): ${detail}`);
      return c.json<TriggerResponse>({ status: 'error' }, 502);
    }

    await redis.set(dedupeKey, `scrubbed:${tocPostId}`);
    console.log(`Snatchy scrubbed author-deleted Reddit post ${input.postId} from TOC post ${tocPostId}`);
    return c.json<TriggerResponse>({ status: 'ok' });
  } catch (error) {
    console.error('Snatchy TOC source scrub request failed', error);
    return c.json<TriggerResponse>({ status: 'error' }, 502);
  }
});

serve({
  fetch: app.fetch,
  createServer,
  port: getServerPort(),
});
