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

	function addHeaderActivityLinks() {
		const menu = document.querySelector('#header--dropdown-menu > .px-2');
		if (!menu || menu.querySelector('[data-account-activity-link]')) return;
		const profile = menu.querySelector('a.dropdown-item[href^="/@"]');
		if (!profile) return;

		const base = profile.getAttribute('href').replace(/\/$/, '');
		const posts = document.createElement('a');
		posts.className = 'dropdown-item';
		posts.href = `${base}/posts`;
		posts.dataset.accountActivityLink = 'posts';
		posts.innerHTML = '<i class="fas fa-file fa-fw mr-3"></i>My posts';

		const comments = document.createElement('a');
		comments.className = 'dropdown-item';
		comments.href = `${base}/comments`;
		comments.dataset.accountActivityLink = 'comments';
		comments.innerHTML = '<i class="fas fa-comments fa-fw mr-3"></i>My comments';

		profile.after(posts, comments);
	}

	async function addSupportSummary() {
		const details = document.getElementById('profile--info');
		if (!details || details.querySelector('[data-profile-support-summary]')) return;
		if (details.dataset.profileSupportLoading === '1') return;

		const match = location.pathname.match(/^\/@([^/]+)/);
		if (!match) return;
		details.dataset.profileSupportLoading = '1';

		try {
			const response = await fetch(`/api/profile/${encodeURIComponent(match[1])}/support-summary`, {
				credentials: 'same-origin',
				headers: {'xhr': 'xhr'},
			});
			if (!response.ok || details.querySelector('[data-profile-support-summary]')) return;
			const data = await response.json();
			const lifetime = document.createElement('div');
			lifetime.dataset.profileSupportSummary = '1';
			lifetime.innerHTML = `<dt>Lifetime donated</dt><dd>${data.lifetime_donated}</dd>`;
			const discount = document.createElement('div');
			discount.dataset.profileSupportSummary = '1';
			discount.innerHTML = `<dt>Total award discount</dt><dd>${data.award_discount}</dd>`;
			details.append(lifetime, discount);
		} catch (_) {
			// Leave the profile usable if the optional support summary request fails.
		} finally {
			delete details.dataset.profileSupportLoading;
		}
	}

	function initializePage() {
		if (document.documentElement.dataset.obsProfileFixesReady === '1') {
			addSupportSummary();
			return;
		}
		document.documentElement.dataset.obsProfileFixesReady = '1';

		applyConfiguredNameColor(document);
		document.querySelectorAll(triggerSelector).forEach(initializePopover);
		renameActivity();
		addHeaderActivityLinks();
		addSupportSummary();

		const observer = new MutationObserver(mutations => {
			mutations.forEach(mutation => mutation.addedNodes.forEach(node => {
				if (!(node instanceof Element)) return;
				applyConfiguredNameColor(node);
				if (node.matches(triggerSelector)) initializePopover(node);
				node.querySelectorAll(triggerSelector).forEach(initializePopover);
				if (node.id === 'profile--info' || node.querySelector('#profile--info')) addSupportSummary();
			}));
		});
		observer.observe(document.body, {childList: true, subtree: true});
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

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', initializePage, {once: true});
	} else {
		initializePage();
	}
	window.addEventListener('pageshow', addSupportSummary);
})();