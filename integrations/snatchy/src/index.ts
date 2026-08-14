import { createHmac } from 'node:crypto';
import { Hono } from 'hono';
import { serve } from '@hono/node-server';
import { createServer, getServerPort, settings } from '@devvit/web/server';
import type { OnPostDeleteRequest, OnPostSubmitRequest, TriggerResponse } from '@devvit/web/shared';
import {
  buildImportPayload,
  buildSourceDeletedPayload,
  type SnatchyDeletePayload,
  type SnatchyImportPayload,
} from './importer';

const TOC_ORIGIN = 'https://theobsessionclub.com';
const TOC_INGEST_URL = `${TOC_ORIGIN}/api/integrations/reddit/snatchy`;
const SOURCE_SUBREDDIT = 'obsessionmovie';
const app = new Hono();

function normalizedSubreddit(name: string | undefined): string {
  return (name || '').trim().replace(/^r\//i, '').toLowerCase();
}

async function getConfig(): Promise<{
  enabled: boolean;
  webhookSecret: string;
}> {
  const enabledSetting = await settings.get<string>('enabled');
  return {
    enabled: !enabledSetting || !['0', 'false', 'off', 'disabled'].includes(enabledSetting.toLowerCase()),
    webhookSecret: ((await settings.get<string>('toc_webhook_secret')) || '').trim(),
  };
}

async function sendWebhook(
  secret: string,
  payload: SnatchyImportPayload | SnatchyDeletePayload
): Promise<Response> {
  const body = JSON.stringify(payload);
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const signature = createHmac('sha256', secret)
    .update(`${timestamp}.`)
    .update(body)
    .digest('hex');

  return fetch(TOC_INGEST_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json;charset=UTF-8',
      Accept: 'application/json',
      'User-Agent': 'Snatchy/0.2 (The Obsession Club Reddit bridge)',
      'X-Snatchy-Timestamp': timestamp,
      'X-Snatchy-Signature': `sha256=${signature}`,
    },
    body,
  });
}

async function relay(
  secret: string,
  payload: SnatchyImportPayload | SnatchyDeletePayload
): Promise<{ ok: boolean; detail: string }> {
  try {
    const response = await sendWebhook(secret, payload);
    const detail = (await response.text().catch(() => '')).slice(0, 1000);
    return { ok: response.ok, detail: `${response.status} ${detail}`.trim() };
  } catch (error) {
    return { ok: false, detail: String(error) };
  }
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
  if (!config.webhookSecret) {
    console.error('Snatchy is missing toc_webhook_secret');
    return c.json<TriggerResponse>({ status: 'error' }, 500);
  }

  const payload = buildImportPayload({
    post,
    authorName,
    subredditName,
  });
  const result = await relay(config.webhookSecret, payload);

  if (!result.ok) {
    console.error(`Snatchy TOC import failed: ${result.detail}`);
    return c.json<TriggerResponse>({ status: 'error' }, 502);
  }

  console.log(`Snatchy imported Reddit post ${post.id}: ${result.detail}`);
  return c.json<TriggerResponse>({ status: 'ok' });
});

app.post('/internal/triggers/on-post-delete', async (c) => {
  const input = await c.req.json<OnPostDeleteRequest>();
  if (!input.postId) return c.json<TriggerResponse>({ status: 'ignored' });

  const subredditName = input.subreddit?.name?.trim() || SOURCE_SUBREDDIT;
  if (normalizedSubreddit(subredditName) !== SOURCE_SUBREDDIT) {
    return c.json<TriggerResponse>({ status: 'ignored' });
  }

  const config = await getConfig();
  if (!config.enabled) return c.json<TriggerResponse>({ status: 'ignored' });
  if (!config.webhookSecret) {
    console.error('Snatchy is missing toc_webhook_secret for source deletion handling');
    return c.json<TriggerResponse>({ status: 'error' }, 500);
  }

  const payload = buildSourceDeletedPayload(input.postId, subredditName);
  const result = await relay(config.webhookSecret, payload);

  if (!result.ok) {
    console.error(`Snatchy TOC source scrub failed: ${result.detail}`);
    return c.json<TriggerResponse>({ status: 'error' }, 502);
  }

  console.log(`Snatchy scrubbed deleted Reddit source ${input.postId}: ${result.detail}`);
  return c.json<TriggerResponse>({ status: 'ok' });
});

serve({
  fetch: app.fetch,
  createServer,
  port: getServerPort(),
});
