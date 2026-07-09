function banModal(link, name, fullname, cls) {
	document.getElementById("banModalTitle").innerHTML = `Ban @${name}`;
	document.getElementById("ban-modal-link").value = link;
	document.getElementById("banUserButton").innerHTML = `Ban @${name}`;

	document.getElementById("banUserButton").addEventListener('click', function() {
		let form = new FormData(document.getElementById("banModalForm"));
		const xhr = createXhrWithFormKey(`/ban_user/${fullname}?form`, "POST", form);
		xhr[0].onload = function() {
			let data
			try {data = JSON.parse(xhr[0].response)}
			catch(e) {console.log(e)}
			success = xhr[0].status >= 200 && xhr[0].status < 300;
			showToast(success, getMessageFromJsonData(success, data));
			document.getElementById(`unban-${fullname}`).classList.toggle(cls);
			document.getElementById(`ban-${fullname}`).classList.toggle(cls);
			document.getElementById(`unban2-${fullname}`).classList.toggle(cls);
			document.getElementById(`ban2-${fullname}`).classList.toggle(cls);
		};

		xhr[0].send(xhr[1]);
	})
}

function chudModal(link, name, fullname, cls) {
	document.getElementById("chudModalTitle").innerHTML = `Chud @${name}`;
	document.getElementById("chud-modal-link").value = link;
	document.getElementById("chudUserButton").innerHTML = `Chud @${name}`;

	document.getElementById("chudUserButton").addEventListener('click', function() {
		let form = new FormData(document.getElementById("chudModalForm"));
		const xhr = createXhrWithFormKey(`/agendaposter/${fullname}?form`, "POST", form);
		xhr[0].onload = function() {
			let data
			try {data = JSON.parse(xhr[0].response)}
			catch(e) {console.log(e)}
			success = xhr[0].status >= 200 && xhr[0].status < 300;
			showToast(success, getMessageFromJsonData(success, data));
			document.getElementById(`unchud-${fullname}`).classList.toggle(cls);
			document.getElementById(`chud-${fullname}`).classList.toggle(cls);
			document.getElementById(`unchud2-${fullname}`).classList.toggle(cls);
			document.getElementById(`chud2-${fullname}`).classList.toggle(cls);
		};

		xhr[0].send(xhr[1]);
	})
}
