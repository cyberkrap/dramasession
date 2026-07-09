function postToastRoastEventDarkmode(t, url) {
	const xhr = createXhrWithFormKey(url);
	xhr[0].onload = function() {
		postToastLoadEventDarkmode(xhr[0])
	};
	xhr[0].send(xhr[1]);
}

function postToastLoadEventDarkmode(xhr) {
	let data
	try {
		data = JSON.parse(xhr.response)
	}
	catch (e) {
		console.log(e)
	}
	success = xhr.status >= 200 && xhr.status < 300;
	showToast(success, getMessageFromJsonData(success, data));
	location.reload();
}
