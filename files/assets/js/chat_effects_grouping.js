(() => {
	'use strict';

	const GROUP_WINDOW_SECONDS = 30;
	const effectCache = new Map();
	let hydrationScheduled = false;
	let hydrationRunning = false;
	let onlineRenderToken = 0;

	function normaliseEffects(value) {
		const values = Array.isArray(value) ? value : String(value || '').split(',');
		return values
			.map(item => String(item || '').trim().toLowerCase())
			.filter(item => /^[a-z0-9_]+$/.test(item));
	}

	function escapeText(value) {
		return String(value ?? '');
	}

	async function loadEffects(userIds) {
		const missing = [...new Set(userIds.map(String))].filter(id => id && !effectCache.has(id));
		if (!missing.length) return;

		try {
			const response = await fetch(`/api/chat/username-effects?ids=${encodeURIComponent(missing.join(','))}`, {
				headers: {'Accept': 'application/json'},
				credentials: 'same-origin',
			});
			if (!response.ok) throw new Error(`Effect lookup failed with ${response.status}`);
			const payload = await response.json();
			const users = payload && payload.users ? payload.users : {};
			for (const id of missing) {
				const user = users[id] || {};
				effectCache.set(id, {
					username: escapeText(user.username),
					effects: normaliseEffects(user.effects),
					effectColor: String(user.effect_color || 'ffffff').replace(/^#/, ''),
					nameColor: String(user.name_color || 'ffffff').replace(/^#/, ''),
					patron: Boolean(user.patron),
				});
			}
		} catch (error) {
			console.warn('Unable to load chat username effects', error);
			for (const id of missing) {
				if (!effectCache.has(id)) effectCache.set(id, {
					username: '', effects: [], effectColor: 'ffffff', nameColor: 'ffffff', patron: false,
				});
			}
		}
	}

	function applyEffectData(element, userId, data) {
		if (!(element instanceof Element)) return;
		const effects = normaliseEffects(data && data.effects);
		if (!effects.length) {
			element.removeAttribute('data-username-effects');
			element.removeAttribute('data-username-effect-user');
			element.removeAttribute('data-username-effect-color');
			return;
		}
		element.dataset.usernameEffectUser = String(userId);
		element.dataset.usernameEffects = effects.join(',');
		element.dataset.usernameEffectColor = String(data.effectColor || 'ffffff').replace(/^#/, '');
	}

	const originalPopulateGroup = populateGroup;
	populateGroup = function populateGroupWithEffects(group, message) {
		originalPopulateGroup(group, message);
		const userId = String(message.user_id || '');
		const cached = effectCache.get(userId);
		const suppliedEffects = normaliseEffects(message.username_effects);
		const data = suppliedEffects.length
			? {
				effects: suppliedEffects,
				effectColor: message.username_effect_color || 'ffffff',
				patron: Boolean(message.patron),
				nameColor: message.namecolor || 'ffffff',
			}
			: cached;
		applyEffectData(group.querySelector('.chat-username'), userId, data);
	};

	function sameMessageGroup(previous, message) {
		if (!previous || String(previous.user_id) !== String(message.user_id)) return false;
		if (Boolean(previous.distinguish_by) !== Boolean(message.distinguish_by)) return false;
		const previousTime = Number(previous.time);
		const currentTime = Number(message.time);
		if (!Number.isFinite(previousTime) || !Number.isFinite(currentTime)) return false;
		const gap = currentTime - previousTime;
		return gap >= 0 && gap <= GROUP_WINDOW_SECONDS;
	}

	renderAll = function renderAllWithFreshGroups() {
		const fragment = document.createDocumentFragment();
		let currentGroup = null;
		let previousMessage = null;

		for (const message of sortedMessages()) {
			if (!currentGroup || !sameMessageGroup(previousMessage, message)) {
				currentGroup = buildGroup(message);
				fragment.appendChild(currentGroup);
			}
			currentGroup.appendChild(buildLine(message));
			previousMessage = message;
		}

		box.replaceChildren(fragment);
		if (typeof bs_trigger === 'function') bs_trigger(box);
		updateLoadMoreButton();
		scheduleMessageHydration();
	};

	function scheduleMessageHydration() {
		if (hydrationScheduled || hydrationRunning) return;
		hydrationScheduled = true;
		queueMicrotask(async () => {
			hydrationScheduled = false;
			hydrationRunning = true;
			try {
				const messages = [...chatState.messages.values()];
				await loadEffects(messages.map(message => message.user_id));
				let changed = false;
				for (const message of messages) {
					const data = effectCache.get(String(message.user_id));
					if (!data) continue;
					const effects = data.effects.join(',');
					const current = normaliseEffects(message.username_effects).join(',');
					if (current !== effects || message.username_effect_color !== data.effectColor) {
						message.username_effects = data.effects.slice();
						message.username_effect_color = data.effectColor;
						changed = true;
					}
				}
				if (changed) renderAll();
			} finally {
				hydrationRunning = false;
			}
		});
	}

	function buildOnlineEntry(entry, mutedUsers, adminLevel) {
		const username = escapeText(entry[0]);
		const userId = String(entry[1] || '');
		const nameColor = String(entry[2] || 'ffffff').replace(/^#/, '');
		const patron = Boolean(entry[3]);
		const data = effectCache.get(userId) || {
			effects: [], effectColor: 'ffffff', nameColor, patron,
		};

		const item = document.createElement('li');
		if (adminLevel && Object.prototype.hasOwnProperty.call(mutedUsers, username.toLowerCase())) {
			const muted = document.createElement('b');
			muted.className = 'text-danger muted';
			muted.textContent = 'X';
			item.append(muted, document.createTextNode(' '));
		}

		const link = document.createElement('a');
		link.className = 'font-weight-bold';
		link.target = '_blank';
		link.href = `/@${encodeURIComponent(username)}`;
		link.style.color = `#${nameColor}`;

		const avatar = document.createElement('img');
		avatar.loading = 'lazy';
		avatar.className = 'mr-1';
		avatar.src = `/pp/${Number(userId)}`;

		const name = document.createElement('span');
		name.textContent = username;
		if (patron) {
			name.classList.add('patron');
			name.style.backgroundColor = `#${nameColor}`;
		}
		applyEffectData(name, userId, data);
		link.append(avatar, name);
		item.append(link);
		return item;
	}

	function replaceOnlineList(target, users, mutedUsers, adminLevel) {
		if (!target) return;
		const fragment = document.createDocumentFragment();
		for (const entry of users) fragment.append(buildOnlineEntry(entry, mutedUsers, adminLevel));
		target.replaceChildren(fragment);
	}

	async function renderOnlineWithEffects(data) {
		const token = ++onlineRenderToken;
		const users = Array.isArray(data && data[0]) ? data[0] : [];
		const mutedUsers = data && data[1] && typeof data[1] === 'object' ? data[1] : {};
		await loadEffects(users.map(entry => entry[1]));
		if (token !== onlineRenderToken) return;
		const adminLevel = Number(document.getElementById('admin_level')?.value || 0);
		replaceOnlineList(document.getElementById('online'), users, mutedUsers, adminLevel);
		replaceOnlineList(document.getElementById('online-mobile'), users, mutedUsers, adminLevel);
	}

	socket.on('online', data => {
		void renderOnlineWithEffects(data);
	});

	// chat.js performs its first render before this enhancement file runs.
	// Re-render once so the 30-second grouping rule applies immediately.
	renderAll();
})();
