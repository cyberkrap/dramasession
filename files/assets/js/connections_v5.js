(() => {
	'use strict';

	const ICONS = {
		github: 'fab fa-github', reddit: 'fab fa-reddit', twitch: 'fab fa-twitch',
		youtube: 'fab fa-youtube', x: 'fab fa-x-twitter', xbox: 'fab fa-xbox',
		playstation: 'fab fa-playstation', bluesky: 'fas fa-cloud', roblox: 'fas fa-cube',
		battlenet: 'fas fa-gamepad',
	};

	const MARKS = {
		spotify: '<svg class="connection-brand-icon" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.493 17.307a.75.75 0 0 1-1.032.249c-2.824-1.726-6.38-2.116-10.562-1.158a.75.75 0 1 1-.335-1.462c4.58-1.048 8.511-.6 11.68 1.337a.75.75 0 0 1 .249 1.034zm1.46-3.247a.938.938 0 0 1-1.29.309c-3.234-1.988-8.163-2.564-11.986-1.402a.938.938 0 1 1-.545-1.794c4.371-1.328 9.802-.685 13.514 1.596a.938.938 0 0 1 .307 1.291zm.125-3.385C15.2 8.372 8.79 8.16 5.078 9.287a1.125 1.125 0 1 1-.653-2.153c4.263-1.293 11.342-1.044 15.8 1.64a1.125 1.125 0 0 1-1.147 1.901z"/></svg>',
		discord: '<svg class="connection-brand-icon" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M19.2 5.3A16.4 16.4 0 0 0 15.1 4l-.5 1a15 15 0 0 0-5.2 0l-.5-1a16.4 16.4 0 0 0-4.1 1.3C2.2 9.1 1.5 12.8 1.8 16.4a16.7 16.7 0 0 0 5.1 2.6l1.2-1.6a10.4 10.4 0 0 1-1.9-.9l.5-.4c3.6 1.7 7.5 1.7 11.1 0l.5.4c-.6.4-1.3.7-1.9.9l1.2 1.6a16.7 16.7 0 0 0 5.1-2.6c.4-4.1-.7-7.8-3.5-11.1zM8.5 14.7c-1 0-1.9-1-1.9-2.2s.8-2.2 1.9-2.2 1.9 1 1.9 2.2-.9 2.2-1.9 2.2zm7 0c-1 0-1.9-1-1.9-2.2s.8-2.2 1.9-2.2 1.9 1 1.9 2.2-.9 2.2-1.9 2.2z"/></svg>',
		steam: '<svg class="connection-brand-icon" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 0a12 12 0 0 0-12 11.4l6.45 2.66a3.4 3.4 0 0 1 1.94-.62l2.87-4.16v-.06a4.55 4.55 0 1 1 4.55 4.55h-.1l-4.08 2.91a3.42 3.42 0 0 1-6.68 1.04L.37 15.83A12 12 0 1 0 12 0zM8.36 18.92a2.56 2.56 0 0 1-2.37-1.58l1.45.6a1.89 1.89 0 1 0 1.45-3.49l-1.5-.62c.3-.11.62-.17.97-.17a2.63 2.63 0 0 1 0 5.26zm7.45-6.67a3.03 3.03 0 1 1 0-6.06 3.03 3.03 0 0 1 0 6.06zm0-.76a2.27 2.27 0 1 0 0-4.54 2.27 2.27 0 0 0 0 4.54z"/></svg>',
		epicgames: '<img class="connection-brand-image" src="/i/Obsession/connections/epicgames.svg" alt="">',
		github: '<i class="fab fa-github connection-brand-font" aria-hidden="true"></i>',
	};

	let currentUser = '';
	let loadedUser = '';
	let loadingUser = '';
	let requestId = 0;
	let controller = null;
	let refreshTimer = 0;
	let retryTimer = 0;
	let progressTimer = 0;
	let initQueued = false;

	function usernameFromPage() {
		const marker = document.getElementById('username');
		if (marker && marker.textContent.trim()) return marker.textContent.trim();
		const match = window.location.pathname.match(/^\/@([^/]+)/);
		if (!match) return '';
		try { return decodeURIComponent(match[1]); }
		catch (_) { return match[1]; }
	}

	function isProfilePage() {
		return Boolean(document.body && usernameFromPage() && (
			document.body.id === 'userpage' || /^\/@[^/]+\/?$/.test(window.location.pathname)
		));
	}

	function safeUrl(value) {
		try {
			const url = new URL(String(value || ''), window.location.origin);
			return ['http:', 'https:'].includes(url.protocol) ? url.href : '';
		} catch (_) { return ''; }
	}

	function normalText(node) {
		return String(node && node.textContent || '').replace(/\s+/g, ' ').trim().toUpperCase();
	}

	function sectionAround(heading) {
		let node = heading && heading.parentElement;
		for (let depth = 0; node && node !== document.body && depth < 7; depth += 1, node = node.parentElement) {
			if (node.matches('section, article, .card, .profile-panel, .userpage-section, [class*="profile-section"]')) return node;
			const style = window.getComputedStyle(node);
			if (node.children.length > 1 && style.borderStyle !== 'none' && parseFloat(style.borderWidth || '0') > 0) return node;
		}
		return heading && heading.parentElement && heading.parentElement.parentElement;
	}

	function getMount() {
		let mount = document.getElementById('profile-connections-mount');
		const headings = Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6,.card-header,strong'));
		const badgeHeading = headings.find(node => ['BADGES', 'AWARDS RECEIVED'].includes(normalText(node)));
		const badgeSection = sectionAround(badgeHeading);

		if (!mount && badgeSection && badgeSection.parentElement) {
			mount = document.createElement('div');
			mount.id = 'profile-connections-mount';
			mount.className = 'profile-connections-mount';
			mount.setAttribute('aria-live', 'polite');
			badgeSection.parentElement.insertBefore(mount, badgeSection);
		}
		if (!mount) return null;
		if (badgeSection && badgeSection.parentElement && mount.nextElementSibling !== badgeSection) {
			badgeSection.parentElement.insertBefore(mount, badgeSection);
		}
		return mount;
	}

	function mark(connection) {
		const provider = String(connection.provider || '').toLowerCase();
		if (MARKS[provider]) return MARKS[provider];
		const icon = String(ICONS[provider] || connection.icon || 'fas fa-link').replace(/[^a-zA-Z0-9 _-]/g, '');
		return `<i class="${icon} connection-brand-font" aria-hidden="true"></i>`;
	}

	function providerIcon(connection) {
		const icon = document.createElement('span');
		icon.className = `connection-provider-icon connection-provider-${String(connection.provider || '').toLowerCase()}`;
		icon.innerHTML = mark(connection);
		return icon;
	}

	function heading(panel, canManage) {
		const header = document.createElement('div');
		header.className = 'profile-panel__heading';
		const title = document.createElement('h2');
		title.textContent = 'Connections';
		header.append(title);
		if (canManage) {
			const manage = document.createElement('a');
			manage.className = 'profile-connections-manage';
			manage.href = '/settings/connections';
			manage.innerHTML = '<i class="fas fa-cog" aria-hidden="true"></i><span>Manage</span>';
			header.append(manage);
		}
		panel.append(header);
	}

	function shell(username) {
		const mount = getMount();
		if (!mount) return null;
		let panel = document.getElementById('profile-connections-panel');
		if (!panel) {
			panel = document.createElement('section');
			panel.id = 'profile-connections-panel';
			panel.className = 'profile-panel profile-connections-panel';
		}
		if (panel.parentElement !== mount) mount.append(panel);
		panel.dataset.connectionsUser = username;
		return panel;
	}

	function showLoading(username) {
		const panel = shell(username);
		if (!panel || panel.dataset.loadingFor === username) return;
		panel.dataset.loadingFor = username;
		panel.replaceChildren();
		heading(panel, false);
		const loading = document.createElement('div');
		loading.className = 'profile-connections-loading';
		loading.innerHTML = '<span></span><span></span><span></span>';
		panel.append(loading);
	}

	function connectionRow(connection) {
		const href = safeUrl(connection.profile_url);
		const row = document.createElement(href ? 'a' : 'div');
		row.className = 'profile-connection-link';
		if (href) {
			row.href = href;
			row.target = '_blank';
			row.rel = 'nofollow noopener';
		}
		row.append(providerIcon(connection));
		const copy = document.createElement('span');
		copy.className = 'profile-connection-copy';
		const name = document.createElement('strong');
		name.textContent = connection.display_name || connection.provider_label || 'Connected account';
		const provider = document.createElement('small');
		provider.textContent = connection.provider_label || connection.provider || 'Connection';
		copy.append(name, provider);
		row.append(copy);
		if (connection.verified) {
			const verified = document.createElement('i');
			verified.className = 'fas fa-badge-check profile-connection-verified';
			verified.title = 'Verified connection';
			row.append(verified);
		}
		return row;
	}

	function activityRow(activity) {
		if (!activity || !activity.title) return null;
		const href = safeUrl(activity.external_url);
		const row = document.createElement(href ? 'a' : 'div');
		row.className = `profile-live-activity${activity.provider === 'steam' ? ' is-steam' : ''}`;
		if (href) {
			row.href = href;
			row.target = '_blank';
			row.rel = 'nofollow noopener';
		}
		const art = document.createElement('img');
		art.className = 'profile-live-art';
		art.loading = 'lazy';
		art.alt = '';
		art.src = safeUrl(activity.image_url) || '/i/Obsession/official-logo.png';
		art.addEventListener('error', () => { art.src = '/i/Obsession/official-logo.png'; }, {once: true});
		row.append(art);
		const copy = document.createElement('span');
		copy.className = 'profile-live-copy';
		const label = document.createElement('span');
		label.className = 'profile-live-label';
		label.textContent = activity.label || 'Live activity';
		const title = document.createElement('strong');
		title.className = 'profile-live-title';
		title.textContent = activity.title;
		const subtitle = document.createElement('span');
		subtitle.className = 'profile-live-subtitle';
		subtitle.textContent = activity.subtitle || '';
		copy.append(label, title, subtitle);
		if (Number(activity.duration_ms) > 0) {
			const progress = document.createElement('span');
			progress.className = 'profile-live-progress';
			const fill = document.createElement('span');
			fill.dataset.progressMs = String(activity.progress_ms || 0);
			fill.dataset.durationMs = String(activity.duration_ms || 0);
			fill.dataset.checkedUtc = String(activity.checked_utc || Math.floor(Date.now() / 1000));
			progress.append(fill);
			copy.append(progress);
		}
		row.append(copy);
		return row;
	}

	function updateProgress() {
		document.querySelectorAll('.profile-live-progress > span').forEach(fill => {
			const duration = Number(fill.dataset.durationMs || 0);
			if (!duration) return;
			const initial = Number(fill.dataset.progressMs || 0);
			const checked = Number(fill.dataset.checkedUtc || 0) * 1000;
			const current = Math.min(duration, initial + Math.max(0, Date.now() - checked));
			fill.style.width = `${Math.max(0, Math.min(100, current / duration * 100))}%`;
		});
	}

	function render(payload, username) {
		const mount = getMount();
		if (!mount) return false;
		const data = Array.isArray(payload.data) ? payload.data : [];
		let panel = document.getElementById('profile-connections-panel');
		if (!data.length) {
			if (panel) panel.remove();
			return true;
		}
		panel = shell(username);
		if (!panel) return false;
		delete panel.dataset.loadingFor;
		panel.replaceChildren();
		heading(panel, Boolean(payload.can_manage));
		const list = document.createElement('div');
		list.className = 'profile-connections-list';
		data.forEach(connection => list.append(connectionRow(connection)));
		panel.append(list);
		data.map(item => item.activity).filter(item => item && item.title).forEach(activity => {
			const row = activityRow(activity);
			if (row) panel.append(row);
		});
		updateProgress();
		return true;
	}

	function scheduleRefresh(seconds) {
		window.clearTimeout(refreshTimer);
		refreshTimer = window.setTimeout(() => {
			loadedUser = '';
			loadConnections(true);
		}, Math.max(20, Number(seconds || 40)) * 1000);
	}

	async function loadConnections(force = false) {
		if (!isProfilePage() || document.hidden) return;
		const username = usernameFromPage();
		if (!username || !getMount()) {
			window.clearTimeout(retryTimer);
			retryTimer = window.setTimeout(() => queueInit(true), 100);
			return;
		}
		if (!force && (loadedUser === username || loadingUser === username)) return;

		currentUser = username;
		loadingUser = username;
		showLoading(username);
		requestId += 1;
		const version = requestId;
		if (controller) controller.abort();
		controller = new AbortController();
		const active = controller;
		const timeout = window.setTimeout(() => active.abort(), 8000);

		try {
			const response = await fetch(`/api/profile/${encodeURIComponent(username)}/connections`, {
				headers: {'Accept': 'application/json'}, credentials: 'same-origin',
				cache: 'no-store', signal: active.signal,
			});
			if (!response.ok) throw new Error(`Connections request failed: ${response.status}`);
			const payload = await response.json();
			if (version !== requestId || username !== usernameFromPage()) return;
			if (render(payload, username)) {
				loadedUser = username;
				loadingUser = '';
				scheduleRefresh(payload.refresh_seconds || 40);
			}
		} catch (_) {
			if (version === requestId) {
				loadingUser = '';
				window.clearTimeout(retryTimer);
				retryTimer = window.setTimeout(() => loadConnections(true), 1500);
			}
		} finally {
			window.clearTimeout(timeout);
			if (controller === active) controller = null;
		}
	}

	function initialize(force = false) {
		if (!isProfilePage()) return;
		const username = usernameFromPage();
		const changed = username !== currentUser;
		if (changed) {
			currentUser = username;
			loadedUser = '';
			loadingUser = '';
		}
		if (!getMount()) {
			window.clearTimeout(retryTimer);
			retryTimer = window.setTimeout(() => queueInit(true), 100);
			return;
		}
		if (force || changed || (loadedUser !== username && loadingUser !== username)) loadConnections(force);
		if (!progressTimer) progressTimer = window.setInterval(updateProgress, 1000);
	}

	function queueInit(force = false) {
		if (initQueued) return;
		initQueued = true;
		window.requestAnimationFrame(() => {
			initQueued = false;
			initialize(force);
		});
	}

	['pushState', 'replaceState'].forEach(method => {
		const original = history[method];
		if (original.__connectionsWrapped) return;
		const wrapped = function (...args) {
			const result = original.apply(this, args);
			window.dispatchEvent(new Event('obsession:navigation'));
			return result;
		};
		wrapped.__connectionsWrapped = true;
		history[method] = wrapped;
	});

	const observer = new MutationObserver(() => {
		if (!isProfilePage()) return;
		const username = usernameFromPage();
		const mount = document.getElementById('profile-connections-mount');
		const panel = document.getElementById('profile-connections-panel');
		if (!mount || username !== currentUser || (!panel && loadedUser !== username && loadingUser !== username)) queueInit(false);
	});
	observer.observe(document.documentElement, {childList: true, subtree: true});

	document.addEventListener('visibilitychange', () => { if (!document.hidden) queueInit(true); });
	window.addEventListener('pageshow', () => queueInit(true));
	window.addEventListener('popstate', () => queueInit(true));
	window.addEventListener('obsession:navigation', () => queueInit(true));

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', () => queueInit(true), {once: true});
	} else {
		queueInit(true);
	}
})();