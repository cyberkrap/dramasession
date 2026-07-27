(() => {
	'use strict';

	const PROVIDER_ICONS = {
		spotify: 'fab fa-spotify',
		github: 'fab fa-github',
		discord: 'fab fa-discord',
		steam: 'fab fa-steam',
		reddit: 'fab fa-reddit',
		twitch: 'fab fa-twitch',
		youtube: 'fab fa-youtube',
		x: 'fab fa-x-twitter',
		xbox: 'fab fa-xbox',
		playstation: 'fab fa-playstation',
		bluesky: 'fas fa-cloud',
		roblox: 'fas fa-cube',
		epicgames: 'fas fa-shield',
		battlenet: 'fas fa-gamepad',
	};

	let profileUsername = '';
	let refreshTimer = 0;
	let progressTimer = 0;

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

	function providerIcon(connection) {
		const box = document.createElement('span');
		box.className = `connection-provider-icon connection-provider-${connection.provider}`;
		if (connection.avatar_url) {
			const image = document.createElement('img');
			image.loading = 'lazy';
			image.alt = '';
			image.src = safeExternalUrl(connection.avatar_url);
			box.append(image);
		} else {
			const icon = document.createElement('i');
			icon.className = PROVIDER_ICONS[connection.provider] || connection.icon || 'fas fa-link';
			box.append(icon);
		}
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
		name.textContent = connection.display_name || connection.provider_label;
		const provider = document.createElement('small');
		provider.textContent = connection.provider_label || connection.provider;
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

		if (activity.duration_ms > 0) {
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
			const elapsed = Math.max(0, Date.now() - checked);
			const current = Math.min(duration, initial + elapsed);
			fill.style.width = `${Math.max(0, Math.min(100, current / duration * 100))}%`;
		});
	}

	function renderConnections(payload) {
		const data = Array.isArray(payload.data) ? payload.data : [];
		let panel = document.getElementById('profile-connections-panel');
		if (!data.length) {
			if (panel) panel.remove();
			return;
		}

		if (!panel) {
			panel = document.createElement('section');
			panel.id = 'profile-connections-panel';
			panel.className = 'profile-panel profile-connections-panel';
			const about = document.querySelector('.profile-primary-column .profile-about');
			const column = document.querySelector('.profile-primary-column');
			if (about) about.insertAdjacentElement('afterend', panel);
			else if (column) column.prepend(panel);
			else return;
		}
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
			edit.innerHTML = '<i class="fas fa-edit mr-1"></i>Manage';
			heading.append(edit);
		}
		panel.append(heading);

		const list = document.createElement('div');
		list.className = 'profile-connections-list';
		data.forEach(connection => list.append(connectionCard(connection)));
		panel.append(list);

		const activities = data.map(connection => connection.activity).filter(activity => activity && activity.title);
		activities.forEach(activity => {
			const card = activityCard(activity);
			if (card) panel.append(card);
		});
		updateProgressBars();
	}

	async function refreshConnections() {
		if (!profileUsername || document.hidden) return;
		try {
			const response = await fetch(`/api/profile/${encodeURIComponent(profileUsername)}/connections`, {
				headers: {'Accept': 'application/json'},
				credentials: 'same-origin',
			});
			if (!response.ok) return;
			const payload = await response.json();
			renderConnections(payload);
			window.clearTimeout(refreshTimer);
			refreshTimer = window.setTimeout(refreshConnections, Math.max(20, Number(payload.refresh_seconds || 40)) * 1000);
		} catch (_) {
			window.clearTimeout(refreshTimer);
			refreshTimer = window.setTimeout(refreshConnections, 60000);
		}
	}

	function initialize() {
		if (!document.body || document.body.id !== 'userpage') return;
		profileUsername = usernameFromPage();
		if (!profileUsername) return;
		refreshConnections();
		progressTimer = window.setInterval(updateProgressBars, 1000);
		document.addEventListener('visibilitychange', () => {
			if (!document.hidden) refreshConnections();
		});
	}

	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize, {once: true});
	else initialize();
})();
