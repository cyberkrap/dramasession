(() => {
	'use strict';

	const plateSelector = [
		'.user-name > .mod',
		'.chat-username.mod',
		'.post-meta .mod',
		'.comment .user-info .mod',
	].join(',');

	const effectClasses = [
		'username-effect-host',
		'username-effect',
		'username-effect-text',
		'username-effect-plate',
		'username-effect--ready',
	];

	const effectAttributes = [
		'data-username-effects',
		'data-username-effect-color',
		'data-username-effect-current',
		'data-username-effect-request',
		'data-username-effect-user',
		'data-username-effect-visible',
	];

	const effectStyleProperties = [
		'--username-effect-image',
		'--username-effect-text-color',
		'background-image',
		'background-position',
		'background-repeat',
		'background-size',
		'background-origin',
		'background-clip',
		'-webkit-background-clip',
		'-webkit-text-fill-color',
		'color',
		'text-shadow',
		'filter',
	];

	function stripEffectPayload(element) {
		if (!(element instanceof Element)) return;

		for (const attribute of effectAttributes) {
			if (element.hasAttribute(attribute)) element.removeAttribute(attribute);
		}

		if (!element.matches('.user-name[data-pop-info]')) return;
		try {
			const payload = JSON.parse(element.dataset.popInfo || '{}');
			let changed = false;
			if (Object.prototype.hasOwnProperty.call(payload, 'username_effects')) {
				delete payload.username_effects;
				changed = true;
			}
			if (Object.prototype.hasOwnProperty.call(payload, 'username_effect_color')) {
				delete payload.username_effect_color;
				changed = true;
			}
			if (changed) element.dataset.popInfo = JSON.stringify(payload);
		} catch (_) {
			// Leave unrelated popover data untouched when legacy markup is malformed.
		}
	}

	function normalisePlate(plate) {
		if (!(plate instanceof Element) || !plate.matches(plateSelector)) return;

		if (!plate.classList.contains('admin-nameplate')) plate.classList.add('admin-nameplate');
		for (const className of effectClasses) plate.classList.remove(className);
		for (const attribute of effectAttributes) {
			if (plate.hasAttribute(attribute)) plate.removeAttribute(attribute);
		}
		if (plate instanceof HTMLElement) {
			for (const property of effectStyleProperties) {
				if (plate.style.getPropertyValue(property)) plate.style.removeProperty(property);
			}
		}

		const trigger = plate.closest('.user-name');
		if (trigger) {
			if (trigger.dataset.distinguished !== '1') trigger.dataset.distinguished = '1';
			stripEffectPayload(trigger);
		}
	}

	function process(root) {
		if (!(root instanceof Element || root instanceof Document)) return;
		if (root instanceof Element && root.matches(plateSelector)) normalisePlate(root);
		if (root.querySelectorAll) root.querySelectorAll(plateSelector).forEach(normalisePlate);
	}

	process(document);

	const observer = new MutationObserver(mutations => {
		for (const mutation of mutations) {
			if (mutation.type === 'attributes') {
				const target = mutation.target;
				if (target instanceof Element) {
					if (target.matches(plateSelector)) normalisePlate(target);
					else if (target.matches('.user-name') && target.querySelector(':scope > .mod')) {
						normalisePlate(target.querySelector(':scope > .mod'));
					}
				}
				continue;
			}
			for (const node of mutation.addedNodes) {
				if (node instanceof Element) process(node);
			}
		}
	});

	observer.observe(document.documentElement, {
		childList: true,
		subtree: true,
		attributes: true,
		attributeFilter: [
			'class',
			'style',
			'data-pop-info',
			'data-username-effects',
			'data-username-effect-color',
			'data-username-effect-current',
			'data-username-effect-request',
		],
	});
})();
