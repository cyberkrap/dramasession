(() => {
	const triggerSelector = '.user-name[data-bs-toggle="popover"]';

	function configuredNameColor(trigger) {
		const inline = trigger.style.getPropertyValue('color').trim();
		if (inline) return inline;
		return getComputedStyle(trigger).color;
	}

	function patronNameplateColor(trigger) {
		const patron = trigger.querySelector(':scope > span.patron');
		if (!patron) return '';
		return patron.style.getPropertyValue('background-color').trim() || configuredNameColor(trigger);
	}

	function styleUsernameTrigger(trigger) {
		const color = configuredNameColor(trigger);
		if (!color) return;
		trigger.style.setProperty('color', color, 'important');

		trigger.querySelectorAll(':scope > span').forEach(username => {
			if (username.classList.contains('mod') || username.classList.contains('mod-rdrama')) return;
			if (username.classList.contains('patron')) {
				const plateColor = patronNameplateColor(trigger) || color;
				username.style.removeProperty('background');
				username.style.setProperty('background-image', 'none', 'important');
				username.style.setProperty('background-color', plateColor, 'important');
				username.style.setProperty('color', '#fff', 'important');
				username.style.setProperty('-webkit-text-fill-color', '#fff', 'important');
				username.style.setProperty('-webkit-background-clip', 'border-box', 'important');
				username.style.setProperty('background-clip', 'border-box', 'important');
				return;
			}
			username.style.setProperty('color', color, 'important');
			username.style.setProperty('-webkit-text-fill-color', color, 'important');
			username.style.setProperty('background', 'none', 'important');
			username.style.setProperty('background-image', 'none', 'important');
			username.style.setProperty('-webkit-background-clip', 'border-box', 'important');
			username.style.setProperty('background-clip', 'border-box', 'important');
		});
	}

	function applyConfiguredNameColor(root=document) {
		const triggers = [];
		if (root instanceof Element && root.matches('.user-name')) triggers.push(root);
		if (root.querySelectorAll) triggers.push(...root.querySelectorAll('.user-name'));
		triggers.forEach(styleUsernameTrigger);
	}

	function initializePopover(trigger) {
		if (!trigger || trigger.dataset.obsPopoverReady === '1' || typeof bootstrap === 'undefined') return;
		const popoverId = trigger.getAttribute('data-content-id');
		const content = popoverId ? document.getElementById(popoverId) : null;
		if (!content) return;

		const existing = bootstrap.Popover.getInstance(trigger);
		if (existing) existing.dispose();
		trigger.setAttribute('data-bs-trigger', 'click');
		bootstrap.Popover.getOrCreateInstance(trigger, {
			content: content.innerHTML,
			html: true,
			trigger: 'click',
			container: 'body',
		});
		trigger.dataset.obsPopoverReady = '1';
	}

	function visiblePopoverFor(trigger) {
		const describedBy = trigger.getAttribute('aria-describedby');
		if (describedBy) {
			const described = document.getElementById(describedBy);
			if (described) return described;
		}
		const visible = document.querySelectorAll('.popover.show');
		return visible.length ? visible[visible.length - 1] : null;
	}

	function sectionize(element, label) {
		if (!element) return;
		element.classList.add('obs-popover-section');
		element.dataset.obsSectionLabel = label;
	}

	function markProfileMeta(popover) {
		const meta = popover.querySelector('.popover-profile-meta');
		if (!meta) return;
		Array.from(meta.children).forEach(item => {
			const text = item.textContent.replace(/\s+/g, ' ').trim().toLowerCase();
			if (text.startsWith('joined') || text.includes('joined ')) {
				item.classList.add('obs-meta-joined');
			}
		});
	}

	function badgeTooltipText(badge) {
		const candidates = [
			badge.getAttribute('data-bs-original-title'),
			badge.getAttribute('data-original-title'),
			badge.getAttribute('title'),
			badge.getAttribute('data-tooltip'),
		];
		for (const candidate of candidates) {
			const text = (candidate || '').replace(/\s+/g, ' ').trim();
			if (text && !/^badge$/i.test(text)) return text;
		}
		return '';
	}

	function initializeBadgeTooltips(popover) {
		if (typeof bootstrap === 'undefined' || !bootstrap.Tooltip) return;
		popover.querySelectorAll('.popover-badges-div img').forEach(badge => {
			const title = badgeTooltipText(badge);
			const existing = bootstrap.Tooltip.getInstance(badge);
			if (existing) existing.dispose();
			badge.removeAttribute('data-bs-original-title');
			badge.removeAttribute('data-original-title');
			if (!title) {
				badge.removeAttribute('title');
				badge.removeAttribute('data-bs-toggle');
				badge.removeAttribute('tabindex');
				return;
			}
			badge.setAttribute('title', title);
			badge.setAttribute('tabindex', '0');
			badge.setAttribute('data-bs-toggle', 'tooltip');
			badge.setAttribute('data-bs-placement', 'top');
			bootstrap.Tooltip.getOrCreateInstance(badge, {
				container: 'body',
				trigger: 'hover focus',
				title,
			});
		});
	}

	function enhancePopoverLayout(popover) {
		if (!popover || popover.dataset.obsPremiumReady === '1') return;
		popover.dataset.obsPremiumReady = '1';
		popover.classList.add('obs-profile-popover-enhanced');
		markProfileMeta(popover);
		sectionize(popover.querySelector('.popover-bio-div'), 'About');
		sectionize(popover.querySelector('.popover-badges-div'), 'Badges');
		initializeBadgeTooltips(popover);

		const view = popover.querySelector('.pop-view_more');
		if (view && !view.querySelector('.fa-arrow-right')) {
			view.insertAdjacentHTML('beforeend', '<i class="fas fa-arrow-right ml-2" aria-hidden="true"></i>');
		}
	}

	function hydratePopover(trigger) {
		const popover = visiblePopoverFor(trigger);
		if (!popover) return;
		const username = popover.querySelector('.pop-username');
		if (username) {
			const plateColor = patronNameplateColor(trigger);
			if (plateColor) {
				username.classList.add('obs-patron-nameplate');
				username.style.setProperty('background-color', plateColor, 'important');
				username.style.setProperty('color', '#fff', 'important');
				username.style.setProperty('-webkit-text-fill-color', '#fff', 'important');
			} else {
				const color = configuredNameColor(trigger);
				username.classList.remove('obs-patron-nameplate');
				username.style.setProperty('color', color, 'important');
				username.style.setProperty('-webkit-text-fill-color', color, 'important');
				username.style.setProperty('background', 'none', 'important');
				username.style.setProperty('background-image', 'none', 'important');
			}
		}
		enhancePopoverLayout(popover);
		popover.addEventListener('pointerdown', event => event.stopPropagation());
		popover.addEventListener('click', event => event.stopPropagation());
	}

	function renameActivity() {
		const activity = document.querySelector('.profile-history');
		if (!activity) return;
		const labels = {
			'/upvoters': 'Upvoters',
			'/downvoters': 'Downvoters',
			'/upvoting': 'Upvoted',
			'/downvoting': 'Downvoted',
		};
		activity.querySelectorAll('a').forEach(link => {
			for (const [path, label] of Object.entries(labels)) {
				if (link.pathname.endsWith(path)) link.textContent = label;
			}
		});
	}

	async function addSupportSummary() {
		const details = document.getElementById('profile--info');
		if (!details || details.querySelector('[data-profile-support-summary]')) return;
		const match = location.pathname.match(/^\/@([^/]+)/);
		if (!match) return;
		try {
			const response = await fetch(`/api/profile/${encodeURIComponent(match[1])}/support-summary`, {
				credentials: 'same-origin',
				headers: {'xhr': 'xhr'},
			});
			if (!response.ok) return;
			const data = await response.json();
			const lifetime = document.createElement('div');
			lifetime.dataset.profileSupportSummary = '1';
			lifetime.innerHTML = `<dt>Lifetime donated</dt><dd>${data.lifetime_donated}</dd>`;
			const discount = document.createElement('div');
			discount.dataset.profileSupportSummary = '1';
			discount.innerHTML = `<dt>Total award discount</dt><dd>${data.award_discount}</dd>`;
			details.append(lifetime, discount);
		} catch (_) {}
	}

	document.addEventListener('shown.bs.popover', event => {
		if (event.target.matches(triggerSelector)) hydratePopover(event.target);
	});

	document.addEventListener('click', event => {
		if (event.target.closest('.popover') || event.target.closest(triggerSelector)) return;
		document.querySelectorAll(triggerSelector).forEach(trigger => {
			const instance = bootstrap.Popover.getInstance(trigger);
			if (instance) instance.hide();
		});
	});

	document.addEventListener('DOMContentLoaded', () => {
		applyConfiguredNameColor(document);
		document.querySelectorAll(triggerSelector).forEach(initializePopover);
		renameActivity();
		addSupportSummary();

		const observer = new MutationObserver(mutations => {
			mutations.forEach(mutation => mutation.addedNodes.forEach(node => {
				if (!(node instanceof Element)) return;
				applyConfiguredNameColor(node);
				node.querySelectorAll(triggerSelector).forEach(initializePopover);
			}));
		});
		observer.observe(document.body, {childList: true, subtree: true});
	});
})();