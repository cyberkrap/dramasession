document.addEventListener('DOMContentLoaded', () => {
	const modalSelector = '.modal[id*="award" i], .modal[id^="giveaward" i], .modal[data-award-modal]';

	function prepareAwardModal(modal) {
		if (!(modal instanceof HTMLElement) || modal.dataset.awardModalGuard === '1') return;
		modal.dataset.awardModalGuard = '1';

		if (modal.parentElement !== document.body) {
			document.body.appendChild(mod