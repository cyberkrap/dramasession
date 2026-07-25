(() => {
	'use strict';

	const ACTION_PATTERN = /\/(subscribe|unsubscribe|save_post|unsave_post|save_comment|unsave_comment)\/(\d+)/;
	const RELATIONSHIP_BUTTON_SELECTOR = 'button[data-onclick], button[data-areyousure]';

	function relationshipFromAction(actionText) {
		const match = String(actionText || '').match(ACTION_PATTERN);
		if (!match) return null;

		const action = match[1];
		const id = Number(match[2]);
		if (!Number.isInteger(id) || id <= 0) return null;

		if (action === 'subscribe' || action === 'unsubscribe') {
			return {
				scope: 'post',
				kind: 'subscriptions',
				id,
				key: `post:subscriptions:${id}`,
				delta: action === 'subscribe' ? 1 : -1,
			};
		}

		const scope = action.endsWith('_comment') ? 'comment' : 'post';
		return {
			scope,
			kind: 'saves',
			id,
			key: `${scope}:saves:${id}`,
			delta: action.startsWith('unsave') ? -1 : 1,
		};
	}

	function relationshipFromButton(button) {
		return relationshipFromAction(
			button.getAttribute('data-onclick') || button.getAttribute('data-areyousure')
		);
	}

	function relationshipButtons(missingOnly = false) {
		return Array.from(document.querySelectorAll(RELATIONSHIP_BUTTON_SELECTOR))
			.map((button) => ({button, relationship: relationshipFromButton(button)}))
			.filter((entry) => entry.relationship)
			.filter((entry) => !missingOnly || !entry.button.querySelector('.relationship-count'));
	}

	function setCount(key, count) {
		const safeCount = Math.max(0, Number(count) || 0);
		document.querySelectorAll('.relationship-count').forEach((element) => {
			if (element.dataset.relationshipCountKey !== key) return;
			element.dataset.relationshipCount = String(safeCount);
			element.textContent = ` [${safeCount.toLocaleString()}]`;
		});
	}

	function adjustCount(key, delta) {
		const matching = Array.from(document.querySelectorAll('.relationship-count'))
			.filter((element) => element.dataset.relationshipCountKey === key);
		if (!matching.length) return;

		const current = Number(matching[0].dataset.relationshipCount || 0);
		setCount(key, current + delta);
	}

	function attachCount(button, relationship, count) {
		let counter = button.querySelector('.relationship-count');
		if (!counter) {
			counter = document.createElement('span');
			counter.className = 'relationship-count';
			button.append(counter);
		}
		counter.dataset.relationshipCountKey = relationship.key;
		counter.dataset.relationshipCount = String(Math.max(0, Number(count) || 0));
		counter.textContent = ` [${Math.max(0, Number(count) || 0).toLocaleString()}]`;
	}

	async function loadCounts() {
		const entries = relationshipButtons(true);
		if (!entries.length) return;

		const postIds = new Set();
		const commentIds = new Set();
		entries.forEach(({relationship}) => {
			if (relationship.scope === 'post') postIds.add(relationship.id);
			else commentIds.add(relationship.id);
		});

		const params = new URLSearchParams();
		if (postIds.size) params.set('post_ids', Array.from(postIds).join(','));
		if (commentIds.size) params.set('comment_ids', Array.from(commentIds).join(','));

		try {
			const response = await fetch(`/relationship-counts?${params.toString()}`, {
				credentials: 'same-origin',
				headers: {'xhr': 'xhr'},
			});
			if (!response.ok) return;
			const data = await response.json();

			entries.forEach(({button, relationship}) => {
				const scopeData = relationship.scope === 'post'
					? data.posts?.[String(relationship.id)]
					: data.comments?.[String(relationship.id)];
				attachCount(button, relationship, scopeData?.[relationship.kind] || 0);
			});
		} catch (error) {
			// Counts are supplementary. Keep the existing controls usable if loading fails.
		}
	}

	function installCountUpdates() {
		if (typeof window.postToastSwitch !== 'function') return;
		const originalPostToastSwitch = window.postToastSwitch;

		window.postToastSwitch = function(t, url, button1, button2, cls, extraActionsOnSuccess, method = 'POST') {
			const relationship = relationshipFromAction(url);
			let successHandler = extraActionsOnSuccess;

			if (relationship) {
				successHandler = function(xhr) {
					adjustCount(relationship.key, relationship.delta);
					if (typeof extraActionsOnSuccess === 'function') {
						return extraActionsOnSuccess(xhr);
					}
				};
			}

			return originalPostToastSwitch(
				t,
				url,
				button1,
				button2,
				cls,
				successHandler,
				method,
			);
		};
	}

	function installSubscribeConfirmationCompatibility() {
		if (typeof window.areyousure !== 'function') return;
		const originalAreYouSure = window.areyousure;

		window.areyousure = function(t) {
			const counter = t?.querySelector?.('.relationship-count');
			if (counter) counter.remove();
			const result = originalAreYouSure(t);
			if (counter) t.append(counter);
			return result;
		};
	}

	function watchDynamicControls() {
		let timer = null;
		const observer = new MutationObserver((mutations) => {
			const hasNewControls = mutations.some((mutation) =>
				Array.from(mutation.addedNodes).some((node) =>
					node.nodeType === Node.ELEMENT_NODE && (
						node.matches?.(RELATIONSHIP_BUTTON_SELECTOR) ||
						node.querySelector?.(RELATIONSHIP_BUTTON_SELECTOR)
					)
				)
			);
			if (!hasNewControls) return;
			clearTimeout(timer);
			timer = setTimeout(loadCounts, 50);
		});
		observer.observe(document.body, {childList: true, subtree: true});
	}

	function initialise() {
		loadCounts();
		watchDynamicControls();
	}

	installCountUpdates();
	installSubscribeConfirmationCompatibility();
	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', initialise, {once: true});
	} else {
		initialise();
	}
})();
