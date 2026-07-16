(() => {
	const toggle = document.getElementById('mobile-menu-toggle');
	const drawer = document.getElementById('navbarResponsive');
	const backdrop = document.getElementById('mobile-drawer-backdrop');
	const closeButton = document.getElementById('mobile-drawer-close');
	if (!toggle || !drawer || !backdrop) return;

	const syncDrawerState = () => {
		if (window.innerWidth >= 768) {
			drawer.setAttribute('aria-hidden', 'false');
		} else if (!drawer.classList.contains('is-open')) {
			drawer.setAttribute('aria-hidden', 'true');
		}
	};

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

	let lastFocused = null;
	syncDrawerState();
	toggle.addEventListener('click', () => drawer.classList.contains('is-open') ? closeDrawer() : openDrawer());
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
})();