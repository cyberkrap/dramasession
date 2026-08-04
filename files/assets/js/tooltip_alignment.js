(() => {
	'use strict';

	const TOOLTIP_ID = 'obsession-aligned-tooltip';
	const installed = new WeakSet();
	const configurations = new WeakMap();
	let activeTrigger = null;
	let tooltip = null;
	let hideTimer = 0;

	function clearHideTimer() {
		window.clearTimeout(hideTimer);
		hideTimer = 0;
	}

	function tooltipElement() {
		if (tooltip && document.body.contains(tooltip)) return tooltip;
		tooltip = document.createElement('div');
		tooltip.id = TOOLTIP_ID;
		tooltip.className = 'obsession-aligned-tooltip';
		tooltip.setAttribute('role', 'tooltip');
		tooltip.setAttribute('aria-hidden', 'true');
		tooltip.addEventListener('pointerenter', () => {
			if (tooltip.dataset.kind === 'ban-hat') clearHideTimer();
		});
		tooltip.addEventListener('pointerleave', () => {
			if (tooltip.dataset.kind === 'ban-hat') hideTooltip(activeTrigger);
		});
		tooltip.addEventListener('focusin', () => {
			if (tooltip.dataset.kind === 'ban-hat') clearHideTimer();
		});
		tooltip.addEventListener('focusout', event => {
			if (tooltip.dataset.kind === 'ban-hat' && !tooltip.contains(event.relatedTarget)) {
				hideTooltip(activeTrigger);
			}
		});
		document.body.appendChild(tooltip);
		return tooltip;
	}

	function disposeBootstrapTooltip(element) {
		if (!(element instanceof Element)) return;
		try {
			window.bootstrap?.Tooltip?.getInstance(element)?.dispose();
		} catch (_) {
			// A tooltip may be mid-disposal while dynamic content is replaced.
		}
	}

	function removeNativeTooltip(element) {
		if (!(element instanceof Element)) return;
		disposeBootstrapTooltip(element);
		element.removeAttribute('data-bs-toggle');
		element.removeAttribute('data-bs-placement');
		element.removeAttribute('data-bs-container');
		element.removeAttribute('data-bs-original-title');
		element.removeAttribute('title');
	}

	function cleanTriggerTree(trigger) {
		removeNativeTooltip(trigger);
		trigger.querySelectorAll('[data-bs-toggle="tooltip"], [data-bs-original-title], [title]').forEach(removeNativeTooltip);
	}

	function clamp(value, minimum, maximum) {
		return Math.min(Math.max(value, minimum), maximum);
	}

	function triggerGeometry(trigger) {
		const rect = trigger.getBoundingClientRect();
		let left = rect.left;
		let right = rect.right;

		// The pin icon historically carries spacing utility classes. Ignore that
		// padding so the label is centred on the visible thumbtack glyph itself.
		if (trigger.matches('.fa-thumbtack')) {
			const style = getComputedStyle(trigger);
			left += parseFloat(style.paddingLeft) || 0;
			right -= parseFloat(style.paddingRight) || 0;
		}

		return {
			center: left + ((right - left) / 2),
			bottom: rect.bottom,
		};
	}

	function positionTooltip() {
		if (!activeTrigger || !tooltip || !document.body.contains(activeTrigger)) return;

		const geometry = triggerGeometry(activeTrigger);
		const margin = 8;
		const kind = tooltip.dataset.kind;
		const gap = kind === 'badge' || kind === 'ban-hat' ? 10 : 8;
		const width = tooltip.offsetWidth;
		const centre = clamp(
			geometry.center,
			margin + (width / 2),
			window.innerWidth - margin - (width / 2),
		);

		tooltip.style.left = `${Math.round(centre)}px`;
		tooltip.style.top = `${Math.round(geometry.bottom + gap)}px`;
	}

	function showTooltip(trigger) {
		clearHideTimer();
		const config = configurations.get(trigger);
		if (!config || !config.content) return;

		activeTrigger = trigger;
		const element = tooltipElement();
		if (config.html) element.innerHTML = config.content;
		else element.textContent = config.content;
		element.dataset.kind = config.kind || 'standard';
		element.setAttribute('aria-hidden', 'false');
		element.classList.add('is-visible');
		trigger.setAttribute('aria-describedby', TOOLTIP_ID);
		positionTooltip();
	}

	function hideTooltip(trigger, immediate = false) {
		const hide = () => {
			if (trigger && activeTrigger !== trigger) return;
			if (activeTrigger) activeTrigger.removeAttribute('aria-describedby');
			activeTrigger = null;
			if (!tooltip) return;
			tooltip.classList.remove('is-visible');
			tooltip.setAttribute('aria-hidden', 'true');
		};

		clearHideTimer();
		if (immediate) hide();
		else hideTimer = window.setTimeout(hide, 120);
	}

	function install(trigger, content, kind, html = false) {
		if (!(trigger instanceof Element) || !content) return;
		const cleanedContent = String(content).trim();
		if (!cleanedContent) return;

		configurations.set(trigger, {
			content: cleanedContent,
			html,
			kind,
		});
		trigger.dataset.obsTooltipKind = kind;
		cleanTriggerTree(trigger);

		if (installed.has(trigger)) return;
		installed.add(trigger);
		trigger.addEventListener('pointerenter', () => showTooltip(trigger));
		trigger.addEventListener('pointerleave', () => hideTooltip(trigger));
		trigger.addEventListener('focusin', () => showTooltip(trigger));
		trigger.addEventListener('focusout', event => {
			if (!tooltip?.contains(event.relatedTarget)) hideTooltip(trigger);
		});
		trigger.addEventListener('pointerdown', event => {
			if (configurations.get(trigger)?.kind !== 'ban-hat') hideTooltip(trigger, true);
			else event.stopPropagation();
		});
	}

	function originalTooltipText(element) {
		return element.getAttribute('title')
			|| element.getAttribute('data-bs-original-title')
			|| element.getAttribute('aria-label')
			|| '';
	}

	function installNavbarTooltips(root) {
		const scope = root instanceof Element ? root : document;
		const candidates = [];
		if (scope.matches?.('#navbar .nav-link, #navbar .mobile-nav-icon, #navbar .navbar-toggler')) candidates.push(scope);
		scope.querySelectorAll?.('#navbar .nav-link, #navbar .mobile-nav-icon, #navbar .navbar-toggler').forEach(item => candidates.push(item));

		candidates.forEach(trigger => {
			if (trigger.id === 'dropdownMenuLink' || trigger.closest('.mobile-drawer-content')) return;
			if (trigger.querySelector('.header--currency')) return;

			const labelledChild = trigger.querySelector('[title], [data-bs-original-title]');
			const text = originalTooltipText(trigger)
				|| (labelledChild ? originalTooltipText(labelledChild) : '');
			if (text) install(trigger, text, 'navbar');
		});
	}

	function installPinnedTooltips(root) {
		const selector = '.fa-thumbtack[title], .fa-thumbtack[data-bs-original-title], [id^="pinned-"][title], [id^="hole-pinned-"][title]';
		const scope = root instanceof Element ? root : document;
		const candidates = [];
		if (scope.matches?.(selector)) candidates.push(scope);
		scope.querySelectorAll?.(selector).forEach(item => candidates.push(item));
		candidates.forEach(trigger => install(trigger, originalTooltipText(trigger), 'pinned'));
	}

	function installBadgeTooltips(root) {
		const scope = root instanceof Element ? root : document;
		const images = [];
		const selector = 'img[src*="/badges/"]';
		if (scope.matches?.(selector)) images.push(scope);
		scope.querySelectorAll?.(selector).forEach(image => images.push(image));

		images.forEach(image => {
			const wrapper = image.parentElement
				? image.parentElement.closest('[title], [data-bs-original-title], [data-bs-toggle="tooltip"]')
				: null;
			const trigger = originalTooltipText(image) ? image : (wrapper || image);
			const text = originalTooltipText(trigger) || originalTooltipText(image);
			if (text) install(trigger, text, 'badge');
		});
	}

	function installBanHatTooltips(root) {
		const scope = root instanceof Element ? root : document;
		const images = [];
		const selector = 'img.hat[src*="/ban-hats/"]';
		if (scope.matches?.(selector)) images.push(scope);
		scope.querySelectorAll?.(selector).forEach(image => images.push(image));

		images.forEach(image => {
			const markup = originalTooltipText(image);
			if (!markup.includes('ban-tooltip-user')) return;
			install(image, markup, 'ban-hat', true);
		});
	}

	function scan(root = document) {
		installNavbarTooltips(root);
		installPinnedTooltips(root);
		installBadgeTooltips(root);
		installBanHatTooltips(root);
	}

	function initialize() {
		scan(document);
		const observer = new MutationObserver(mutations => {
			mutations.forEach(mutation => {
				if (mutation.type === 'attributes' && mutation.target instanceof Element) {
					scan(mutation.target);
				}
				mutation.addedNodes.forEach(node => {
					if (node instanceof Element) scan(node);
				});
			});
		});
		observer.observe(document.body, {
			attributeFilter: ['src', 'title', 'data-bs-original-title'],
			attributes: true,
			childList: true,
			subtree: true,
		});

		window.addEventListener('resize', positionTooltip, {passive: true});
		window.addEventListener('scroll', positionTooltip, {passive: true, capture: true});
		document.addEventListener('hide.bs.tooltip', event => {
			if (configurations.has(event.target)) hideTooltip(event.target, true);
		});
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', initialize, {once: true});
	} else {
		initialize();
	}
})();
