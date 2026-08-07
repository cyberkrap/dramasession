(() => {
	const triggerSelector = '.user-name[data-bs-toggle="popover"]';
	const states = new WeakMap();

	function visiblePopoverFor(trigger) {
		const describedBy = trigger.getAttribute('aria-describedby');
		if (describedBy) {
			const described = document.getElementById(describedBy);
			if (described) return described;
		}
		const visible = document.querySelectorAll('.popover.show');
		return visible.length ? visible[visible.length - 1] : null;
	}

	function configureTrigger(trigger) {
		if (!trigger || trigger.dataset.obsProfileNavigationReady === '1') return;
		if (typeof bootstrap === 'undefined') return;

		const popoverId = trigger.getAttribute('data-content-id');
		const content = popoverId ? document.getElementById(popoverId) : null;
		if (!content) return;

		const existing = bootstrap.Popover.getInstance(trigger);
		if (existing) existing.dispose();

		trigger.setAttribute('data-bs-trigger', 'manual');
		const instance = new bootstrap.Popover(trigger, {
			content: content.innerHTML,
			html: true,
			trigger: 'manual',
			container: 'body',
		});

		let hideTimer = null;
		const clearHide = () => {
			if (hideTimer !== null) {
				clearTimeout(hideTimer);
				hideTimer = null;
			}
		};
		const show = () => {
			clearHide();
			instance.show();
		};
		const scheduleHide = () => {
			clearHide();
			hideTimer = window.setTimeout(() => {
				const popover = visiblePopoverFor(trigger);
				const active = document.activeElement;
				const triggerActive = trigger.matches(':hover') || trigger.contains(active);
				const popoverActive = !!popover && (popover.matches(':hover') || popover.contains(active));
				if (triggerActive || popoverActive) return;
				instance.hide();
			}, 180);
		};

		trigger.addEventListener('mouseenter', show);
		trigger.addEventListener('mouseleave', scheduleHide);
		trigger.addEventListener('focusin', show);
		trigger.addEventListener('focusout', scheduleHide);
		trigger.dataset.obsProfileNavigationReady = '1';
		states.set(trigger, {clearHide, scheduleHide});
	}

	function bridgePopover(trigger) {
		const popover = visiblePopoverFor(trigger);
		const state = states.get(trigger);
		if (!popover || !state || popover.dataset.obsProfileHoverBridge === '1') return;

		popover.dataset.obsProfileHoverBridge = '1';
		popover.addEventListener('mouseenter', state.clearHide);
		popover.addEventListener('mouseleave', state.scheduleHide);
		popover.addEventListener('focusin', state.clearHide);
		popover.addEventListener('focusout', state.scheduleHide);
	}

	function configureTree(root = document) {
		if (root instanceof Element && root.matches(triggerSelector)) configureTrigger(root);
		if (root.querySelectorAll) root.querySelectorAll(triggerSelector).forEach(configureTrigger);
	}

	document.addEventListener('inserted.bs.popover', event => {
		if (event.target.matches(triggerSelector)) bridgePopover(event.target);
	});
	document.addEventListener('shown.bs.popover', event => {
		if (event.target.matches(triggerSelector)) bridgePopover(event.target);
	});

	const initialize = () => {
		configureTree(document);
		const observer = new MutationObserver(mutations => {
			mutations.forEach(mutation => mutation.addedNodes.forEach(node => {
				if (node instanceof Element) configureTree(node);
			}));
		});
		observer.observe(document.body, {childList: true, subtree: true});
	};

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', initialize, {once: true});
	} else {
		initialize();
	}
})();
