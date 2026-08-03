(() => {
	'use strict';

	const descriptions = {
		Wishcoins: 'Wishcoins - Earned from votes on your posts and comments.',
		Wishbux: 'Wishbux - Earned by supporting Obsession.',
	};

	function installTooltip(row, text) {
		if (!(row instanceof Element)) return;
		row.setAttribute('title', text);
		row.setAttribute('aria-label', text);
		row.dataset.bsToggle = 'tooltip';
		row.dataset.bsPlacement = 'bottom';
		row.style.cursor = 'help';

		row.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(child => {
			if (child === row) return;
			if (window.bootstrap?.Tooltip) {
				window.bootstrap.Tooltip.getInstance(child)?.dispose();
			}
			child.removeAttribute('data-bs-toggle');
			child.removeAttribute('data-bs-original-title');
			child.removeAttribute('title');
		});

		if (window.bootstrap?.Tooltip) {
			window.bootstrap.Tooltip.getInstance(row)?.dispose();
			window.bootstrap.Tooltip.getOrCreateInstance(row, {
				container: 'body',
				placement: 'bottom',
				fallbackPlacements: [],
				boundary: 'viewport',
				offset: [0, 6],
			});
		}
	}

	function enhanceCurrencyTooltips() {
		document.querySelectorAll('.header--currency img[alt]').forEach(icon => {
			const text = descriptions[icon.alt];
			if (text) installTooltip(icon.closest('.header--currency'), text);
		});

		document.querySelectorAll('.mobile-drawer-balance span').forEach(item => {
			const icon = item.querySelector('img[alt]');
			const text = icon && descriptions[icon.alt];
			if (!text) return;
			item.setAttribute('title', text);
			item.setAttribute('aria-label', text);
		});
	}

	function ageVerificationTarget(data) {
		if (!data || typeof data.verification_path !== 'string' || !data.verification_path) return null;
		const target = new URL(data.verification_path, window.location.origin);
		if (target.origin !== window.location.origin) return null;
		if (!target.searchParams.has('next')) {
			target.searchParams.set('next', window.location.pathname + window.location.search + window.location.hash);
		}
		if (data.reason && !target.searchParams.has('reason')) {
			target.searchParams.set('reason', String(data.reason));
		}
		return target.pathname + target.search + target.hash;
	}

	function redirectAgeGate(data) {
		const target = ageVerificationTarget(data);
		if (!target) return false;
		window.location.assign(target);
		return true;
	}

	const nativeOpen = XMLHttpRequest.prototype.open;
	XMLHttpRequest.prototype.open = function(...args) {
		if (!this.__obsessionAgeGateListener) {
			this.__obsessionAgeGateListener = true;
			this.addEventListener('load', function(event) {
				if (this.status !== 451) return;
				let data = null;
				try {
					data = JSON.parse(this.responseText || '{}');
				} catch (_) {}
				if (!redirectAgeGate(data)) return;
				event.stopImmediatePropagation();
			}, true);
		}
		return nativeOpen.apply(this, args);
	};

	if (typeof window.fetch === 'function') {
		const nativeFetch = window.fetch.bind(window);
		window.fetch = async function(...args) {
			const response = await nativeFetch(...args);
			if (response.status !== 451) return response;
			let data = null;
			try {
				data = await response.clone().json();
			} catch (_) {}
			if (!redirectAgeGate(data)) return response;
			return new Promise(() => {});
		};
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', enhanceCurrencyTooltips, {once: true});
	} else {
		enhanceCurrencyTooltips();
	}
})();
