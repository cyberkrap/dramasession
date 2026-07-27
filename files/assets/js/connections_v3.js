(() => {
	'use strict';

	const PROVIDER_ICONS = {
		github: 'fab fa-github',
		reddit: 'fab fa-reddit',
		twitch: 'fab fa-twitch',
		youtube: 'fab fa-youtube',
		x: 'fab fa-x-twitter',
		xbox: 'fab fa-xbox',
		playstation: 'fab fa-playstation',
		bluesky: 'fas fa-cloud',
		roblox: 'fas fa-cube',
		battlenet: 'fas fa-gamepad',
	};

	const PROVIDER_MARKS = {
		spotify: '<svg class="connection-brand-icon" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.493 17.307a.75.75 0 0 1-1.032.249c-2.824-1.726-6.38-2.116-10.562-1.158a.75.75 0 1 1-.335-1.462c4.58-1.048 8.511-.6 11.68 1.337a.75.75 0 0 1 .249 1.034zm1.46-3.247a.938.938 0 0 1-1.29.309c-3.234-1.988-8.163-2.564-11.986-1.402a.938.938 0 1 1-.545-1.794c4.371-1.328 9.802-.685 13.514 1.596a.938.938 0 0 1 .307 1.291zm.125-3.385C15.2 8.372 8.79 8.16 5.078 9.287a1.125 1.125 0 1 1-.653-2.153c4.263-1.293 11.342-1.044 15.8 1.64a1.125 1.125 0 0 1-1.147 1.901z"/></svg>',
		discord: '<svg class="connection-brand-icon" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M19.2 5.3A16.4 16.4 0 0 0 15.1 4l-.5 1a15 15 0 0 0-5.2 0l-.5-1a16.4 16.4 0 0 0-4.1 1.3C2.2 9.1 1.5 12.8 1.8 16.4a16.7 16.7 0 0 0 5.1 2.6l1.2-1.6a10.4 10.4 0 0 1-1.9-.9l.5-.4c3.6 1.7 7.5 1.7 11.1 0l.5.4c-.6.4-1.3.7-1.9.9l1.2 1.6a16.7 16.7 0 0 0 5.1-2.6c.4-4.1-.7-7.8-3.5-11.1zM8.5 14.7c-1 0-1.9-1-1.9-2.2s.8-2.2 1.9-2.2 1.9 1 1.9 2.2-.9 2.2-1.9 2.2zm7 0c-1 0-1.9-1-1.9-2.2s.8-2.2 1.9-2.2 1.9 1 1.9 2.2-.9 2.2-1.9 2.2z"/></svg>',
		steam: '<svg class="connection-brand-icon" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 0a12 12 0 0 0-12 11.4l6.45 2.66a3.4 3.4 0 0 1 1.94-.62l2.87-4.16v-.06a4.55 4.55 0 1 1 4.55 4.55h-.1l-4.08 2.91a3.42 3.42 0 0 1-6.68 1.04L.37 15.83A12 12 0 1 0 12 0zM8.36 18.92a2.56 2.56 0 0 1-2.37-1.58l1.45.6a1.89 1.89 0 1 0 1.45-3.49l-1.5-.62c.3-.11.62-.17.97-.17a2.63 2.63 0 0 1 0 5.26zm7.45-6.67a3.03 3.03 0 1 1 0-6.06 3.03 3.03 0 0 1 0 6.06zm0-.76a2.27 2.27 0 1 0 0-4.54 2.27 2.27 0 0 0 0 4.54z"/></svg>',
		epicgames: '<img class="connection-brand-image" src="/i/Obsession/connections/epicgames.svg" alt="">',
		github: '<i class="fab fa-github connection-brand-font" aria-hidden="true"></i>',
	};

	let profileUsername = '';
	let refreshTimer = 0;
	let progressTimer = 0;
	let initializeTimer = 0;
	let requestVersion = 0;

	function safeExternalUrl(value) {
		try {
			const url = new URL(String(value || ''), window.location.origin);
			return url.protocol === 'https:' || url.protocol === 'http:' ? url.href : '';
		} catch (_) {
			return '';
		}
	}

	function usernameFromPage() {
		const marker = document.getElementById('username');
		if (marker && marker.textContent.trim()) return marker.textContent.trim();
		const match = window.location.pathname.match(/^\/@([^/]+)/);
		if (!match) return '';
		try { return decodeURIComponent(match[1]); }
		catch (_) { return match[1]; }
	}

	function isProfilePage() {
		if (!document.body || !usernameFromPage()) return false;
		return document.body.id === 'userpage' || /^\/@[^/]+\/?$/.test(window.location.pathname);
	}

	function normalText(node) {
		return String(node && node.textContent || '').replace(/\s+/g, ' ').trim().toUpperCase();
	}

	function cardAroundHeading(heading) {
		let node = heading && heading.parentElement;
		for (let depth = 0; node && node !== document.body && depth < 7; depth += 1, node = node.parentElement) {
			if (node.matches('section, article, .card, .profile-panel, .userpage-section, [class*="profile-section"]')) return node;
			const style = window.getComputedStyle(node);
			if (node.children.length > 1 && style.borderStyle !== 'none' && parseFloat(style.borderWidth || '0') > 0) return node;
		}
		return heading && heading.parentElement && heading.parentElement.parentElement;
	}

	function connectionMount() {
		const mount = document.getElementById('profile-connections-mount');
		if (!mount) return null;

		const headings = Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6,.card-header,strong'));
		const badgeHeading = headings.find(node => ['BADGES', 'AWARDS RECEIVED'].includes(normalText(node)));
		const badgeSection = cardAroundHeading(badgeHeading);
		if (badgeSection && badgeSection.parentElement && badgeSection !== mount && mount.nextElementSibling !== badgeSection) {
			badgeSection.parentElement.insertBefore(mount, badgeSection);
		}
		return mount;
	}

	function brandMarkup(connection) {
		const provider = String(connection.provider || '').toLowerCase();
		if (PROVIDER_MARKS[provider]) return PROVIDER_MARKS[provider];
		const iconClass = PROVIDER_ICONS[provider] || connection.icon || 'fas fa-link';
		const safeClass = String(iconClass).replace(/[^a-zA-Z0-9 _-]/g, '');
		return `<i class="${safeClass} connection-brand-font" aria-hidden="true"></i>`;
	}

	function providerIcon(connection) {
		const box = document.createElement('span');
		box.className = `connection-provider-icon connection-provider-${String(connection.provider || '').toLowerCase()}`;
		box.innerHTML = brandMarkup(connection);
		return box;
	}

	function connectionCard(connection) {
		const href = safeExternalUrl(connection.profile_url);
		const card = document.createElement(href ? 'a' : 'div');
		card.className = 'profile-connection-link';
		if (href) {
			card.href = href;
			card.target = '_blank';
			card.rel = 'nofollow noopener';
		}
		card.append(providerIcon(connection));

		const copy = document.createElement('span');
		copy.className = 'profile-connection-copy';
		const name = document.createElement('strong');
		name.textContent = connection.display_name || connection.provider_label || 'Connected account';
		const provider = document.createElement('small');
		provider.textContent = connection.provider_label || connection.provider || 'Connection';
		copy.append(name, provider);
		card.append(copy);

		if (connection.verified) {
			const verified = document.createElement('i');
			verified.className = 'fas fa-badge-check profile-connection-verified';
			verified.title = 'Verified connection';
			card.append(verified);
		}
		return card;
	}

	function activityCard(activity) {
		if (!activity || !activity.title) return null;
		const href = safeExternalUrl(activity.external_url);
		const card = document.createElement(href ? 'a' : 'div');
		card.className = `profile-live-activity${activity.provider === 'steam' ? ' is-steam' : ''}`;
		if (href) {
			card.href = href;
			card.target = '_blank';
			card.rel = 'nofollow noopener';
		}

		const art = document.createElement('img');
		art.className = 'profile-live-art';
		art.loading = 'lazy';
		art.alt = '';
		art.src = safeExternalUrl(activity.image_url) || '/i/Obsession/official-logo.png';
		art.addEventListener('error', () => { art.src = '/i/Obsession/official-logo.png'; }, {once: true});
		card.append(art);

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
		card.append(copy);
		return card;
	}

	function updateProgressBars() {
		document.querySelectorAll('.profile-live-progress > span').forEach(fill => {
			const duration = Number(fill.dataset.durationMs || 0);
			const initial = Number(fill.dataset.progressMs || 0);
			const checked = Number(fill.dataset.checkedUtc || 0) * 1000;
			if (!duration) return;
			const current = Math.min(duration, initial + Math.max(0, Date.now() - checked));
			fill.style.width = `${Math.max(0, Math.min(100, current / duration * 100))}%`;
		});
	}

	function renderConnections(payload, username) {
		const mount = connectionMount();
		if (!mount) return false;
		const data = Array.isArray(payload.data) ? payload.data : [];
		let panel = document.getElementById('profile-connections-panel');
		if (!data.length) {
			if (panel) panel.remove();
			return true;
		}

		if (!panel) {
			panel = document.createElement('section');
			panel.id = 'profile-connections-panel';
			panel.className = 'profile-panel profile-connections-panel';
		}
		if (panel.parentElement !== mount) mount.append(panel);
		panel.dataset.connectionsUser = username;
		panel.replaceChildren();

		const heading = document.createElement('div');
		heading.className = 'profile-panel__heading';
		const title = document.createElement('h2');
		title.textContent = 'Connections';
		heading.append(title);
		if (payload.can_manage) {
			const edit = document.createElement('a');
			edit.className = 'btn btn-secondary btn-sm';
			edit.href = '/settings/connections';
			edit.innerHTML = '<i class="fas fa-cog mr-1"></i>Manage';
			heading.append(edit);
		}
		panel.append(heading);

		const list = document.createElement('div');
		list.className = 'profile-connections-list';
		data.forEach(connection => list.append(connectionCard(connection)));
		panel.append(list);

		data.map(connection => connection.activity)
			.filter(activity => activity && activity.title)
			.forEach(activity => {
				const card = activityCard(activity);
				if (card) panel.append(card);
			});
		updateProgressBars();
		return true;
	}

	function scheduleRefresh(delay) {
		window.clearTimeout(refreshTimer);
		refreshTimer = window.setTimeout(refreshConnections, delay);
	}

	async function refreshConnections() {
		if (!isProfilePage()) return;
		if (document.hidden) {
			scheduleRefresh(5000);
			return;
		}
		const username = usernameFromPage();
		if (!username) return;
		if (username !== profileUsername) {
			profileUsername = username;
			requestVersion += 1;
		}
		const version = ++requestVersion;
		const controller = new AbortController();
		const timeout = window.setTimeout(() => controller.abort(), 12000);

		try {
			const response = await fetch(`/api/profile/${encodeURIComponent(username)}/connections`, {
				headers: {'Accept': 'application/json'},
				credentials: 'same-origin',
				signal: controller.signal,
				cache: 'no-store',
			});
			if (!response.ok) throw new Error(`Connections request failed: ${response.status}`);
			const payload = await response.json();
			if (version !== requestVersion || username !== usernameFromPage()) return;
			const rendered = renderConnections(payload, username);
			scheduleRefresh(rendered ? Math.max(20, Number(payload.refresh_seconds || 40)) * 1000 : 1000);
		} catch (_) {
			if (version === requestVersion) scheduleRefresh(3000);
		} finally {
			window.clearTimeout(timeout);
		}
	}

	function initialize(force = false) {
		if (!isProfilePage()) return;
		const username = usernameFromPage();
		const panel = document.getElementById('profile-connections-panel');
		const changedUser = username !== profileUsername;
		if (changedUser) {
			profileUsername = username;
			requestVersion += 1;
		}
		if (force || changedUser || !panel || panel.dataset.connectionsUser !== username) refreshConnections();
		if (!progressTimer) progressTimer = window.setInterval(updateProgressBars, 1000);
	}

	function scheduleInitialize(delay = 80, force = false) {
		window.clearTimeout(initializeTimer);
		initializeTimer = window.setTimeout(() => initialize(force), delay);
	}

	function installNavigationHooks() {
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
	}

	installNavigationHooks();
	const observer = new MutationObserver(() => scheduleInitialize());
	observer.observe(document.documentElement, {childList: true, subtree: true});
	document.addEventListener('visibilitychange', () => { if (!document.hidden) scheduleInitialize(0, true); });
	window.addEventListener('pageshow', () => scheduleInitialize(0, true));
	window.addEventListener('popstate', () => scheduleInitialize(0, true));
	window.addEventListener('obsession:navigation', () => scheduleInitialize(0, true));

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', () => scheduleInitialize(0, true), {once: true});
	} else {
		scheduleInitialize(0, true);
	}
})();
