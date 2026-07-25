(() => {
	'use strict';

	const ACTION_PATTERN = /\/(subscribe|unsubscribe|save_post|unsave_post|save_comment|unsave_comment)\/(\d+)/;
	const RELATIONSHIP_BUTTON_SELECTOR = [
		'button[data-relationship-kind][data-relationship-id]',
		'button[data-onclick]',
		'button[data-areyousure]',
	].join(', ');
	const countCache = new Map();

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
		const actionRelationship = relationshipFromAction(
			button.getAttribute('data-onclick') || button.getAttribute('data-areyousure')
		);
		const scope = button.dataset.relationshipScope;
		const kind = button.dataset.relationshipKind;
		const id = Number(button.dataset.relationshipId);

		if (
			(scope === 'post' || scope === 'comment') &&
			(kind === 'saves' || kind === 'subscriptions') &&
			Number.isInteger(id) && id > 0
		) {
			return {
				scope,
				kind,
				id,
				key: `${scope}:${kind}:${id}`,
				delta: actionRelationship?.delta || 0,
			};
		}

		return actionRelationship;
	}

	function relationshipButtons(missingOnly = false) {
		return Array.from(document.querySelectorAll(RELATIONSHIP_BUTTON_SELECTOR))
			.map((button) => ({button, relationship: relationshipFromButton(button)}))
			.filter((entry) => entry.relationship)
			.filter((entry) => !missingOnly || !entry.button.querySelector('.relationship-count'));
	}

	function formatCount(count) {
		return Math.max(0, Number(count) || 0).toLocaleString('en-US');
	}

	function attachCount(button, relationship, count) {
		const safeCount = Math.max(0, Number(count) || 0);
		let counter = button.querySelector('.relationship-count');
		if (!counter) {
			counter = document.createElement('span');
			counter.className = 'relationship-count';
			counter.setAttribute('aria-live', 'polite');
			button.append(counter);
		}
		counter.dataset.relationshipCountKey = relationship.key;
		counter.dataset.relationshipCount = String(safeCount);
		counter.textContent = ` [${formatCount(safeCount)}]`;
		countCache.set(relationship.key, safeCount);
	}

	function setCount(key, count) {
		const safeCount = Math.max(0, Number(count) || 0);
		countCache.set(key, safeCount);
		document.querySelectorAll('.relationship-count').forEach((element) => {
			if (element.dataset.relationshipCountKey !== key) return;
			element.dataset.relationshipCount = String(safeCount);
			element.textContent = ` [${formatCount(safeCount)}]`;
		});
	}

	function adjustCount(key, delta) {
		const current = countCache.has(key)
			? countCache.get(key)
			: Number(
				Array.from(document.querySelectorAll('.relationship-count'))
					.find((element) => element.dataset.relationshipCountKey === key)
					?.dataset.relationshipCount || 0
			);
		setCount(key, current + delta);
	}

	async function loadCounts() {
		const entries = relationshipButtons(true);
		if (!entries.length) return;

		const unresolvedEntries = [];
		entries.forEach(({button, relationship}) => {
			if (countCache.has(relationship.key)) {
				attachCount(button, relationship, countCache.get(relationship.key));
			} else {
				unresolvedEntries.push({button, relationship});
			}
		});
		if (!unresolvedEntries.length) return;

		const postIds = new Set();
		const commentIds = new Set();
		unresolvedEntries.forEach(({relationship}) => {
			if (relationship.scope === 'post') postIds.add(relationship.id);
			else commentIds.add(relationship.id);
		});

		const params = new URLSearchParams();
		if (postIds.size) params.set('post_ids', Array.from(postIds).join(','));
		if (commentIds.size) params.set('comment_ids', Array.from(commentIds).join(','));
		if (!params.toString()) return;

		try {
			const response = await fetch(`/relationship-counts?${params.toString()}`, {
				credentials: 'same-origin',
				headers: {'xhr': 'xhr'},
			});
			if (!response.ok) return;
			const data = await response.json();

			unresolvedEntries.forEach(({button, relationship}) => {
				const scopeData = relationship.scope === 'post'
					? data.posts?.[String(relationship.id)]
					: data.comments?.[String(relationship.id)];
				attachCount(button, relationship, scopeData?.[relationship.kind] || 0);
			});
		} catch (error) {
			// Counts are supplementary. Existing controls remain usable if loading fails.
		}
	}

	function installCountUpdates() {
		if (window.__relationshipCountPostToastWrapped) return;
		if (typeof window.postToastSwitch !== 'function') return;
		window.__relationshipCountPostToastWrapped = true;
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
		if (window.__relationshipCountAreYouSureWrapped) return;
		if (typeof window.areyousure !== 'function') return;
		window.__relationshipCountAreYouSureWrapped = true;
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
			timer = setTimeout(loadCounts, 40);
		});
		observer.observe(document.body, {childList: true, subtree: true});
	}

	function initialise() {
		installCountUpdates();
		installSubscribeConfirmationCompatibility();
		loadCounts();
		watchDynamicControls();
	}

	if (document.readyState === 'complete') {
		initialise();
	} else {
		document.addEventListener('DOMContentLoaded', initialise, {once: true});
	}
})();