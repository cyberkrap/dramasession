(() => {
	'use strict';

	const rendered = new WeakMap();
	const visualKinds = ['confetti', 'fireflies', 'ricardo', 'firework', 'wholesome', 'shit'];

	function targetForIcon(icon) {
		const comment = icon.closest('.comment-body');
		if (comment) return comment;
		const directPost = icon.closest('#post-root > .card');
		if (directPost) return directPost;
		const card = icon.closest('.card');
		if (card && !card.closest('.modal')) return card;
		return null;
	}

	function countsForTarget(target) {
		const counts = {};
		for (const kind of visualKinds) {
			counts[kind] = Array.from(target.querySelectorAll(`.award-kind-${kind}`))
				.filter((icon) => targetForIcon(icon) === target).length;
		}
		return counts;
	}

	function fingerprint(counts) {
		return visualKinds.map((kind) => `${kind}:${counts[kind] || 0}`).join('|');
	}

	function ensureLayer(target) {
		let layer = Array.from(target.children).find((child) => child.classList && child.classList.contains('content-award-effects'));
		if (!layer) {
			layer = document.createElement('div');
			layer.className = 'content-award-effects';
			layer.setAttribute('aria-hidden', 'true');
			target.appendChild(layer);
		}
		return layer;
	}

	function randomPercent(min = 2, max = 96) {
		return `${min + Math.random() * (max - min)}%`;
	}

	function addFireflies(layer, count) {
		const total = Math.min(24, 7 + count * 4);
		for (let i = 0; i < total; i++) {
			const dot = document.createElement('span');
			dot.className = 'award-firefly';
			dot.style.setProperty('--x', randomPercent());
			dot.style.setProperty('--y', randomPercent(4, 92));
			dot.style.setProperty('--dx', `${-24 + Math.random() * 48}px`);
			dot.style.setProperty('--dy', `${-18 + Math.random() * 36}px`);
			dot.style.setProperty('--delay', `${-Math.random() * 5}s`);
			dot.style.setProperty('--duration', `${3.5 + Math.random() * 4}s`);
			layer.appendChild(dot);
		}
	}

	function addRicardo(layer, count) {
		for (let i = 0; i < Math.min(count, 3); i++) {
			const image = document.createElement('img');
			image.loading = 'lazy';
			image.src = `/i/ricardo${i + 1}.webp?v=20260809-scoped`;
			image.alt = 'Celebration';
			image.className = `award-ricardo award-ricardo-${i + 1}`;
			layer.appendChild(image);
		}
	}

	function startFirework(item, index) {
		const image = item.querySelector('img');
		if (!image) return;

		const launch = () => {
			if (!item.isConnected) return;
			const endTop = 12 + Math.floor(Math.random() * 42);
			item.style.left = randomPercent(8, 88);
			item.style.top = '90%';
			item.style.opacity = '1';
			item.style.filter = `hue-rotate(${Math.floor(Math.random() * 360)}deg)`;
			image.src = '/i/firework-trail.webp?v=20260809-scoped';

			const flight = item.animate(
				[{top: '90%'}, {top: `${endTop}%`}],
				{duration: 850, easing: 'ease-out', fill: 'forwards'}
			);
			flight.onfinish = () => {
				image.src = `/i/firework-explosion.webp?v=${Date.now()}`;
				setTimeout(() => {
					item.style.opacity = '0';
					setTimeout(launch, 1800 + Math.random() * 2600);
				}, 850);
			};
		};
		setTimeout(launch, index * 650);
	}

	function addFireworks(layer, count) {
		for (let i = 0; i < Math.min(count, 4); i++) {
			const item = document.createElement('div');
			item.className = 'award-firework';
			const image = document.createElement('img');
			image.alt = 'Firework';
			image.src = '/i/firework-trail.webp?v=20260809-scoped';
			item.appendChild(image);
			layer.appendChild(item);
			startFirework(item, i);
		}
	}

	function addWholesome(layer, count) {
		for (let i = 0; i < Math.min(count, 4); i++) {
			const image = document.createElement('img');
			image.loading = 'lazy';
			image.src = '/e/marseywholesome.webp';
			image.alt = ':#marseywholesome:';
			image.className = `award-wholesome award-wholesome-${i + 1}`;
			layer.appendChild(image);
		}
	}

	function addSparkTrail(layer, count) {
		const total = Math.min(18, 5 + count * 3);
		for (let i = 0; i < total; i++) {
			const spark = document.createElement('span');
			spark.className = 'award-spark';
			spark.style.setProperty('--x', randomPercent());
			spark.style.setProperty('--y', randomPercent(5, 90));
			spark.style.setProperty('--delay', `${-Math.random() * 3}s`);
			layer.appendChild(spark);
		}
	}

	function renderTarget(target) {
		if (!(target instanceof HTMLElement)) return;
		const counts = countsForTarget(target);
		const signature = fingerprint(counts);
		if (rendered.get(target) === signature) return;
		rendered.set(target, signature);

		for (const cls of Array.from(target.classList)) {
			if (cls.startsWith('has-award-')) target.classList.remove(cls);
		}
		for (const kind of visualKinds) {
			if (counts[kind]) target.classList.add(`has-award-${kind}`);
		}
		target.classList.add('award-effect-target');

		const oldLayer = Array.from(target.children).find((child) => child.classList && child.classList.contains('content-award-effects'));
		if (oldLayer) oldLayer.remove();
		if (!visualKinds.some((kind) => counts[kind])) return;

		const layer = ensureLayer(target);
		if (counts.fireflies) addFireflies(layer, counts.fireflies);
		if (counts.ricardo) addRicardo(layer, counts.ricardo);
		if (counts.firework) addFireworks(layer, counts.firework);
		if (counts.wholesome) addWholesome(layer, counts.wholesome);
		if (counts.shit) addSparkTrail(layer, counts.shit);
	}

	function scan(root = document) {
		const icons = [];
		if (root instanceof HTMLElement && /(^|\s)award-kind-/.test(root.className || '')) icons.push(root);
		root.querySelectorAll?.('[class*="award-kind-"]').forEach((icon) => icons.push(icon));
		const targets = new Set();
		for (const icon of icons) {
			const target = targetForIcon(icon);
			if (target) targets.add(target);
		}
		targets.forEach(renderTarget);
	}

	function init() {
		scan(document);
		const observer = new MutationObserver((mutations) => {
			for (const mutation of mutations) {
				for (const node of mutation.addedNodes) {
					if (node instanceof HTMLElement && !node.classList.contains('content-award-effects')) scan(node);
				}
			}
		});
		observer.observe(document.body, {childList: true, subtree: true});
	}

	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once: true});
	else init();
})();
