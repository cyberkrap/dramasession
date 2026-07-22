(() => {
	const triggerSelector = '.user-name[data-bs-toggle="popover"]';

	function configuredNameColor(trigger) {
		const inline = trigger.style.getPropertyValue('color').trim();
		if (inline) return inline;
		return getComputedStyle(trigger).color;
	}

	function applyConfiguredNameColor(root=document) {
		const triggers = [];
		if (root instanceof Element && root.matches('.user-name')) triggers.push(root);
		if (root.querySelectorAll) triggers.push(...root.querySelectorAll('.user-name'));

		triggers.forEach(trigger => {
			const color = configuredNameColor(trigger);
			if (!color) return;
			trigger.style.setProperty('color', color, 'important');
			trigger.querySelectorAll(':scope > span').forEach(username => {
				if (username.classList.contains('mod') || username.classList.contains('mod-rdrama')) return;
				username.style.setProperty('color', color, 'important');
				username.style.setProperty('-webkit-text-fill-color', color, 'important');
				username.style.setProperty('background', 'none', 'important');
				username.style.setProperty('background-image', 'none', 'important');
				username.style.setProperty('-webkit-background-clip', 'border-box', 'important');
				username.style.setProperty('background-clip', 'border-box', 'important');
			});
		});
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

	function hydratePopover(trigger) {
		const popover = visiblePopoverFor(trigger);
		if (!popover) return;
		const username = popover.querySelector('.pop-username');
		if (username) {
			const color = configuredNameColor(trigger);
			username.style.setProperty('color', color, 'important');
			username.style.setProperty('-webkit-text-fill-color', color, 'important');
			username.style.setProperty('background', 'none', 'important');
			username.style.setProperty('background-image', 'none', 'important');
		}
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