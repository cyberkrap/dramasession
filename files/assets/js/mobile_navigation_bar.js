(() => {
	function makeAccountLink({href, label, icon, marker}) {
		const link = document.createElement('a');
		link.className = 'dropdown-item';
		link.href = href;
		if (marker) link.dataset.accountActivityLink = marker;
		link.innerHTML = `<i class="${icon} fa-fw mr-3" aria-hidden="true"></i>${label}`;
		return link;
	}

	function ensureAccountMenuLinks() {
		const menu = document.querySelector('#header--dropdown-menu > .px-2');
		if (!menu) return;

		const profile = menu.querySelector('a.dropdown-item[href^="/@"]');
		if (profile) {
			const base = profile.getAttribute('href').replace(/\/$/, '');
			let anchor = profile;
			const activityLinks = [
				{href: `${base}/posts`, label: 'My posts', icon: 'fas fa-file', marker: 'posts'},
				{href: `${base}/comments`, label: 'My comments', icon: 'fas fa-comments', marker: 'comments'},
			];

			for (const item of activityLinks) {
				let link = menu.querySelector(`a[href="${item.href}"]`);
				if (!link) {
					link = makeAccountLink(item);
					anchor.insertAdjacentElement('afterend', link);
				}
				anchor = link;
			}
		}

		let threadAnchor = menu.querySelector('a[href="/directory"]');
		const communityLinks = [
			{
				href: '/post/11/changelog-and-site-updates-megathread',
				label: 'Changelog',
				icon: 'fas fa-clipboard-list',
			},
			{
				href: '/post/10/bugs-and-suggestions-megathread',
				label: 'Bugs & Suggestions',
				icon: 'fas fa-bug',
			},
		];

		for (const item of communityLinks) {
			let link = menu.querySelector(`a[href="${item.href}"]`);
			if (!link) {
				link = makeAccountLink(item);
				if (threadAnchor) threadAnchor.insertAdjacentElement('afterend', link);
				else menu.append(link);
			}
			threadAnchor = link;
		}
	}

	const init = () => {
		ensureAccountMenuLinks();

		const toggle = document.getElementById('mobile-menu-toggle');
		const drawer = document.getElementById('navbarResponsive');
		const backdrop = document.getElementById('mobile-drawer-backdrop');
		const closeButton = document.getElementById('mobile-drawer-close');
		if (!toggle || !drawer || !backdrop || toggle.dataset.mobileNavigationReady === 'true') return;
		toggle.dataset.mobileNavigationReady = 'true';

		const syncDrawerState = () => {
			if (window.innerWidth >= 768) {
				drawer.setAttribute('aria-hidden', 'false');
			} else if (!drawer.classList.contains('is-open')) {
				drawer.setAttribute('aria-hidden', 'true');
			}
		};

		let lastFocused = null;
		const closeDrawer = () => {
			drawer.classList.remove('is-open');
			backdrop.classList.remove('is-visible');
			drawer.setAttribute('aria-hidden', 'true');
			toggle.setAttribute('aria-expanded', 'false');
			toggle.setAttribute('aria-label', 'Open navigation menu');
			document.documentElement.classList.remove('mobile-drawer-open');
			document.body.classList.remove('mobile-drawer-open');
			if (lastFocused) lastFocused.focus();
		};

		const openDrawer = () => {
			lastFocused = document.activeElement;
			drawer.classList.add('is-open');
			backdrop.classList.add('is-visible');
			drawer.setAttribute('aria-hidden', 'false');
			toggle.setAttribute('aria-expanded', 'true');
			toggle.setAttribute('aria-label', 'Close navigation menu');
			document.documentElement.classList.add('mobile-drawer-open');
			document.body.classList.add('mobile-drawer-open');
			const firstControl = drawer.querySelector('input, a, button');
			if (firstControl) firstControl.focus();
		};

		syncDrawerState();
		toggle.addEventListener('click', (event) => {
			event.preventDefault();
			event.stopPropagation();
			drawer.classList.contains('is-open') ? closeDrawer() : openDrawer();
		});
		backdrop.addEventListener('click', closeDrawer);
		if (closeButton) closeButton.addEventListener('click', closeDrawer);
		drawer.addEventListener('click', (event) => {
			if (event.target.closest('a, button')) closeDrawer();
		});
		document.addEventListener('keydown', (event) => {
			if (event.key === 'Escape' && drawer.classList.contains('is-open')) closeDrawer();
		});
		window.addEventListener('resize', () => {
			syncDrawerState();
			if (window.innerWidth >= 768 && drawer.classList.contains('is-open')) closeDrawer();
		});
	};

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', init, {once: true});
	} else {
		init();
	}
})();