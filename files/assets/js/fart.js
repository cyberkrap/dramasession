fart = Math.floor(Math.random() * 5) + 1
let audio = new Audio(`/assets/images/${fart}.webp`);

audio.play();
if (audio.paused) {
	document.addEventListener('click', () => {
		if (audio.paused) audio.play();
	}, {once : true})
}
