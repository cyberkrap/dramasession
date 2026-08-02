(() => {
	const triggerSelector = '.user-name[data-bs-toggle="popover"]';

	function visiblePopoverFor(trigger) {
		const describedBy = trigger.getAttribute('aria-describedby');
		if (describedBy) {
			const described = document.getElementById(describedBy);
			if (described) return described;
		}
		const visible = document.querySelectorAll('.popover.show');
		return visible.length ? visible[visible.length - 1] : null;
	}

	function profileData(trigger) {
		try {
			return JSON.parse(trigger.dataset.popInfo || '{}');
		} catch (_) {
			return {};
		}
	}

	function formatNumber(value) {
		const number = Number(value);
		return Number.isFinite(number) ? number.toLocaleString('en-US') : '0';
	}

	function makeText(className, value) {
		const element = document.createElement('span');
		element.className = className;
		element.textContent = value;
		return element;
	}

	function rebuildIdentity(profile, data) {
		const info = profile.querySelector('.popover-profile-identity > .text-truncate');
		const username = info?.querySelector('.pop-username');
		if (!info || !username) return;

		const reserved = info.querySelector('.obs-card-reserved') || Array.from(info.querySelectorAll('*')).find(element => /reserved username/i.test(element.textContent || ''));
		const reservedText = reserved ? reserved.textContent.replace(/\s+/g, ' ').trim() : '';

		const nameRow = document.createElement('div');
		nameRow.className = 'obs-card-name-row';
		nameRow.append(username);
		if (data.created_date) nameRow.append(makeText('obs-card-joined', `Joined ${data.created_date}`));

		const facts = document.createElement('div');
		facts.className = 'obs-card-facts';
		facts.append(
			makeText('obs-card-user-id', `ID ${data.id ?? ''}`),
			makeText('obs-card-truescore', `Truescore ${formatNumber(data.truescore)}`),
		);

		info.replaceChildren(nameRow, facts);
		if (reservedText) info.append(makeText('obs-card-reserved', reservedText));
	}

	function makeStat(data, key, label, suffix) {
		const stat = document.createElement('a');
		stat.className = 'pop-profile-stat';
		stat.href = `${data.url || '#'}${suffix}`;

		const value = document.createElement('strong');
		value.textContent = formatNumber(data[key]);
		const caption = document.createElement('span');
		caption.textContent = label;
		stat.append(value, caption);
		return stat;
	}

	function rebuildStats(profile, data) {
		const stats = profile.querySelector('.popover-profile-stats');
		if (!stats) return;

		const view = document.createElement('a');
		view.className = 'pop-view_more';
		view.href = data.url || '#';
		view.append(document.createTextNode('View'));
		const arrow = document.createElement('span');
		arrow.className = 'obs-card-view-arrow';
		arrow.setAttribute('aria-hidden', 'true');
		arrow.textContent = '→';
		view.append(arrow);

		stats.replaceChildren(
			makeStat(data, 'post_count', 'posts', '/posts'),
			makeStat(data, 'comment_count', 'comments', '/comments'),
			makeStat(data, 'coins', 'Wishcoins', ''),
			makeStat(data, 'bux', 'Wishbux', ''),
			view,
		);
	}

	function repairPopover(trigger) {
		const popover = visiblePopoverFor(trigger);
		const profile = popover?.querySelector('.popover-user-profile');
		if (!popover || !profile) return;

		const data = profileData(trigger);
		if (!data.username) return;

		rebuildIdentity(profile, data);
		rebuildStats(profile, data);
		profile.dataset.obsDataHotfixReady = '1';

		const instance = typeof bootstrap !== 'undefined' ? bootstrap.Popover.getInstance(trigger) : null;
		requestAnimationFrame(() => instance?.update());
	}

	function handlePopover(event) {
		if (!event.target.matches(triggerSelector)) return;
		queueMicrotask(() => repairPopover(event.target));
	}

	document.addEventListener('inserted.bs.popover', handlePopover);
	document.addEventListener('shown.bs.popover', handlePopover);
})();
