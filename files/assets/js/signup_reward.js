(() => {
	'use strict';

	const DISMISSED_KEY = 'obsession-signup-reward-dismissed';

	function number(value) {
		return Number(value || 0).toLocaleString('en-GB');
	}

	function burst(origin) {
		if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
		const colors = ['#ef233c', '#ffd78a', '#ffffff', '#b5122f'];
		const rect = origin.getBoundingClientRect();
		const x = rect.left + rect.width / 2;
		const y = rect.top + rect.height / 2;
		for (let i = 0; i < 24; i += 1) {
			const spark = document.createElement('span');
			const angle = (Math.PI * 2 * i) / 24;
			const distance = 70 + Math.random() * 90;
			spark.className = 'signup-reward-spark';
			spark.style.left = `${x}px`;
			spark.style.top = `${y}px`;
			spark.style.color = colors[i % colors.length];
			spark.style.setProperty('--spark-x', `${Math.cos(angle) * distance}px`);
			spark.style.setProperty('--spark-y', `${Math.sin(angle) * distance + 35}px`);
			spark.style.setProperty('--spark-r', `${Math.round(Math.random() * 540 - 270)}deg`);
			document.body.appendChild(spark);
			window.setTimeout(() => spark.remove(), 1000);
		}
	}

	function applyReward(modal, reward) {
		modal.querySelector('#signupRewardIntro').textContent = `You are one of ${reward.audience_label} in the signup campaign.`;
		modal.querySelector('#signupRewardPosition').textContent = `#${reward.slot} of 200`;
		modal.querySelector('#signupRewardCoins').textContent = `${reward.coins_formatted || number(reward.coins)} Wishcoins`;
		modal.querySelector('#signupRewardValue').textContent = `${reward.value_label} worth of site currency`;
	}

	async function fetchReward() {
		const response = await fetch('/api/signup-reward', {
			headers: {'xhr': 'xhr'},
			credentials: 'same-origin',
			cache: 'no-store',
		});
		if (!response.ok) return null;
		return response.json();
	}

	async function claimReward(modal, claimButton, feedback) {
		claimButton.disabled = true;
		claimButton.textContent = 'Claiming…';
		feedback.classList.remove('is-error');
		feedback.textContent = '';

		const body = new FormData();
		body.append('formkey', modal.dataset.formkey || '');
		try {
			const response = await fetch('/api/signup-reward/claim', {
				method: 'POST',
				headers: {'xhr': 'xhr'},
				credentials: 'same-origin',
				body,
			});
			let data = null;
			try { data = await response.json(); } catch (_) { data = null; }
			if (!response.ok || !data || !data.claimed) {
				throw new Error((data && data.error) || 'The reward could not be claimed. Please try again.');
			}

			modal.classList.add('is-claimed');
			modal.querySelector('.signup-reward-kicker').textContent = 'Reward claimed';
			modal.querySelector('#signupRewardTitle').textContent = 'You’re all set';
			modal.querySelector('#signupRewardIntro').textContent = data.message;
			modal.querySelector('#signupRewardPosition').textContent = `Claimed spot #${data.slot}`;
			modal.querySelector('.signup-reward-mark i').className = 'fas fa-check';
			const laterButton = modal.querySelector('#signupRewardLater');
			if (laterButton) laterButton.remove();
			modal.querySelector('#signupRewardActions')?.classList.add('is-single');
			claimButton.textContent = 'Start exploring';
			claimButton.disabled = false;
			claimButton.setAttribute('data-bs-dismiss', 'modal');
			feedback.textContent = '';
			sessionStorage.removeItem(DISMISSED_KEY);
			burst(claimButton);
		} catch (error) {
			claimButton.disabled = false;
			claimButton.textContent = 'Claim now';
			feedback.classList.add('is-error');
			feedback.textContent = error.message;
		}
	}

	async function initialize() {
		const modal = document.getElementById('signupRewardModal');
		if (!modal || typeof bootstrap === 'undefined' || !bootstrap.Modal) return;
		if (sessionStorage.getItem(DISMISSED_KEY) === '1') return;

		let reward = null;
		try { reward = await fetchReward(); } catch (_) { return; }
		if (!reward || !reward.eligible) return;

		applyReward(modal, reward);
		const instance = bootstrap.Modal.getOrCreateInstance(modal, {
			backdrop: 'static',
			keyboard: false,
		});
		const laterButton = modal.querySelector('#signupRewardLater');
		const claimButton = modal.querySelector('#signupRewardClaim');
		const feedback = modal.querySelector('#signupRewardFeedback');
		laterButton.addEventListener('click', () => sessionStorage.setItem(DISMISSED_KEY, '1'), {once: true});
		claimButton.addEventListener('click', () => {
			if (modal.classList.contains('is-claimed')) return;
			claimReward(modal, claimButton, feedback);
		});
		instance.show();
	}

	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize, {once: true});
	else initialize();
})();
