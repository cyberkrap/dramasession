// TODO: Refactor this ugly shit who wrote this lmao
function vote(type, id, dir) {
	const upvotes = document.getElementsByClassName(type + '-' + id + '-up');
	const downvotes = document.getElementsByClassName(type + '-' + id + '-down');
	const scoretexts = document.getElementsByClassName(type + '-score-' + id);

	for (let i=0; i<upvotes.length; i++) {

		const upvote = upvotes[i]
		const downvote = downvotes[i]
		const scoretext = scoretexts[i]
		const score = Number(scoretext.textContent);

		if (dir == "1") {
			if (upvote.classList.contains('active')) {
				upvote.classList.remove('active')
				upvote.classList.remove('active-anim')
				scoretext.textContent = score - 1
				votedirection = "0"
			} else if (downvote.classList.contains('active')) {
				upvote.classList.add('active')
				upvote.classList.add('active-anim')
				downvote.classList.remove('active')
				downvote.classList.remove('active-anim')
				scoretext.textContent = score + 2
				votedirection = "1"
			} else {
				upvote.classList.add('active')
				upvote.classList.add('active-anim')
				scoretext.textContent = score + 1
				votedirection = "1"
			}

			if (upvote.classList.contains('active')) {
				scoretext.classList.add('score-up')
				scoretext.classList.add('score-up-anim')
				scoretext.classList.remove('score-down')
				scoretext.classList.remove('score')
			} else if (downvote.classList.contains('active')) {
				scoretext.classList.add('score-down')
				scoretext.classList.remove('score-up')
				scoretext.classList.remove('score-up-anim');
				scoretext.classList.remove('score')
			} else {
				scoretext.classList.add('score')
				scoretext.classList.remove('score-up')
				scoretext.classList.remove('score-up-anim');
				scoretext.classList.remove('score-down')
			}
		}
		else {
			if (downvote.classList.contains('active')) {
				downvote.classList.remove('active')
				downvote.classList.remove('active-anim')
				scoretext.textContent = score + 1
				votedirection = "0"
			} else if (upvote.classList.contains('active')) {
				downvote.classList.add('active')
				downvote.classList.add('active-anim')
				upvote.classList.remove('active')
				upvote.classList.remove('active-anim')
				scoretext.textContent = score - 2
				votedirection = "-1"
			} else {
				downvote.classList.add('active')
				downvote.classList.add('active-anim')
				scoretext.textContent = score - 1
				votedirection = "-1"
			}

			if (upvote.classList.contains('active')) {
				scoretext.classList.add('score-up')
				scoretext.classList.add('score-up-anim')
				scoretext.classList.remove('score-down')
				scoretext.classList.remove('score')
			} else if (downvote.classList.contains('active')) {
				scoretext.classList.add('score-down')
				scoretext.classList.remove('score-up-anim')
				scoretext.classList.remove('score-up')
				scoretext.classList.remove('score')
			} else {
				scoretext.classList.add('score')
				scoretext.classList.remove('score-up')
				scoretext.classList.remove('score-down')
				scoretext.classList.remove('score-up-anim')
			}
		}
	}

	const xhr = createXhrWithFormKey("/vote/" + type.replace('-mobile','') + "/" + id + "/" + votedirection);
	xhr[0].send(xhr[1]);
}

function pick(kind, price, coins, marseybux) {
	price = parseInt(price)
	coins = parseInt(coins)
	marseybux = parseInt(marseybux)

	const buy1 = document.getElementById('buy1')
	if (marseybux >= price && kind != "grass")
		buy1.disabled=false;
	else
		buy1.disabled=true;

	const buy2 = document.getElementById('buy2')
	if (coins >= price && kind != "benefactor")
		buy2.disabled=false;
	else
		buy2.disabled=true;

	let ownednum = Number(document.getElementById(`${kind}-owned`).textContent);
	document.getElementById('giveaward').disabled = (ownednum == 0);
	document.getElementById('kind').value=kind;
	if (document.getElementsByClassName('picked').length > 0) {
		document.getElementsByClassName('picked')[0].classList.toggle('picked');
	}
	document.getElementById(kind).classList.toggle('picked')
	if (kind == "flairlock") {
		document.getElementById('notelabel').innerHTML = "New flair:";
		document.getElementById('note').placeholder = "Insert new flair here, or leave empty to add 1 day to the duration of the current flair. 100 characters max.";
		document.getElementById('note').maxLength = 100;
	}
	else {
		document.getElementById('notelabel').innerHTML = "Note (optional):";
		document.getElementById('note').placeholder = "Note to include in award notification";
		document.getElementById('note').maxLength = 200;
	}
}

function buy(mb) {
	const kind = document.getElementById('kind').value;
	url = `/buy/${kind}`
	if (mb) url += "?mb=true"
	const xhr = createXhrWithFormKey(url);
	xhr[0].onload = function() {
		let data
		try {data = JSON.parse(xhr[0].response)}
		catch(e) {console.log(e)}
		success = xhr[0].status >= 200 && xhr[0].status < 300;
		showToast(success, getMessageFromJsonData(success, data), true);
		if (success) {
			if (kind != "lootbox")
			{
				document.getElementById('giveaward').disabled=false;
				let owned = document.getElementById(`${kind}-owned`)
				let ownednum = Number(owned.textContent) + 1;
				owned.textContent = ownednum
			}
		}
	};

	xhr[0].send(xhr[1]);

}

function giveaward(t) {
	const kind = document.getElementById('kind').value;
	postToast(t, t.dataset.action,
		{
		"kind": kind,
		"note": document.getElementById('note').value
		},
		() => {
			let owned = document.getElementById(`${kind}-owned`)
			let ownednum = Number(owned.textContent) - 1;
			owned.textContent = ownednum
			if (ownednum == 0)
				document.getElementById('giveaward').disabled=true;
		}
	);
}

const data_url = document.querySelectorAll('[data-url]');
for (const element of data_url) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.addEventListener('click', () => {
		document.getElementById('giveaward').dataset.action = element.dataset.url
	});
}
