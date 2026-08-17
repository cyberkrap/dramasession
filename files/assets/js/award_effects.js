(() => {
	'use strict';

	const rendered = new WeakMap();
	const visualKinds = ['confetti', 'fireflies', 'ricardo', 'firework', 'wholesome'];

	function isStandaloneThread() {
		return document.body && document.body.id === 'thread';
	}

	function targetForIcon(icon) {
		if (!isStandaloneThread()) return null;

		// .comment-body contains nested replies; .comment-anchor is the exact
		// awarded comment only. Binding here prevents effects leaking downward.
		const comment = icon.closest('.comment-anchor');
		if (comment) return comment;

		const directPost = icon.closest('#post-root > .card');
		if (directPost) return directPost;

		// Award visual effects belong to the opened thread only, never unrelated
		// homepage/profile/search cards rendered beside it.
		return null;
	}

	function iconsFor(target, kind) {
		return Array.from(target.querySelectorAll(`.award-kind-${kind}`))
			.filter((icon) => targetForIcon(icon) === target);
	}

	function decorateEmojiAwardIcon(icon, name) {
		if (!icon || !name || icon.dataset.emojiAwardDecorated === name) return;
		icon.dataset.emojiAwardDecorated = name;
		icon.style.backgroundImage = `url('/e/${encodeURIComponent(name)}.webp')`;
		icon.style.backgroundPosition = 'center';
		icon.style.backgroundRepeat = 'no-repeat';
		icon.style.backgroundSize = 'contain';
		icon.style.display = 'inline-block';
		icon.style.width = '24px';
		icon.style.height = '24px';
		icon.style.fontSize = '0';
		icon.style.color = 'transparent';
		icon.style.verticalAlign = 'middle';
	}

	function emojiNameForIcon(icon) {
		for (const token of icon.classList) {
			if (token.startsWith('award-emoji-name-')) {
				const value = token.slice('award-emoji-name-'.length);
				if (/^[A-Za-z0-9_-]{1,80}$/.test(value)) {
					decorateEmojiAwardIcon(icon, value);
					return value;
				}
			}
		}
		// Historical Wholesome awards did not store a chosen emoji. Keep them
		// visible using their original asset instead of silently dropping them.
		return 'marseywholesome';
	}

	function dataForTarget(target) {
		const counts = {};
		for (const kind of visualKinds) counts[kind] = iconsFor(target, kind).length;
		const emojiNames = iconsFor(target, 'wholesome').map(emojiNameForIcon);
		return {counts, emojiNames};
	}

	function fingerprint(data) {
		const countPart = visualKinds.map((kind) => `${kind}:${data.counts[kind] || 0}`).join('|');
		return `${countPart}|emoji:${data.emojiNames.join(',')}`;
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

	function randomSigned(min, max) {
		const value = min + Math.random() * (max - min);
		return Math.random() < .5 ? -value : value;
	}

	function animateFirefly(dot, dx, dy, duration) {
		if (typeof dot.animate !== 'function') return;

		dot.style.animation = 'none';
		dot.animate([
			{transform: 'translate3d(0, 0, 0) scale(.55)', opacity: .15},
			{transform: `translate3d(${dx * .38}px, ${dy * .35}px, 0) scale(1.18)`, opacity: 1, offset: .42},
			{transform: `translate3d(${dx}px, ${dy}px, 0) scale(.78)`, opacity: .32}
		], {
			duration,
			delay: -Math.random() * duration,
			iterations: Infinity,
			direction: 'alternate',
			easing: 'ease-in-out'
		});
	}

	function addFireflies(layer, count) {
		const total = Math.min(24, 7 + count * 4);
		for (let i = 0; i < total; i++) {
			const dot = document.createElement('span');
			const dx = -55 + Math.random() * 110;
			const dy = -38 + Math.random() * 76;
			const duration = 2600 + Math.random() * 3600;
			dot.className = 'award-firefly';
			dot.style.setProperty('--x', randomPercent());
			dot.style.setProperty('--y', randomPercent(4, 92));
			dot.style.setProperty('--dx', `${dx}px`);
			dot.style.setProperty('--dy', `${dy}px`);
			dot.style.setProperty('--delay', `${-Math.random() * 5}s`);
			dot.style.setProperty('--duration', `${duration}ms`);
			layer.appendChild(dot);
			animateFirefly(dot, dx, dy, duration);
		}
	}

	function startRicardoRoam(layer, sprites) {
		if (!sprites.length) return;

		requestAnimationFrame(() => {
			if (!layer.isConnected) return;
			const width = Math.max(1, layer.clientWidth);
			const height = Math.max(1, layer.clientHeight);
			for (const sprite of sprites) {
				const size = sprite.element.offsetWidth || 46;
				sprite.x = Math.random() * Math.max(0, width - size);
				sprite.y = Math.random() * Math.max(0, height - size);
				sprite.element.style.transform = `translate3d(${sprite.x}px, ${sprite.y}px, 0)`;
			}

			let last = performance.now();
			const frame = (now) => {
				if (!layer.isConnected) return;
				const dt = Math.min(40, Math.max(0, now - last));
				last = now;
				const layerWidth = Math.max(1, layer.clientWidth);
				const layerHeight = Math.max(1, layer.clientHeight);

				for (const sprite of sprites) {
					const size = sprite.element.offsetWidth || 46;
					const maxX = Math.max(0, layerWidth - size);
					const maxY = Math.max(0, layerHeight - size);
					sprite.x += sprite.vx * dt;
					sprite.y += sprite.vy * dt;

					if (sprite.x <= 0) {
						sprite.x = 0;
						sprite.vx = Math.abs(sprite.vx);
					} else if (sprite.x >= maxX) {
						sprite.x = maxX;
						sprite.vx = -Math.abs(sprite.vx);
					}
					if (sprite.y <= 0) {
						sprite.y = 0;
						sprite.vy = Math.abs(sprite.vy);
					} else if (sprite.y >= maxY) {
						sprite.y = maxY;
						sprite.vy = -Math.abs(sprite.vy);
					}

					sprite.element.style.transform = `translate3d(${sprite.x}px, ${sprite.y}px, 0)`;
				}
				requestAnimationFrame(frame);
			};
			requestAnimationFrame(frame);
		});
	}

	function addRicardo(layer, count) {
		// The legacy effect already displayed at most three Ricardos. Keep that
		// density, but let those dancers roam freely instead of pinning them to
		// three corners.
		const total = Math.min(Math.max(0, count), 3);
		const sprites = [];
		for (let i = 0; i < total; i++) {
			const roamer = document.createElement('span');
			roamer.className = 'award-ricardo-roamer';

			const image = document.createElement('img');
			image.loading = 'lazy';
			image.src = `/i/ricardo${(i % 3) + 1}.webp?v=20260816-roam`;
			image.alt = '';
			image.className = 'award-ricardo';
			image.style.animationDelay = `${-Math.random() * 1.8}s`;
			roamer.appendChild(image);
			layer.appendChild(roamer);

			sprites.push({
				element: roamer,
				x: 0,
				y: 0,
				vx: randomSigned(.035, .085),
				vy: randomSigned(.03, .075),
			});
		}
		startRicardoRoam(layer, sprites);
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

	function addEmojiRain(layer, emojiNames) {
		for (const name of emojiNames.slice(0, 30)) {
			const image = document.createElement('img');
			const duration = 5200 + Math.random() * 5200;
			image.loading = 'lazy';
			image.src = `/e/${encodeURIComponent(name)}.webp`;
			image.alt = '';
			image.className = 'award-emoji-rain';
			image.style.setProperty('--x', randomPercent(1, 96));
			image.style.setProperty('--size', `${34 + Math.random() * 20}px`);
			image.style.setProperty('--sway-a', `${randomSigned(12, 48)}px`);
			image.style.setProperty('--sway-b', `${randomSigned(18, 70)}px`);
			image.style.setProperty('--sway-c', `${randomSigned(12, 58)}px`);
			image.style.setProperty('--rot-a', `${randomSigned(18, 85)}deg`);
			image.style.setProperty('--rot-b', `${randomSigned(120, 310)}deg`);
			image.style.setProperty('--duration', `${duration}ms`);
			image.style.setProperty('--delay', `${-Math.random() * duration}ms`);
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
		if (!(target instanceof HTMLElement) || !isStandaloneThread()) return;
		const data = dataForTarget(target);
		const counts = data.counts;
		const signature = fingerprint(data);
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
		if (counts.wholesome) addEmojiRain(layer, data.emojiNames);
	}

	function scan(root = document) {
		if (!isStandaloneThread()) return;
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
		if (!isStandaloneThread()) return;
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
