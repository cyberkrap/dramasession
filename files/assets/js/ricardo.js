const isleft = true
setInterval(() => {
	let ricardo1 = document.getElementById("ricardo1")
	const height = Math.floor(Math.random()*60)+10
	if (ricardo1) {
		ricardo1.firstElementChild.src = ""

		if (isleft == true) {
			ricardo1.className = "ricardo ricardoright"
			isleft = false
		} else {
			ricardo1.className = "ricardo ricardoleft"
			isleft = true
		}

		ricardo1.firstElementChild.src = "/i/ricardo1.webp"
		ricardo1.style.top=height+"%"
	}
}, 5800)

setInterval(() => {
	let ricardo2 = document.getElementById("ricardo2")
	const xpos = Math.floor(Math.random()*9)*10

	if (ricardo2) ricardo2.style.left=xpos+"%"
}, 1700)
