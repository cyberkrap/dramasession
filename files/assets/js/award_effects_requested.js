(() => {
	'use strict';

	const rendered = new WeakMap();
	const scheduled = new Set();
	const assetBase = '/assets/images/awards/';
	const largeKinds = new Set(['truthnuke', 'truthnova', 'lovebomb']);
	const decorativeKinds = ['furry', 'shit', 'fireflies', 'ricardo', 'firework', 'wholesome', 'confetti'];

	const isThread = () => document.body && document.body.id === 'thread';

	function ownerForIcon(icon) {
		if (!(icon instanceof HTMLElement)) return null;
		return icon.closest('.comment-anchor') || icon.closest('#post-root > .card');
	}

	function bodyHost(owner) {
		if (!owner) return null;
		if (owner.classList.contains('comment-anchor')) {
			return Array.from(owner.children).find((el) => el.classList?.contains('comment-text')) || null;
		}
		return owner.querySelector('#post-body') || owner.querySelector('#post-content');
	}

	function kindForIcon(icon) {
		for (const cls of icon.classList || []) {
			if (cls.startsWith('award-kind-')) return cls.slice(11);
		}
		return null;
	}

	function timestampForIcon(icon) {
		for (const cls of icon.classList || []) {
			if (!cls.startsWith('award-ts-')) continue;
			const value = Number.parseInt(cls.slice(9), 10);
			if (Number.isFinite(value)) return value;
		}
		return 0;
	}

	function iconsFor(owner, kind) {
		return Array.from(owner.querySelectorAll(`.award-kind-${kind}`))
			.filter((icon) => ownerForIcon(icon) === owner);
	}

	function emojiName(icon) {
		for (const cls of icon.classList || []) {
			if (!cls.startsWith('award-emoji-name-')) continue;
			const value = cls.slice(17);
			if (/^[A-Za-z0-9_-]{1,80}$/.test(value)) return value;
		}
		return null;
	}

	function decorateEmojiIcon(icon, name) {
		if (!name) return;
		Object.assign(icon.style, {
			backgroundImage: `url('/e/${encodeURIComponent(name)}.webp')`,
			backgroundPosition: 'center',
			backgroundRepeat: 'no-repeat',
			backgroundSize: 'contain',
			display: 'inline-block',
			width: '24px',
			height: '24px',
			fontSize: '0',
			color: 'transparent',
			verticalAlign: 'middle',
		});
	}

	function dataFor(owner) {
		const counts = {};
		for (const kind of decorativeKinds) counts[kind] = iconsFor(owner, kind).length;
		const emojiAwards = iconsFor(owner, 'wholesome').map((icon) => {
			const name = emojiName(icon);
			decorateEmojiIcon(icon, name);
			return name;
		});

		let latestLarge = null;
		let order = 0;
		for (const icon of owner.querySelectorAll('[class*="award-kind-"]')) {
			if (ownerForIcon(icon) !== owner) continue;
			const kind = kindForIcon(icon);
			if (!largeKinds.has(kind)) continue;
			const candidate = {kind, timestamp: timestampForIcon(icon), order: order++};
			if (!latestLarge || candidate.timestamp > latestLarge.timestamp ||
				(candidate.timestamp === latestLarge.timestamp && candidate.order >= latestLarge.order)) latestLarge = candidate;
		}
		return {counts, emojiAwards, latestLarge};
	}

	function signature(data) {
		const small = decorativeKinds.map((kind) => `${kind}:${data.counts[kind] || 0}`).join('|');
		const emoji = data.emojiAwards.map((name) => name || 'fallback').join(',');
		const large = data.latestLarge ? `${data.latestLarge.kind}:${data.latestLarge.timestamp}:${data.latestLarge.order}` : 'none';
		return `${small}|emoji:${emoji}|large:${large}`;
	}

	const randomSigned = (min, max) => (Math.random() < .5 ? -1 : 1) * (min + Math.random() * (max - min));
	const randomPercent = (min = 2, max = 96) => `${min + Math.random() * (max - min)}%`;

	function ensureDecorativeLayer(owner) {
		let layer = Array.from(owner.children).find((el) => el.classList?.contains('toc-award-decorative-effects'));
		if (!layer) {
			layer = document.createElement('div');
			layer.className = 'toc-award-decorative-effects';
			layer.setAttribute('aria-hidden', 'true');
			owner.appendChild(layer);
		}
		owner.classList.add('award-free-effect-host');
		return layer;
	}

	function ensureLargeLayer(host) {
		let layer = Array.from(host.children).find((el) => el.classList?.contains('toc-award-large-effects'));
		if (!layer) {
			layer = document.createElement('div');
			layer.className = 'toc-award-large-effects';
			layer.setAttribute('aria-hidden', 'true');
			host.appendChild(layer);
		}
		host.classList.add('award-effect-content-host');
		return layer;
	}

	function roam(layer, elements, minSpeed, maxSpeed) {
		if (!elements.length) return;
		requestAnimationFrame(() => {
			if (!layer.isConnected) return;
			const sprites = elements.map((element) => ({
				element,
				x: Math.random() * Math.max(0, layer.clientWidth - (element.offsetWidth || 24)),
				y: Math.random() * Math.max(0, layer.clientHeight - (element.offsetHeight || 24)),
				vx: randomSigned(minSpeed, maxSpeed),
				vy: randomSigned(minSpeed, maxSpeed),
			}));
			let last = performance.now();
			const tick = (now) => {
				if (!layer.isConnected) return;
				const dt = Math.min(40, Math.max(0, now - last));
				last = now;
				for (const s of sprites) {
					if (!s.element.isConnected) continue;
					const w = s.element.offsetWidth || 24;
					const h = s.element.offsetHeight || 24;
					const maxX = Math.max(0, layer.clientWidth - w);
					const maxY = Math.max(0, layer.clientHeight - h);
					s.x += s.vx * dt;
					s.y += s.vy * dt;
					if (s.x <= 0 || s.x >= maxX) { s.x = Math.max(0, Math.min(maxX, s.x)); s.vx *= -1; }
					if (s.y <= 0 || s.y >= maxY) { s.y = Math.max(0, Math.min(maxY, s.y)); s.vy *= -1; }
					s.element.style.transform = `translate3d(${s.x}px,${s.y}px,0)`;
				}
				requestAnimationFrame(tick);
			};
			requestAnimationFrame(tick);
		});
	}

	function addFurry(layer, count) {
		if (!count) return;
		const roamers = [];
		for (let i = 0; i < Math.min(5, count + 2); i++) {
			const roamer = document.createElement('span');
			roamer.className = 'award-furry-roamer';
			const img = document.createElement('img');
			img.className = 'award-furry-dancer';
			img.alt = '';
			img.src = `${assetBase}furry${(i % 3) + 1}.webp?v=20260818h`;
			img.style.animationDelay = `${-Math.random() * 1.8}s`;
			img.addEventListener('error', () => { img.remove(); roamer.classList.add('award-furry-fallback'); roamer.textContent = '🐾'; }, {once: true});
			roamer.appendChild(img);
			layer.appendChild(roamer);
			roamers.push(roamer);
		}
		roam(layer, roamers, .02, .055);
	}

	function addRicardo(layer, count) {
		if (!count) return;
		const roamers = [];
		for (let i = 0; i < Math.min(3, count); i++) {
			const roamer = document.createElement('span');
			roamer.className = 'award-ricardo-roamer';
			const img = document.createElement('img');
			img.className = 'award-ricardo';
			img.alt = '';
			img.src = `/assets/images/ricardo${i + 1}.webp?v=20260818h`;
			img.style.animationDelay = `${-Math.random() * 1.8}s`;
			img.addEventListener('error', () => roamer.remove(), {once: true});
			roamer.appendChild(img);
			layer.appendChild(roamer);
			roamers.push(roamer);
		}
		roam(layer, roamers, .035, .085);
	}

	function animateFlyFrames(flies) {
		const states = flies.map((fly) => ({fly, frame: Math.floor(Math.random() * 20), next: 0, period: 55 + Math.random() * 35}));
		const draw = (s) => {
			const col = s.frame % 5;
			const row = Math.floor(s.frame / 5);
			s.fly.style.backgroundPosition = `${col * 25}% ${row * (100 / 3)}%`;
		};
		states.forEach(draw);
		const tick = (now) => {
			let alive = false;
			for (const s of states) {
				if (!s.fly.isConnected) continue;
				alive = true;
				if (now >= s.next) { s.frame = (s.frame + 1) % 20; s.next = now + s.period; draw(s); }
			}
			if (alive) requestAnimationFrame(tick);
		};
		requestAnimationFrame(tick);
	}

	function addShit(layer, count) {
		if (!count) return;
		const flies = [];
		for (let i = 0; i < Math.min(22, 8 + count * 2); i++) {
			const fly = document.createElement('span');
			fly.className = 'award-shit-fly';
			layer.appendChild(fly);
			flies.push(fly);
		}
		animateFlyFrames(flies);
		roam(layer, flies, .045, .12);
	}

	function addFireflies(layer, count) {
		if (!count) return;
		for (let i = 0; i < Math.min(28, 7 + count * 4); i++) {
			const dot = document.createElement('span');
			const dx = -55 + Math.random() * 110;
			const dy = -38 + Math.random() * 76;
			const duration = 2600 + Math.random() * 3600;
			dot.className = 'award-firefly';
			dot.style.left = randomPercent();
			dot.style.top = randomPercent(4, 92);
			layer.appendChild(dot);
			if (dot.animate) dot.animate([
				{transform:'translate3d(0,0,0) scale(.55)',opacity:.15},
				{transform:`translate3d(${dx*.38}px,${dy*.35}px,0) scale(1.18)`,opacity:1,offset:.42},
				{transform:`translate3d(${dx}px,${dy}px,0) scale(.78)`,opacity:.32},
			], {duration,delay:-Math.random()*duration,iterations:Infinity,direction:'alternate',easing:'ease-in-out'});
		}
	}

	function setEmojiVars(el) {
		const duration = 5200 + Math.random() * 5200;
		el.style.setProperty('--x', randomPercent(1,96));
		el.style.setProperty('--size', `${34 + Math.random()*20}px`);
		el.style.setProperty('--sway-a', `${randomSigned(12,48)}px`);
		el.style.setProperty('--sway-b', `${randomSigned(18,70)}px`);
		el.style.setProperty('--sway-c', `${randomSigned(12,58)}px`);
		el.style.setProperty('--rot-a', `${randomSigned(18,85)}deg`);
		el.style.setProperty('--rot-b', `${randomSigned(120,310)}deg`);
		el.style.setProperty('--duration', `${duration}ms`);
		el.style.setProperty('--delay', `${-Math.random()*duration}ms`);
	}

	function emojiFallback(original) {
		const fallback = document.createElement('span');
		fallback.className = 'award-emoji-rain award-emoji-fallback';
		fallback.textContent = '✨';
		for (const key of ['--x','--size','--sway-a','--sway-b','--sway-c','--rot-a','--rot-b','--duration','--delay']) {
			fallback.style.setProperty(key, original.style.getPropertyValue(key));
		}
		original.replaceWith(fallback);
	}

	function addEmoji(layer, names) {
		for (const name of names.slice(0,30)) {
			const el = name ? document.createElement('img') : document.createElement('span');
			el.className = 'award-emoji-rain';
			setEmojiVars(el);
			if (name) {
				el.alt = '';
				el.src = `/e/${encodeURIComponent(name)}.webp`;
				el.addEventListener('error', () => emojiFallback(el), {once:true});
			}
			else { el.classList.add('award-emoji-fallback'); el.textContent = '✨'; }
			layer.appendChild(el);
		}
	}

	function startFirework(item, index) {
		const img = item.querySelector('img');
		const fallback = () => {
			img.style.display = 'none';
			item.classList.add('award-firework-fallback');
			item.textContent = '✦';
			setTimeout(() => { item.textContent=''; item.classList.remove('award-firework-fallback'); img.style.display=''; }, 900);
		};
		img.addEventListener('error', fallback);
		const launch = () => {
			if (!item.isConnected) return;
			const endTop = 10 + Math.floor(Math.random()*45);
			item.style.left = randomPercent(8,88);
			item.style.top = '92%';
			item.style.opacity = '1';
			item.style.filter = `hue-rotate(${Math.floor(Math.random()*360)}deg)`;
			img.src = '/assets/images/firework-trail.webp?v=20260818h';
			const finish = () => {
				img.src = `/assets/images/firework-explosion.webp?v=20260818h-${Date.now()}`;
				setTimeout(() => { item.style.opacity='0'; setTimeout(launch,1600+Math.random()*2500); },900);
			};
			if (item.animate) {
				const flight = item.animate([{top:'92%'},{top:`${endTop}%`}],{duration:850,easing:'ease-out',fill:'forwards'});
				flight.onfinish = finish;
			} else { item.style.top=`${endTop}%`; setTimeout(finish,850); }
		};
		setTimeout(launch,index*650);
	}

	function addFireworks(layer, count) {
		for (let i=0; i<Math.min(4,count); i++) {
			const item=document.createElement('span');
			item.className='award-firework';
			const img=document.createElement('img');
			img.alt='';
			img.src='/assets/images/firework-trail.webp?v=20260818h';
			item.appendChild(img);
			layer.appendChild(item);
			startFirework(item,i);
		}
	}

	function addConfetti(layer, count) {
		for (let i=0; i<Math.min(110,28+count*12); i++) {
			const p=document.createElement('span');
			p.className='award-confetti-piece';
			p.style.setProperty('--x',randomPercent(0,99));
			p.style.setProperty('--size',`${5+Math.random()*7}px`);
			p.style.setProperty('--hue',`${Math.floor(Math.random()*360)}`);
			p.style.setProperty('--duration',`${3000+Math.random()*5500}ms`);
			p.style.setProperty('--delay',`${-Math.random()*7000}ms`);
			p.style.setProperty('--drift',`${randomSigned(15,85)}px`);
			p.style.setProperty('--spin',`${randomSigned(240,720)}deg`);
			layer.appendChild(p);
		}
	}

	function addLarge(layer, kind) {
		const wrap=document.createElement('div');
		wrap.className=`award-large-effect award-large-effect-${kind}`;
		const img=document.createElement('img');
		img.alt='';
		img.src = kind==='truthnova' ? `${assetBase}truthnova.gif?v=20260818h` :
			kind==='truthnuke' ? `${assetBase}truthnuke.webp?v=20260818h` : `${assetBase}lovebomb.webp?v=20260818h`;
		img.addEventListener('error',()=>wrap.remove(),{once:true});
		wrap.appendChild(img);
		layer.appendChild(wrap);
	}

	function render(owner) {
		if (!isThread() || !(owner instanceof HTMLElement)) return;
		const host=bodyHost(owner);
		if (!host) return;
		const data=dataFor(owner);
		const sig=signature(data);
		if (rendered.get(owner)===sig) return;
		rendered.set(owner,sig);

		const hasDecorative=decorativeKinds.some((kind)=>data.counts[kind]);
		let free=Array.from(owner.children).find((el)=>el.classList?.contains('toc-award-decorative-effects'));
		if (hasDecorative) {
			free=ensureDecorativeLayer(owner);
			free.replaceChildren();
			addConfetti(free,data.counts.confetti);
			addFireflies(free,data.counts.fireflies);
			addShit(free,data.counts.shit);
			addFurry(free,data.counts.furry);
			addRicardo(free,data.counts.ricardo);
			addEmoji(free,data.emojiAwards);
			addFireworks(free,data.counts.firework);
		} else { free?.remove(); owner.classList.remove('award-free-effect-host'); }

		let large=Array.from(host.children).find((el)=>el.classList?.contains('toc-award-large-effects'));
		if (data.latestLarge) {
			large=ensureLargeLayer(host);
			large.replaceChildren();
			addLarge(large,data.latestLarge.kind);
		} else { large?.remove(); host.classList.remove('award-effect-content-host'); }
	}

	function schedule(owner) {
		if (!owner) return;
		scheduled.add(owner);
		if (schedule.pending) return;
		schedule.pending=true;
		requestAnimationFrame(()=>{
			schedule.pending=false;
			const owners=Array.from(scheduled);
			scheduled.clear();
			owners.forEach(render);
		});
	}
	schedule.pending=false;

	function scan(root=document) {
		if (!isThread()) return;
		const owners=new Set();
		const icons=[];
		if (root instanceof HTMLElement && /(^|\s)award-kind-/.test(root.className||'')) icons.push(root);
		root.querySelectorAll?.('[class*="award-kind-"]').forEach((icon)=>icons.push(icon));
		for (const icon of icons) { const owner=ownerForIcon(icon); if (owner) owners.add(owner); }
		document.querySelectorAll('.award-free-effect-host,.award-effect-content-host').forEach((node)=>{
			const owner=node.classList.contains('comment-anchor') ? node : node.closest('.comment-anchor') || node.closest('#post-root > .card');
			if (owner) owners.add(owner);
		});
		owners.forEach(schedule);
	}

	// Pin/Giga Pin tooltips use durable award metadata rather than mutable tooltip text.
	function pinOwner(pin) { return pin.closest('.comment-anchor') || pin.closest('.actual-post') || pin.closest('.card'); }
	function tooltipText(el) {
		if (!el) return '';
		const direct=el.getAttribute('title')||el.getAttribute('data-bs-original-title')||el.getAttribute('aria-label');
		if (direct) return direct;
		const instance=window.bootstrap?.Tooltip?.getInstance(el);
		return typeof instance?._config?.title==='string' ? instance._config.title : '';
	}
	function decodeGiver(icon) {
		for (const cls of icon.classList||[]) {
			if (!cls.startsWith('award-user-b64-')) continue;
			const raw=cls.slice(15);
			try {
				const padded=raw+'='.repeat((4-raw.length%4)%4);
				const binary=atob(padded.replace(/-/g,'+').replace(/_/g,'/'));
				return new TextDecoder().decode(Uint8Array.from(binary,(c)=>c.charCodeAt(0)));
			} catch (_) {}
		}
		const match=tooltipText(icon).match(/given by\s+@([^\s]+)/i);
		return match ? match[1].replace(/[.,;:!?]+$/,'') : null;
	}
	function latestPinAward(owner) {
		if (!owner) return null;
		let latest=null, order=0;
		for (const icon of owner.querySelectorAll('.award-kind-pin,.award-kind-gigapin')) {
			const giver=decodeGiver(icon);
			if (!giver) continue;
			const candidate={kind:icon.classList.contains('award-kind-gigapin')?'gigapin':'pin',giver,timestamp:timestampForIcon(icon),order:order++};
			if (!latest || candidate.timestamp>latest.timestamp || (candidate.timestamp===latest.timestamp && candidate.order>=latest.order)) latest=candidate;
		}
		return latest;
	}
	function fixPin(pin) {
		if (!(pin instanceof HTMLElement)) return;
		pin.removeAttribute('data-onmouseover');
		pin.onmouseover=null;
		const source=latestPinAward(pinOwner(pin));
		const existing=tooltipText(pin).replace(/\s+until\s+.*$/i,'').trim();
		let base=source ? `Pinned by @${source.giver} (${source.kind==='gigapin'?'Giga pin award':'Pin award'})` :
			(/^Pinned by\s+/i.test(existing)?existing:'Pinned by (a site admin)');
		const ts=Number.parseInt(pin.dataset.timestamp||'',10);
		if (Number.isFinite(ts)) {
			const date=new Date(ts*1000);
			base += ` until ${typeof window.formatDate==='function'?window.formatDate(date):date.toLocaleString()}`;
		}
		pin.setAttribute('title',base);
		pin.setAttribute('data-bs-original-title',base);
		const tip=window.bootstrap?.Tooltip?.getInstance(pin);
		if (tip) { if (tip._config) tip._config.title=base; tip.setContent?.({'.tooltip-inner':base}); }
	}
	function preparePins(root=document) {
		if (root instanceof HTMLElement && root.matches?.('[id^="pinned-"]')) fixPin(root);
		root.querySelectorAll?.('[id^="pinned-"]').forEach(fixPin);
	}
	window.pinned_timestamp=(id)=>{ const pin=document.getElementById(id); if (pin) fixPin(pin); };

	// Add Clear Awards beside the existing admin Remove action. The backend still
	// enforces POST_COMMENT_MODERATION; this UI is only injected where the mod button exists.
	function clearTarget(button) {
		const match=button.id.match(/^remove(2)?-(\d+)$/);
		if (!match) return null;
		const id=Number.parseInt(match[2],10);
		const comment=button.closest('.comment-anchor')||button.closest('.comment');
		return {type:comment?'comment':'post',id,mobile:Boolean(match[1])||button.classList.contains('list-group-item')};
	}
	function clearButton(reference,target) {
		const button=document.createElement('button');
		button.type='button';
		button.id=`clear-awards${target.mobile?'2':''}-${target.type}-${target.id}`;
		button.className=target.mobile?'list-group-item text-danger toc-clear-awards':'dropdown-item list-inline-item text-danger toc-clear-awards';
		button.innerHTML=`<i class="fas fa-eraser text-danger${target.mobile?' mr-2':' fa-fw'}"></i>Clear Awards`;
		if (target.mobile) button.setAttribute('data-bs-dismiss','modal');
		button.addEventListener('click',()=>{
			if (!confirm(`Clear every award from this ${target.type}? This removes all award icons and visual award effects.`)) return;
			const url=`/admin/clear-awards/${target.type}/${target.id}`;
			if (typeof window.postToast==='function') window.postToast(button,url,{},()=>location.reload());
			else {
				const form=new FormData();
				if (typeof window.formkey==='function') form.append('formkey',window.formkey());
				fetch(url,{method:'POST',headers:{xhr:'xhr'},body:form,credentials:'same-origin'}).then((r)=>{if(!r.ok)throw Error();location.reload();});
			}
		});
		return button;
	}
	function injectClear(root=document) {
		const refs=[];
		if (root instanceof HTMLElement && root.matches?.('button[id^="remove-"],button[id^="remove2-"]')) refs.push(root);
		root.querySelectorAll?.('button[id^="remove-"],button[id^="remove2-"]').forEach((el)=>refs.push(el));
		for (const ref of refs) {
			if (ref.dataset.tocClearAwards==='1') continue;
			const target=clearTarget(ref);
			if (!target) continue;
			ref.dataset.tocClearAwards='1';
			const id=`clear-awards${target.mobile?'2':''}-${target.type}-${target.id}`;
			if (!document.getElementById(id)) ref.after(clearButton(ref,target));
		}
	}

	function init() {
		preparePins(document);
		injectClear(document);
		scan(document);
		document.addEventListener('mouseover',(event)=>{const pin=event.target.closest?.('[id^="pinned-"]');if(pin)fixPin(pin);},true);
		let pending=false;
		new MutationObserver((mutations)=>{
			let rescan=false;
			for (const mutation of mutations) {
				for (const node of mutation.addedNodes) {
					if (!(node instanceof HTMLElement)) continue;
					if (node.closest?.('.toc-award-decorative-effects,.toc-award-large-effects')) continue;
					preparePins(node);
					injectClear(node);
					if (/(^|\s)award-kind-/.test(node.className||'') || node.querySelector?.('[class*="award-kind-"]')) rescan=true;
				}
				if (mutation.removedNodes.length) rescan=true;
			}
			if (rescan&&!pending) { pending=true; requestAnimationFrame(()=>{pending=false;scan(document);}); }
		}).observe(document.body,{childList:true,subtree:true});
	}

	if (document.readyState==='loading') document.addEventListener('DOMContentLoaded',init,{once:true});
	else init();
})();