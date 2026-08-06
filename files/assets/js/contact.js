document.addEventListener('paste', function(event) {
	const files = Array.from(event.clipboardData?.files || []);
	if (!files.length) return;

	if (files.length > 4) {
		alert("You can't upload more than 4 files at one time!");
		return;
	}

	const focused = document.activeElement;
	if (!(focused instanceof HTMLTextAreaElement)) return;

	let inputId = null;
	let filenameId = null;
	if (focused.id === 'input-message') {
		inputId = 'file-upload';
		filenameId = 'filename';
	} else if (focused.id === 'restricted-contact-message') {
		inputId = 'restricted-file-upload';
		filenameId = 'restricted-filename';
	} else {
		// Thread replies use the inline image uploader and insert URLs at the
		// cursor, so the new-conversation attachment field must not steal them.
		return;
	}

	const input = document.getElementById(inputId);
	const filename = document.getElementById(filenameId);
	if (!input || !filename || input.disabled) return;

	const transfer = new DataTransfer();
	for (const file of files) transfer.items.add(file);
	input.files = transfer.files;
	filename.textContent = files.map((file) => file.name.toLowerCase()).join(', ');
});
