function pinned_timestamp(id) {
	const el = document.getElementById(id)
	const pintooltip = el.getAttribute("data-bs-original-title")
	if (!pintooltip.includes('until'))
		{
			const time = formatDate(new Date(parseInt(el.dataset.timestamp)*1000))
			el.setAttribute("data-bs-original-title", `${pintooltip} until ${time}`)
		}
}

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
	if (author["hat"]) popover.getElementsByClassName('pop-hat')[0].src = author['hat'] + "?h=7"
	popover.getElementsByClassName('pop-username')[0].innerHTML = author["username"]
	if (popover.getElementsByClassName('pop-bio').length > 0) {
		popover.getElementsByClassName('pop-bio')[0].innerHTML = author["bio_html"]
	}
	popover.getElementsByClassName('pop-postcount')[0].innerHTML = author["post_count"]
	popover.getElementsByClassName('pop-commentcount')[0].innerHTML = author["comment_count"]
	popover.getElementsByClassName('pop-coins')[0].innerHTML = author["coins"]
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
