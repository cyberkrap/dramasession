function parseAltResponse(xhr) {
	try {
		return JSON.parse(xhr.response);
	}
	catch (e) {
		console.log(e);
		return null;
	}
}

function setAltDeletedState(element, username, otherId, shouldDelink) {
	element.disabled = true;
	element.classList.add('disabled');

	const method = shouldDelink ? 'PUT' : 'DELETE';
	const xhr = createXhrWithFormKey(`/@${username}/alts/${otherId}/deleted`, method, new FormData());
	xhr[0].onload = function() {
		const data = parseAltResponse(xhr[0]);
		if (xhr[0].status >= 200 && xhr[0].status < 300) {
			showToast(true, getMessageFromJsonData(true, data));
			location.reload();
			return;
		}

		showToast(false, getMessageFromJsonData(false, data));
		element.disabled = false;
		element.classList.remove('disabled');
	};
	xhr[0].send(xhr[1]);
}

function submitAddAlt(element, username) {
	const isLinking = element.id == 'add-alt-form-link';
	const otherElement = isLinking ? document.getElementById('add-alt-form-delink') : document.getElementById('add-alt-form-link');
	if (!otherElement) return;
	element.disabled = true;
	otherElement.disabled = true;
	element.classList.add('disabled');
	otherElement.classList.add('disabled');
	const form = new FormData();
	if (!isLinking) form.append('deleted', 'true');
	form.append('other_username', document.getElementById('link-input-other').value);
	const xhr = createXhrWithFormKey(`/@${username}/alts/`, 'POST', form);
	xhr[0].onload = function() {
		const data = parseAltResponse(xhr[0]);
		if (xhr[0].status >= 200 && xhr[0].status < 300) {
			showToast(true, getMessageFromJsonData(true, data));
			location.reload();
		} else {
			showToast(false, getMessageFromJsonData(false, data));
			element.disabled = false;
			otherElement.disabled = false;
			element.classList.remove('disabled');
			otherElement.classList.remove('disabled');
		}
	};
	xhr[0].send(xhr[1]);
}
