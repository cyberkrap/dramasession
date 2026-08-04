(() => {
	'use strict';

	const selector = '[data-bs-toggle="tooltip"].hat';
	const hideDelay = 140;

	function tooltipMarkup(element) {
		const source = element.getAttribute('src') || '';
		const markup = element.getAttribute('data-bs-original-title') || element.getAttribute('title') || '';
		const isBanHat = source.includes('/ban-hats/') || element.classList.contains('pop-hat-ban');
		return isBanHat && markup.includes('ban-tooltip-user') ? markup : '';
	}

	function install(element) {
		if (!(element instanceof Element) || element.dataset.banTooltipReady === '1') return;

		const markup = tooltipMarkup(element);
		if (!markup || typeof bootstrap === 'undefined' || !bootstrap.Tooltip) return;

		const oldInstance = bootstrap.Tooltip.getInstance(element);
		if (oldInstance) oldInstance.dispose();

		let hideTimer = null;
		const tooltip = new bootstrap.Tooltip(element, {
			boundary: 'viewport',
			container: 'body',
			customClass: 'ban-hat-tooltip',
			fallbackPlacements: [],
			html: true,
			offset: [0, 6],
			placement: element.getAttribute('data-bs-placement') || 'bottom',
			sanitize: false,
			title: markup,
			trigger: 'manual',
		});

		function clearHide() {
			if (hideTimer !== null) {
				window.clearTimeout(hideTimer);
				hideTimer = null;
			}
		}

		function scheduleHide(delay = hideDelay) {
			clearHide();
			hideTimer = window.setTimeout(() => tooltip.hide(), delay);
		}

		function show() {
			clearHide();
			tooltip.show();
		}

		function bindRenderedTooltip() {
			const tooltipId = element.getAttribute('aria-describedby');
			const rendered = tooltipId ? document.getElementById(tooltipId) : null;
			if (!rendered || rendered.dataset.banTooltipInteractive === '1') return;

			rendered.dataset.banTooltipInteractive = '1';
			rendered.addEventListener('mouseenter', clearHide);
			rendered.addEventListener('mouseleave', () => scheduleHide(80));
			rendered.addEventListener('focusin', clearHide);
			rendered.addEventListener('focusout', (event) => {
				if (!rendered.contains(event.relatedTarget)) scheduleHide(80);
			});
		}

		element.dataset.banTooltipReady = '1';
		element.addEventListener('mouseenter', show);
		element.addEventListener('mouseleave', () => scheduleHide());
		element.addEventListener('focusin', show);
		element.addEventListener('focusout', () => scheduleHide());
		element.addEventListener('shown.bs.tooltip', bindRenderedTooltip);
	}

	function scan(root = document) {
		if (root instanceof Element && root.matches(selector)) install(root);
		if (root.querySelectorAll) root.querySelectorAll(selector).forEach(install);
	}

	function start() {
		scan();
		new MutationObserver((mutations) => {
			for (const mutation of mutations) {
				if (mutation.type === 'attributes') install(mutation.target);
				for (const node of mutation.addedNodes) {
					if (node instanceof Element) scan(node);
				}
			}
		}).observe(document.documentElement, {
			attributeFilter: ['src', 'title', 'data-bs-original-title'],
			attributes: true,
			childList: true,
			subtree: true,
		});
	}

	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, {once: true});
	else start();
})();
