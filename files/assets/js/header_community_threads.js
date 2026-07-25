(() => {
	'use strict';

	const links = [
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

	function makeLink(item, mobile = false) {
		const link = document.createElement('a');
		link.href = item.href;
		link.className = mobile
			? 'nav-link mobile-drawer-link'
			: 'dropdown-item';

		const icon = document.createElement('i');
		icon.className = `${item.icon} fa-fw mr-3`;
		icon.setAttribute('aria-hidden', 'true');
		link.append(icon, document.createTextNode(item.label));
		return link;
	}

	function insertDesktopLinks() {
		const menu = document.querySelector('#header--dropdown-menu > .px-2');
		if (!menu) return;

		const directory = menu.querySelector('a[href="/directory"]');
		let anchor = directory;

		for (const item of links) {
			if (menu.querySelector(`a[href="${item.href}"]`)) continue;
			const link = makeLink(item);
			if (anchor) {
				anchor.insertAdjacentElement('afterend', link);
			} else {
				menu.append(link);
			}
			anchor = link;
		}
	}

	function insertMobileLinks() {
		const accountSection = document.querySelector('.mobile-drawer-section');
		if (!accountSection) return;

		const feedback = accountSection.querySelector('a[href="/contact"]');
		for (const item of links) {
			if (accountSection.querySelector(`a[href="${item.href}"]`)) continue;
			const link = makeLink(item, true);
			if (feedback) feedback.insertAdjacentElement('beforebegin', link);
			else accountSection.append(link);
		}
	}

	function install() {
		insertDesktopLinks();
		insertMobileLinks();
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', install, {once: true});
	} else {
		install();
	}
})();
