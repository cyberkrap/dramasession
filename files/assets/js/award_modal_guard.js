(() => {
	'use strict';

	function cleanupAwardModal() {
		document.body.classList.remove('award-modal-open', 'modal-open');
		document.body.style.removeProperty('overflow');
		document.body.style.removeProperty('padding-right');
		document.querySelectorAll('.modal-backdrop').forEach(backdrop => backdrop.remove());
	}

	function resetAwardForm(modal) {
		if (!modal) return;
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

	document.addEventListener('DOMContentLoaded', () => {
		const modal = document.querySelector('#awardModal');
		if (!modal) return;

		if (modal.parentElement !== document.body) document.body.appendChild(modal);

		modal.addEventListener('show.bs.modal', () => {
			cleanupAwardModal();
			document.body.classList.add('award-modal-open');
		});
		modal.addEventListener('shown.bs.modal', () => {
			document.body.classList.add('award-modal-open', 'modal-open');
		});
		modal.addEventListener('hide.bs.modal', () => {
			document.body.classList.remove('award-modal-open');
		});
		modal.addEventListener('hidden.bs.modal', () => {
			cleanupAwardModal();
			resetAwardForm(modal);
		});

		modal.addEventListener('click', event => {
			if (event.target !== modal) return;
			const instance = window.bootstrap?.Modal?.getInstance(modal);
			if (instance) instance.hide();
			else cleanupAwardModal();
		});

		document.addEventListener('keydown', event => {
			if (event.key !== 'Escape' || !modal.classList.contains('show')) return;
			const instance = window.bootstrap?.Modal?.getInstance(modal);
			if (instance) instance.hide();
			else cleanupAwardModal();
		});
	});
})();
