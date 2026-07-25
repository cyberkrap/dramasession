(() => {
	'use strict';

	const links = [
		{
			href: '/post/11/changelog-and-site-updates-megathread',
			label: 'Changelog',
			icon: 'fas fa-clipboard',
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

	function removeFeedbackLinks() {
		document.querySelectorAll(
			'#header--dropdown-menu a[href="/contact"], .mobile-drawer-section a[href="/contact"]'
		).forEach((link) => {
			if (link.textContent.trim().toLowerCase() === 'feedback') link.remove();
		});
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

		const contact = Array.from(accountSection.querySelectorAll('a[href="/contact"]'))
			.find((link) => link.textContent.trim().toLowerCase() === 'contact us');
		for (const item of links) {
			if (accountSection.querySelector(`a[href="${item.href}"]`)) continue;
			const link = makeLink(item, true);
			if (contact) contact.insertAdjacentElement('beforebegin', link);
			else accountSection.append(link);
		}
	}

	function replaceText(root, oldText, newText) {
		const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
		const needle = oldText.toLowerCase();
		let node = walker.nextNode();
		while (node) {
			if (node.nodeValue.toLowerCase().includes(needle)) {
				node.nodeValue = node.nodeValue.replace(new RegExp(oldText, 'i'), newText);
				return true;
			}
			node = walker.nextNode();
		}
		return false;
	}

	function setDirectoryIcon(card, iconClass) {
		const oldIcon = card.querySelector('[data-directory-icon], i');
		const icon = document.createElement('i');
		const preservedClasses = oldIcon
			? Array.from(oldIcon.classList).filter((className) =>
				!['fas', 'far', 'fal', 'fab', 'fad'].includes(className) &&
				!className.startsWith('fa-')
			)
			: [];
		icon.className = [...preservedClasses, 'fas', iconClass].join(' ');
		icon.setAttribute('aria-hidden', 'true');
		icon.removeAttribute('hidden');
		icon.style.display = '';

		if (oldIcon) {
			oldIcon.replaceWith(icon);
			return;
		}

		const heading = card.querySelector(
			'[data-directory-title], h1, h2, h3, h4, h5, h6, strong, b, .font-weight-bold'
		);
		if (heading) heading.insertAdjacentElement('beforebegin', icon);
		else card.prepend(icon);
	}

	function setDirectoryCard(card, item, previousLabel = 'Community Feedback') {
		card.href = item.href;
		card.removeAttribute('target');
		card.removeAttribute('rel');
		setDirectoryIcon(card, item.icon);

		const heading = Array.from(card.querySelectorAll(
			'[data-directory-title], h1, h2, h3, h4, h5, h6, strong, b, .font-weight-bold'
		)).find((element) => element.textContent.toLowerCase().includes(previousLabel.toLowerCase()));
		if (heading) heading.textContent = item.label;
		else replaceText(card, previousLabel, item.label);

		const description = card.querySelector(
			'[data-directory-description], .directory-description, p, small, .text-muted'
		);
		if (description) description.textContent = item.description;
	}

	function enhanceDirectory() {
		if (!location.pathname.startsWith('/directory')) return;

		const main = document.querySelector('#main-content-col') || document.querySelector('main') || document.body;
		const feedbackCard = Array.from(main.querySelectorAll('a')).find((link) =>
			link.textContent.replace(/\s+/g, ' ').trim().toLowerCase().includes('community feedback')
		);
		if (!feedbackCard) return;

		const parent = feedbackCard.parentElement;
		if (!parent) return;

		const sourceCard = feedbackCard.cloneNode(true);
		setDirectoryCard(feedbackCard, {
			href: '/donate',
			label: 'Support',
			description: 'Support The Obsession Club.',
			icon: 'fa-heart',
		});

		const directoryItems = [
			{
				href: '/post/10/bugs-and-suggestions-megathread',
				label: 'Bugs & Suggestions',
				description: 'Report bugs and suggest improvements.',
				icon: 'fa-bug',
			},
			{
				href: '/post/11/changelog-and-site-updates-megathread',
				label: 'Changelog',
				description: 'Read the latest site changes and updates.',
				icon: 'fa-clipboard',
			},
		];

		let insertionPoint = feedbackCard;
		for (const item of directoryItems) {
			if (parent.querySelector(`a[href="${item.href}"]`)) continue;
			const card = sourceCard.cloneNode(true);
			card.removeAttribute('id');
			card.querySelectorAll('[id]').forEach((element) => element.removeAttribute('id'));
			setDirectoryCard(card, item);
			insertionPoint.insertAdjacentElement('afterend', card);
			insertionPoint = card;
		}
	}

	function install() {
		removeFeedbackLinks();
		insertDesktopLinks();
		insertMobileLinks();
		enhanceDirectory();
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', install, {once: true});
	} else {
		install();
	}
})();