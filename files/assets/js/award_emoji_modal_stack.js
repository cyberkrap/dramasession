(() => {
	'use strict';

	let pickerOpen = false;
	let backdrop = null;
	let awardFocusTrap = null;

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

		// emoji_modal.js emits this before its normal input event. Let the existing
		// award picker consume that input first, then close only this stacked picker.
		document.addEventListener('emojiInserted', () => {
			if (!pickerOpen) return;
			setTimeout(closePicker, 0);
		});

		awardModal()?.addEventListener('hidden.bs.modal', closePicker);
	}

	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once: true});
	else init();
})();
