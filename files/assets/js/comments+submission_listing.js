function pinned_timestamp(id) {
	const el = document.getElementById(id)
	if (!el) return
	const pintooltip = el.getAttribute("data-bs-original-title") || el.getAttribute("title") || "Pinned"
	if (!pintooltip.includes('until')) {
		const time = formatDate(new Date(parseInt(el.dataset.timestamp) * 1000))
		const title = `${pintooltip} until ${time}`
		el.setAttribute("data-bs-original-title", title)
		el.setAttribute("title", title)
		const tooltip = bootstrap.Tooltip.getInstance(el)
		if (tooltip && tooltip.setContent) tooltip.setContent({'.tooltip-inner': title})
	}
}

// Bootstrap escapes tooltip HTML by default. Ban-hat tooltip content is generated
// server-side from escaped text, so restore only the marked username links after
// the tooltip is shown. This preserves ordinary tooltip sanitisation everywhere else.
document.addEventListener('shown.bs.tooltip', (event) => {
	const trigger = event.target;
	const rawTitle = trigger.getAttribute('data-bs-original-title') || trigger.getAttribute('title') || '';
	if (!rawTitle.includes('ban-tooltip-user')) return;

	const tooltipId = trigger.getAttribute('aria-describedby');
	const tooltip = tooltipId ? document.getElementById(tooltipId) : null;
	const inner = tooltip ? tooltip.querySelector('.tooltip-inner') : null;
	if (!inner) return;

	inner.innerHTML = rawTitle;
	const instance = bootstrap.Tooltip.getInstance(trigger);
	if (instance && instance.update) instance.update();
});

const popClickBadgeTemplateDOM = document.createElement("IMG");
popClickBadgeTemplateDOM.classList.add("pop-badge");
popClickBadgeTemplateDOM.loading = "lazy";
popClickBadgeTemplateDOM.alt = "badge";

document.addEventListener('shown.bs.popover', (e) => {
	let popover = document.getElementsByClassName("popover")
	popover = popover[popover.length-1]

	const author = JSON.parse(e.target.dataset.popInfo);

	if (popover.getElementsByClassName('pop-username')[0].innerHTML == author["username"])
		return

	if (popover.getElementsByClassName('pop-badges')) {
		const badgesDOM = popover.getElementsByClassName('pop-badges')[0];
		badgesDOM.innerHTML = "";
		for (const badge of author["badges"]) {
			const badgeDOM = popClickBadgeTemplateDOM.cloneNode();
			badgeDOM.src = badge + "?b=6";

			badgesDOM.append(badgeDOM);
		}
	}

	popover.getElementsByClassName('pop-banner')[0].src = author["bannerurl"]
	popover.getElementsByClassName('pop-picture')[0].src = author["profile_url"]

	const popHat = popover.getElementsByClassName('pop-hat')[0];
	if (author["hat"]) {
		const separator = author["hat"].includes('?') ? '&' : '?';
		popHat.src = author["hat"] + separator + "h=8";
		popHat.classList.remove('d-none');
		const isBanHat = author["hat"].includes('/ban-hats/');
		popHat.classList.toggle('pop-hat-ban', isBanHat);
		if (isBanHat) {
			popHat.style.width = '64px';
			popHat.style.left = '5.5px';
			popHat.style.bottom = '0';
			popHat.style.height = 'auto';
			popHat.style.objectFit = 'contain';
		} else {
			popHat.style.removeProperty('width');
			popHat.style.removeProperty('left');
			popHat.style.removeProperty('bottom');
			popHat.style.removeProperty('height');
			popHat.style.removeProperty('object-fit');
		}
	} else {
		popHat.removeAttribute('src');
		popHat.classList.add('d-none');
		popHat.classList.remove('pop-hat-ban');
		popHat.removeAttribute('style');
	}

	popover.getElementsByClassName('pop-username')[0].innerHTML = author["username"]
	if (popover.getElementsByClassName('pop-bio').length > 0) {
		popover.getElementsByClassName('pop-bio')[0].innerHTML = author["bio_html"]
	}
	const number = (value) => typeof formatNumber === 'function' ? formatNumber(value) : Number(value).toLocaleString('en-US')
	popover.getElementsByClassName('pop-user-id')[0].textContent = number(author["id"])
	popover.getElementsByClassName('pop-truescore')[0].textContent = number(author["truescore"])
	popover.getElementsByClassName('pop-postcount')[0].textContent = number(author["post_count"])
	popover.getElementsByClassName('pop-commentcount')[0].textContent = number(author["comment_count"])
	popover.getElementsByClassName('pop-coins')[0].textContent = number(author["coins"])
	popover.getElementsByClassName('pop-bux')[0].textContent = number(author["bux"])
	popover.getElementsByClassName('pop-post-link')[0].href = author["url"] + '/posts'
	popover.getElementsByClassName('pop-comment-link')[0].href = author["url"] + '/comments'
	popover.getElementsByClassName('pop-view_more')[0].href = author["url"]
	popover.getElementsByClassName('pop-created-date')[0].innerHTML = author["created_date"]
})

function post(url) {
	const xhr = createXhrWithFormKey(url);
	xhr[0].send(xhr[1]);
};

function poll_vote_0(oid, parentid, kind) {
	for(let el of document.getElementsByClassName('presult-'+parentid)) {
		el.classList.remove('d-none');
	}
	const full_oid = kind + '-' + oid
	const type = document.getElementById(full_oid).checked;
	const scoretext = document.getElementById('score-' + full_oid);
	const score = Number(scoretext.textContent);
	if (type == true) scoretext.textContent = score + 1;
	else scoretext.textContent = score - 1;
	post(`/vote/${kind}/option/${oid}`);
}

function poll_vote_1(oid, parentid, kind) {
	for(let el of document.getElementsByClassName('presult-'+parentid)) {
		el.classList.remove('d-none');
	}
	const full_oid = kind + '-' + oid
	let curr = document.getElementById(`current-${kind}-${parentid}`)
	if (curr && curr.value)
	{
		const scoretext = document.getElementById('score-' + curr.value);
		const score = Number(scoretext.textContent);
		scoretext.textContent = score - 1;
	}

	const scoretext = document.getElementById('score-' + full_oid);

	const score = Number(scoretext.textContent);
	scoretext.textContent = score + 1;
	post(`/vote/${kind}/option/${oid}`);
	curr.value = full_oid
}

function bet_vote(t, oid) {
	postToast(t, `/vote/post/option/${oid}`,
		{
		},
		() => {
			for(let el of document.getElementsByClassName('bet')) {
				el.disabled = true;
			}
			for(let el of document.getElementsByClassName('cost')) {
				el.classList.add('d-none')
			}
			const scoretext = document.getElementById('option-' + oid);
			const score = Number(scoretext.textContent);
			scoretext.textContent = score + 1;

			document.getElementById("user-coins-amount").innerText = parseInt(document.getElementById("user-coins-amount").innerText) - 200;
		}
	);
}
