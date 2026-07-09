const fireworks = document.getElementsByClassName("firework")
let counter = 0

for (let firework of fireworks){
const timeout = 2000 * counter
counter++
setTimeout(() => {
	setInterval(() => {
	firework.firstElementChild.src = "/i/firework-trail.webp"

	const xpos = Math.floor(Math.random() * 80) + 5
	let ypos = 95
	firework.style.top=ypos+"%"
	firework.style.left=xpos+"%"

	firework.style.display="inline-block"
	const hue = Math.floor(Math.random()*360)+1
	firework.style.filter="hue-rotate("+hue+"deg)"

	let id = null
	const height = Math.floor(Math.random()*60)+15
	clearInterval(id);
	id = setInterval(frame, 20);

	const vnum = Math.floor(Math.random()*1000)

	function frame() {
		if (ypos <= height) {
		clearInterval(id);
		firework.firstElementChild.src = "/i/firework-explosion.webp?v="+vnum
		} else {
		ypos--;
		firework.style.top=ypos+"%"
		}
	}
	}, 5000)
}, timeout)
}
