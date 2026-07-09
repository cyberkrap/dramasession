if (!window.matchMedia('(display-mode: minimal-ui)')['matches']) {
	if (window.innerWidth <= 737) {
		const tt = bootstrap.Tooltip.getOrCreateInstance(document.getElementById('mobile-prompt'))
		tt.show()
		document.getElementsByClassName('tooltip')[0].addEventListener('click', function(e) {
			tt.hide()
			const xhr = new XMLHttpRequest();
			xhr.withCredentials=true;
			xhr.open("POST", '/dismiss_mobile_tip', true);
			xhr.setRequestHeader('xhr', 'xhr');
			xhr.send();
			if (!e.target.classList.contains('dismiss-beg'))
				location.href = "/app"
		})
	}
}
