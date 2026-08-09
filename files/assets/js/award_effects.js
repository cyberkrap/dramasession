(() => {
	'use strict';

	const rendered = new WeakSet();
	const loadedScripts = new Map();

	function loadScript(src) {
		if (loadedScripts.has(src)) return loadedScripts.get(src);
		const existing = Array.from(document.scripts).find((s) => s.src && s.src.includes(src));
		if (existing) {
			const ready = Promise.resolve();
			loadedScripts.set(src, ready);
			return ready;
		}

		const promise = new Promise((resolve, reject) => {
			const script = document.createElement('script');
			script.src = `/assets/js/${src}?v=20260809-awards`;
			script.defer = true;
			script.onload = resolve;
			script.onerror = reject;
			document.head.appendChild(script);
		});
		loadedScripts.set(src, promise);
		return promise;
	}

	function countAward(comment, kind) {
		return comment.querySelectorAll(`.award-kind-${kind}`).length;
	}

	function getLayer(comment) {
		let layer = comment.querySelector(':scope > .comment-award-effects');
		if (!layer) {
			layer = document.createElement('div');
			layer.className = 'comment-award-effects';
			layer.setAttribute('aria-hidden', 'true');
			comment.appendChild(layer);
		}
		return layer;
	}

	function addStackable(layer, kind, count, src, alt) {
		const stack = document.createElement('div');
		stack.className = `comment-award-stack comment-award-stack-${kind}`;
		for (let i = 0; i < Math.min(count, 4); i++) {
			const item = document.createElement('div');
			item.className = `comment-${kind} comment-${kind}-${i + 1}`;
			const image = document.createElement('img');
			image.loading = 'lazy';
			image.src = src;
			image.alt = alt;
			item.appendChild(image);
			stack.appendChild(item);
		}
		layer.appendChild(stack);
	}

	function addRicardo(layer, count) {
		for (let i = 0; i < Math.min(count, 3); i++) {
			const item = document.createElement('div');
			item.className = `comment-ricardo comment-ricardo-${i + 1}`;
			const image = document.createElement('img');
			image.loading = 'lazy';
			image.src = `/i/ricardo${i + 1}.webp?v=20260809-awards`;
			image.alt = 'Celebration';
			item.appendChild(image);
			layer.appendChild(item);
		}
	}

	function startFirework(item, index) {
		const image = item.querySelector('img');
		if (!image) return;

		const launch = () => {
			if (!item.isConnected) return;
			const endTop = 8 + Math.floor(Math.random() * 48);
			item.style.left = `${5 + Math.floor(Math.random() * 86)}%`;
			item.style.top = '92%';
			item.style.opacity = '1';
			item.style.filter = `hue-rotate(${Math.floor(Math.random() * 360)}deg)`;
			image.src = `/i/firework-trail.webp?v=20260809-awards`;

			const flight = item.animate(
				[{ top: '92%' }, { top: `${endTop}%` }],
				{ duration: 900, easing: 'ease-out', fill: 'forwards' }
			);

			flight.onfinish = () => {
				image.src = `/i/firework-explosion.webp?v=${Date.now()}`;
				setTimeout(() => {
					item.style.opacity = '0';
					setTimeout(launch, 1800 + Math.floor(Math.random() * 2500));
				}, 1100);
			};
		};

		setTimeout(launch, index * 700);
	}

	function addFireworks(layer, count) {
		for (let i = 0; i < Math.min(count, 4); i++) {
			const item = document.createElement('div');
			item.className = 'comment-firework';
			const image = document.createElement('img');
			image.src = '/i/firework-trail.webp?v=20260809-awards';
			image.alt = 'Firework';
			item.appendChild(image);
			layer.appendChild(item);
			startFirework(item, i);
		}
	}

	async function enableCritterEffect(kind) {
		try {
			await loadScript('vendor/critters.js');
			await loadScript(kind === 'fireflies' ? 'fireflies.js' : 'bugs.js');
		} catch (error) {
			console.warn(`Unable to load ${kind} award effect`, error);
		}
	}

	function renderComment(comment) {
		if (!(comment instanceof HTMLElement) || rendered.has(comment)) return;
		if (!comment.querySelector('[class*="award-kind-"]')) return;
		rendered.add(comment);

		const wholesome = countAward(comment, 'wholesome');
		const train = countAward(comment, 'train');
		const scooter = countAward(comment, 'scooter');
		const ricardo = countAward(comment, 'ricardo');
		const firework = countAward(comment, 'firework');
		const sparks = countAward(comment, 'shit');
		const fireflies = countAward(comment, 'fireflies');

		if (wholesome || train || scooter || ricardo || firework) {
			const layer = getLayer(comment);
			if (wholesome) addStackable(layer, 'wholesome', wholesome, '/e/marseywholesome.webp', ':#marseywholesome:');
			if (train) addStackable(layer, 'train', train, '/e/marseytrain.webp', ':#marseytrain:');
			if (scooter) addStackable(layer, 'scooter', scooter, '/e/marseyscooter.webp', ':#marseyscooter:');
			if (ricardo) addRicardo(layer, ricardo);
			if (firework) addFireworks(layer, firework);
		}

		if (sparks) enableCritterEffect('shit');
		if (fireflies) enableCritterEffect('fireflies');
	}

	function scan(root = document) {
		if (root instanceof HTMLElement && root.matches('.comment-body')) renderComment(root);
		root.querySelectorAll?.('.comment-body').forEach(renderComment);
	}

	function init() {
		scan(document);
		const observer = new MutationObserver((mutations) => {
			for (const mutation of mutations) {
				for (const node of mutation.addedNodes) {
					if (node instanceof HTMLElement) scan(node);
				}
			}
		});
		observer.observe(document.body, { childList: true, subtree: true });
	}

	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
	else init();
})();
