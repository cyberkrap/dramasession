(() => {
	const activityItems = [
		{suffix: '/posts', label: 'My posts', icon: 'fas fa-file', marker: 'posts'},
		{suffix: '/comments', label: 'My comments', icon: 'fas fa-comments', marker: 'comments'},
	];

	const communityItems = [
		{
			href: '/post/11/changelog-and-site-updates-megathread',
			label: 'Changelog',
			icon: 'fas fa-history',
		},
		{
			href: '/post/10/bugs-and-suggestions-megathread',
			label: 'Bugs & Suggestions',
			icon: 'fas fa-bug',
		},
	];

	function prepareLink(link, item, mobile = false) {
		link.className = mobile ? 'nav-link mobile-drawer-link' : 'dropdown-item';
		link.href = item.href;
		if (item.marker) link.dataset.accountActivityLink = item.marker;

		const icon = document.createElement('i');
		icon.className = `${item.icon} fa-fw mr-3`;
		icon.setAttribute('aria-hidden', 'true');
		link.replaceChildren(icon, document.createTextNode(item.label));
		return link;
	}

	function getOrCreateLink(root, item, mobile = false) {
		const link = root.querySelector(`a[href="${item.href}"]`) || document.createElement('a');
		return prepareLink(link, item, mobile);
	}

	function removeFeedbackLinks(root) {
		root.querySelectorAll('a[href="/contact"]').forEach((link) => {
			if (link.textContent.trim().toLowerCase() === 'feedback') link.remove();
		});
	}

	function installDesktopMenu() {
		const menu = document.querySelector('#header--dropdown-menu > .px-2');
		if (!menu) return;

		removeFeedbackLinks(menu);

		const profile = menu.querySelector('a.dropdown-item[href^="/@"]');
		if (profile) {
			const base = profile.getAttribute('href').replace(/\/$/, '');
			let anchor = profile;
			for (const item of activityItems) {
				const link = getOrCreateLink(menu, {...item, href: `${base}${item.suffix}`});
				anchor.insertAdjacentElement('afterend', link);
				anchor = link;
			}
		}

		let anchor = menu.querySelector('a[href="/directory"]') || menu.querySelector('button.copy-link');
		for (const item of communityItems) {
			const link = getOrCreateLink(menu, item);
			if (anchor) anchor.insertAdjacentElement('afterend', link);
			else menu.append(link);
			anchor = link;
		}
	}

	function installMobileMenu() {
		const section = document.querySelector('.mobile-drawer-section');
		if (!section) return;

		removeFeedbackLinks(section);

		const profile = section.querySelector('a.mobile-drawer-link[href^="/@"]');
		if (profile) {
			const base = profile.getAttribute('href').replace(/\/$/, '');
			let anchor = profile;
			for (const item of activityItems) {
				const link = getOrCreateLink(section, {...item, href: `${base}${item.suffix}`}, true);
				anchor.insertAdjacentElement('afterend', link);
				anchor = link;
			}
		}

		let anchor = section.querySelector('a[href="/directory"]') || section.querySelector('button.copy-link');
		for (const item of communityItems) {
			const link = getOrCreateLink(section, item, true);
			if (anchor) anchor.insertAdjacentElement('afterend', link);
			else section.append(link);
			anchor = link;
		}
	}

	function installMenus() {
		installDesktopMenu();
		installMobileMenu();
	}

	function installDrawer() {
		const toggle = document.getElementById('mobile-menu-toggle');
		const drawer = document.getElementById('navbarResponsive');
		const backdrop = document.getElementById('mobile-drawer-backdrop');
		const closeButton = document.getElementById('mobile-drawer-close');
		if (!toggle || !drawer || !backdrop || toggle.dataset.mobileNavigationReady === 'true') return;
		toggle.dataset.mobileNavigationReady = 'true';

		const syncDrawerState = () => {
			if (window.innerWidth >= 768) drawer.setAttribute('aria-hidden', 'false');
			else if (!drawer.classList.contains('is-open')) drawer.setAttribute('aria-hidden', 'true');
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
	}

	function init() {
		installMenus();
		installDrawer();
	}

	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once: true});
	else init();
})();