(() => {
	'use strict';

	let pickerOpen = false;
	let backdrop = null;
	let awardFocusTrap = null;
	const savedEffectLayers = new Map();

	function awardModal() {
		return document.getElementById('awardModal');
	}

	function emojiModal() {
		return document.getElementById('emojiModal');
	}

	function pickerButton() {
		return document.getElementById('award-emoji-picker');
	}

	function removeBackdrop() {
		if (!backdrop) return;
		backdrop.remove();
		backdrop = null;
	}

	function suspendAwardFocusTrap() {
		const award = awardModal();
		awardFocusTrap = window.bootstrap?.Modal?.getInstance(award)?._focustrap || null;
		awardFocusTrap?.deactivate?.();
	}

	function restoreAwardModalState() {
		const award = awardModal();
		if (award?.classList.contains('show')) {
			document.body.classList.add('modal-open');
			awardFocusTrap?.activate?.();
		}
		awardFocusTrap = null;
	}

	function closePicker() {
		if (!pickerOpen) return;
		pickerOpen = false;

		const modal = emojiModal();
		if (modal) {
			modal.classList.remove('show', 'award-emoji-modal-stacked');
			modal.style.display = 'none';
			modal.style.removeProperty('z-index');
			modal.setAttribute('aria-hidden', 'true');
			modal.removeAttribute('aria-modal');
			modal.removeAttribute('role');
		}

		removeBackdrop();
		restoreAwardModalState();
		setTimeout(() => pickerButton()?.focus(), 20);
	}

	window.openAwardEmojiStack = function() {
		const award = awardModal();
		const modal = emojiModal();
		if (!award?.classList.contains('show') || !modal) return;

		pickerOpen = true;
		removeBackdrop();
		suspendAwardFocusTrap();

		backdrop = document.createElement('div');
		backdrop.className = 'modal-backdrop fade show award-emoji-modal-backdrop';
		backdrop.style.zIndex = '1080';
		backdrop.addEventListener('click', closePicker);
		document.body.appendChild(backdrop);

		modal.classList.add('show', 'award-emoji-modal-stacked');
		modal.style.display = 'block';
		modal.style.zIndex = '1085';
		modal.removeAttribute('aria-hidden');
		modal.setAttribute('aria-modal', 'true');
		modal.setAttribute('role', 'dialog');
		document.body.classList.add('modal-open');

		requestAnimationFrame(() => document.getElementById('emoji_search')?.focus());
	};

	function directEffectLayers(target) {
		return Array.from(target?.children || []).filter((child) => child.classList?.contains('content-award-effects'));
	}

	function captureEffectLayers() {
		savedEffectLayers.clear();
		for (const target of document.querySelectorAll('.award-effect-target')) {
			const layer = directEffectLayers(target).at(-1);
			if (layer) savedEffectLayers.set(target, layer);
		}
	}

	function resumeAnimations(layer) {
		if (!layer) return;
		for (const node of layer.querySelectorAll('*')) {
			if (node instanceof HTMLElement) node.style.animationPlayState = 'running';
		}
		try {
			for (const animation of layer.getAnimations?.({subtree: true}) || []) animation.play();
		} catch (_) {}
	}

	function repairEffectLayers() {
		if (!document.querySelector('.modal.show')) {
			document.body.classList.remove('award-modal-open');
		}

		const targets = new Set([
			...document.querySelectorAll('.award-effect-target'),
			...savedEffectLayers.keys(),
		]);

		for (const target of targets) {
			if (!(target instanceof HTMLElement) || !target.isConnected) continue;

			let layers = directEffectLayers(target);
			let layer = layers.at(-1) || null;
			const saved = savedEffectLayers.get(target);

			if (!layer && saved) {
				target.appendChild(saved);
				layer = saved;
				layers = [saved];
			}
			if (!layer) continue;

			for (const duplicate of layers) {
				if (duplicate !== layer) duplicate.remove();
			}

			target.style.setProperty('isolation', 'isolate', 'important');
			layer.style.setProperty('z-index', '1000', 'important');
			layer.style.setProperty('visibility', 'visible', 'important');
			layer.style.setProperty('opacity', '1', 'important');
			layer.style.setProperty('display', 'block', 'important');
			layer.style.setProperty('pointer-events', 'none', 'important');
			resumeAnimations(layer);
		}
	}

	function scheduleEffectRepair() {
		for (const delay of [0, 80, 300]) setTimeout(repairEffectLayers, delay);
	}

	function emojiNameFromAwardIcon(icon) {
		for (const token of icon.classList || []) {
			if (!token.startsWith('award-emoji-name-')) continue;
			const name = token.slice('award-emoji-name-'.length);
			if (/^[A-Za-z0-9_-]{1,80}$/.test(name)) return name;
		}
		return '';
	}

	function addEmojiNameToTooltip(icon) {
		if (!(icon instanceof HTMLElement) || !icon.classList.contains('award-kind-wholesome')) return;
		const emojiName = emojiNameFromAwardIcon(icon);
		if (!emojiName) return;

		const original = icon.getAttribute('data-bs-original-title') || icon.getAttribute('title') || '';
		if (!original || original.includes(`: \"${emojiName}\"`)) return;

		const dateMarker = ' on ';
		const dateAt = original.lastIndexOf(dateMarker);
		const tooltip = dateAt > -1
			? `${original.slice(0, dateAt)}: \"${emojiName}\"${original.slice(dateAt)}`
			: `${original}: \"${emojiName}\"`;

		icon.setAttribute('title', tooltip);
		if (icon.hasAttribute('data-bs-original-title')) icon.setAttribute('data-bs-original-title', tooltip);

		const instance = window.bootstrap?.Tooltip?.getInstance(icon);
		if (instance?._config) instance._config.title = tooltip;
		try { instance?.setContent?.({'.tooltip-inner': tooltip}); } catch (_) {}
	}

	function decorateEmojiTooltips(root = document) {
		if (root instanceof HTMLElement && root.matches('.award-kind-wholesome')) addEmojiNameToTooltip(root);
		root.querySelectorAll?.('.award-kind-wholesome').forEach(addEmojiNameToTooltip);
	}

	function init() {
		const modal = emojiModal();
		if (modal) {
			modal.addEventListener('click', (event) => {
				if (!pickerOpen || !event.target.closest('[data-bs-dismiss="modal"]')) return;
				event.preventDefault();
				event.stopPropagation();
				closePicker();
			}, true);
		}

		document.addEventListener('keydown', (event) => {
			if (!pickerOpen || event.key !== 'Escape') return;
			event.preventDefault();
			event.stopPropagation();
			closePicker();
		}, true);

		document.addEventListener('emojiInserted', () => {
			if (!pickerOpen) return;
			setTimeout(closePicker, 0);
		});

		const award = awardModal();
		if (award) {
			award.addEventListener('show.bs.modal', () => {
				captureEffectLayers();
				repairEffectLayers();
			});
			award.addEventListener('hidden.bs.modal', () => {
				closePicker();
				scheduleEffectRepair();
			});
		}

		decorateEmojiTooltips(document);
		repairEffectLayers();

		const observer = new MutationObserver((mutations) => {
			for (const mutation of mutations) {
				for (const node of mutation.addedNodes) {
					if (node instanceof HTMLElement) decorateEmojiTooltips(node);
				}
			}
		});
		observer.observe(document.body, {childList: true, subtree: true});
	}

	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once: true});
	else init();
})();
