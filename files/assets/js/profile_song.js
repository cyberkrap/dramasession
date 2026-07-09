let u_username = document.getElementById('u_username')

if (u_username)
{
	u_username = u_username.innerHTML

	let audio = new Audio(`/@${u_username}/song`);
	audio.loop=true;

	function toggle() {
		if (audio.paused) {
			audio.play();
			audio.play();
		}
		else {
			audio.pause();
			audio.pause();
		}
	}

	audio.play();
	document.addEventListener('click', () => {
		if (audio.paused) audio.play();
	}, {once : true});

	prepare_to_pause(audio)
}
else
{
	let v_username = document.getElementById('v_username')
	if (v_username)
	{
		v_username = v_username.innerHTML

		const paused = localStorage.getItem("paused")

		let audio = new Audio(`/@${v_username}/song`);
		audio.loop=true;

		function toggle() {
			if (audio.paused)
			{
				audio.play()
				localStorage.setItem("paused", "")
			}
			else
			{
				audio.pause()
				localStorage.setItem("paused", "1")
			}
		}

		if (!paused)
		{
			audio.play();
			document.addEventListener('click', () => {
				if (audio.paused) audio.play();
			}, {once : true});
		}

		prepare_to_pause(audio)
	}
}
