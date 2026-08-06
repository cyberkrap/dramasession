document.onpaste = function(event) {
	const files = structuredClone(event.clipboardData.files);

	if (files.length > 4)
	{
		alert("You can't upload more than 4 files at one time!")
		return
	}

	if (!files.length) return

	const f = document.getElementById('file-upload');
	let filename = ''
	for (const file of files)
		filename += file.name + ', '
	filename = filename.toLowerCase().slice(0, -2)
	f.files = files;
	document.getElementById('filename').textContent = filename;
}
