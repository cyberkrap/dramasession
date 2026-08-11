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

	function makeBannerClickable(profile, data) {
		const banner = profile.querySelector('.pop-banner');
		const bannerUrl = String(data.bannerurl || '').trim();
		if (!banner || !bannerUrl) return;

		banner.src = bannerUrl;
		let link = banner.closest('a.obs-popover-banner-link');
		if (!link) {
			link = document.createElement('a');
			link.className = 'obs-popover-banner-link';
			banner.before(link);
			link.append(banner);
		}

		link.href = bannerUrl;
		link.target = '_blank';
		link.rel = 'noopener noreferrer';
		link.title = 'Open profile banner';
		link.setAttribute('aria-label', `Open @${data.username || 'user'} profile banner`);
		link.style.display = 'block';
		link.style.lineHeight = '0';
		link.style.cursor = 'zoom-in';
	}

	function makeAvatarClickableAndCentered(profile, data) {
		let wrapper = profile.querySelector('.popover-profile-identity .profile-pic-75-wrapper');
		const profileUrl = String(data.profile_url || '').trim();
		if (!wrapper) return;

		if (!(wrapper instanceof HTMLAnchorElement) && profileUrl) {
			const link = document.createElement('a');
			link.className = wrapper.className;
			wrapper.replaceWith(link);
			while (wrapper.firstChild) link.append(wrapper.firstChild);
			wrapper = link;
		}

		if (wrapper instanceof HTMLAnchorElement && profileUrl) {
			wrapper.href = profileUrl;
			wrapper.target = '_blank';
			wrapper.rel = 'noopener noreferrer';
			wrapper.title = 'Open profile picture';
			wrapper.setAttribute('aria-label', `Open @${data.username || 'user'} profile picture`);
		}

		wrapper.style.setProperty('position', 'relative', 'important');
		wrapper.style.setProperty('display', 'block', 'important');
		wrapper.style.setProperty('box-sizing', 'border-box', 'important');
		wrapper.style.setProperty('padding', '0', 'important');
		wrapper.style.setProperty('text-decoration', 'none', 'important');
		wrapper.style.setProperty('cursor', profileUrl ? 'zoom-in' : 'default', 'important');

		const picture = wrapper.querySelector('.pop-picture');
		if (picture) {
			if (profileUrl) picture.src = profileUrl;
			picture.style.setProperty('position', 'absolute', 'important');
			picture.style.setProperty('top', '50%', 'important');
			picture.style.setProperty('left', '50%', 'important');
			picture.style.setProperty('margin', '0', 'important');
			picture.style.setProperty('transform', 'translate(-50%, -50%)', 'important');
		}

		const hat = wrapper.querySelector('.pop-hat');
		if (hat) {
			hat.style.setProperty('position', 'absolute', 'important');
			hat.style.setProperty('left', '50%', 'important');
			hat.style.setProperty('bottom', '3px', 'important');
			hat.style.setProperty('height', 'auto', 'important');
			hat.style.setProperty('margin', '0', 'important');
			hat.style.setProperty('transform', 'translateX(-50%)', 'important');
		}
	}

	function repairMedia(profile, data) {
		makeBannerClickable(profile, data);
		makeAvatarClickableAndCentered(profile, data);
	}

	function repairPopover(trigger) {
		const popover = visiblePopoverFor(trigger);
		const profile = popover?.querySelector('.popover-user-profile');
		if (!popover || !profile) return;

		const data = profileData(trigger);
		if (!data.username) return;

		repairMedia(profile, data);
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
