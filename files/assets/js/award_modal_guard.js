(() => {
	'use strict';

	const MODAL_SELECTOR = '.modal';
	const GUARD_ATTRIBUTE = 'modalLifecycleGuard';

	function shownModals() {
		return Array.from(document.querySelectorAll(`${MODAL_SELECTOR}.show`));
	}

	function forceHideModal(modal) {
		modal.classList.remove('show');
		modal.style.display = 'none';
		modal.setAttribute('aria-hidden', 'true');
		modal.removeAttribute('aria-modal');
		modal.removeAttribute('role');
	}

	function hideOtherModals(current) {
		shownModals().forEach(modal => {
			if (modal === current) return;
			const instance = window.bootstrap?.Modal?.getInstance(modal);
			if (instance) instance.hide();
			else forceHideModal(modal);
		});
	}

	function resetAwardForm(modal) {
		if (!modal || modal.id !== 'awardModal') return;
		modal.querySelectorAll('.award-choice.picked').forEach(choice => choice.classList.remove('picked'));
		const kind = modal.querySelector('#kind');
		const note = modal.querySelector('#note');
		const summary = modal.querySelector('#award-price-summary');
		const submit = modal.querySelector('#giveaward');
		if (kind) kind.value = '';
		if (note) note.value = '';
		if (summary) summary.textContent = 'Choose an award';
		if (submit) {
			submit.disabled = true;
			submit.textContent = 'Give Award';
		}
	}

	function normalizeModalState() {
		const openModals = shownModals();
		const backdrops = Array.from(document.querySelectorAll('.modal-backdrop'));

		if (!openModals.length) {
			backdrops.forEach(backdrop => backdrop.remove());
			document.body.classList.remove('award-modal-open', 'modal-open');
			document.body.style.removeProperty('overflow');
			document.body.style.removeProperty('padding-right');
			return;
		}

		document.body.classList.add('modal-open');
		document.body.classList.toggle('award-modal-open', openModals.some(modal => modal.id === 'awardModal'));

		const activeModal = openModals[openModals.length - 1];
		const usesBackdrop = activeModal.getAttribute('data-bs-backdrop') !== 'false';
		if (!usesBackdrop) {
			backdrops.forEach(backdrop => backdrop.remove());
			return;
		}

		backdrops.slice(0, -1).forEach(backdrop => backdrop.remove());
		if (!backdrops.length) {
			const backdrop = document.createElement('div');
			backdrop.className = 'modal-backdrop fade show';
			document.body.appendChild(backdrop);
		}
	}

	function prepareModal(modal) {
		if (!(modal instanceof HTMLElement) || !modal.matches(MODAL_SELECTOR)) return;
		if (modal.parentElement !== document.body) document.body.appendChild(modal);
		if (modal.dataset[GUARD_ATTRIBUTE] === '1') return;
		modal.dataset[GUARD_ATTRIBUTE] = '1';

		modal.addEventListener('click', event => {
			if (event.target !== modal || modal.getAttribute('data-bs-backdrop') === 'static') return;
			const instance = window.bootstrap?.Modal?.getInstance(modal);
			if (instance) instance.hide();
		});
	}

	function prepareWithin(root) {
		if (!(root instanceof Element) && root !== document) return;
		if (root instanceof Element && root.matches(MODAL_SELECTOR)) prepareModal(root);
		root.querySelectorAll(MODAL_SELECTOR).forEach(prepareModal);
	}

	document.addEventListener('DOMContentLoaded', () => {
		prepareWithin(document);
		normalizeModalState();

		const observer = new MutationObserver(mutations => {
			mutations.forEach(mutation => {
				mutation.addedNodes.forEach(node => {
					if (node.nodeType === Node.ELEMENT_NODE) prepareWithin(node);
				});
			});
		});
		observer.observe(document.body, {childList: true, subtree: true});
	});

	document.addEventListener('show.bs.modal', event => {
		const modal = event.target;
		if (!(modal instanceof HTMLElement) || !modal.matches(MODAL_SELECTOR)) return;
		prepareModal(modal);
		hideOtherModals(modal);
		document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());
	}, true);

	document.addEventListener('shown.bs.modal', () => {
		window.setTimeout(normalizeModalState, 0);
	}, true);

	document.addEventListener('hidden.bs.modal', event => {
		resetAwardForm(event.target);
		window.setTimeout(normalizeModalState, 0);
	}, true);

	document.addEventListener('keydown', event => {
		if (event.key !== 'Escape') return;
		const openModals = shownModals();
		const modal = openModals[openModals.length - 1];
		if (!modal || modal.getAttribute('data-bs-keyboard') === 'false') return;
		const instance = window.bootstrap?.Modal?.getInstance(modal);
		if (instance) instance.hide();
		else {
			forceHideModal(modal);
			normalizeModalState();
		}
	});

	window.addEventListener('pageshow', () => window.setTimeout(normalizeModalState, 0));
})();
