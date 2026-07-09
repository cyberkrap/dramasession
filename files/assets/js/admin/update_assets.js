const IMAGE_FORMATS = document.getElementById('IMAGE_FORMATS').value.split(',')

document.onpaste = function(event) {
	files = structuredClone(event.clipboardData.files);

	filename = files[0]

	if (filename)
	{
		filename = filename.name.toLowerCase()
		f=document.getElementById('file-upload');
		f.files = files;
		document.getElementById('filename-show').textContent = filename;
		if (IMAGE_FORMATS.some(s => filename.endsWith(s)))
		{
			const fileReader = new FileReader();
			fileReader.readAsDataURL(f.files[0]);
			fileReader.addEventListener("load", function () {
				document.getElementById('image-preview').setAttribute('src', this.result);
				document.getElementById('image-preview').classList.remove('d-none');
			});
		}
	}
}

document.getElementById('file-upload').addEventListener('change', function(){
	f=document.getElementById('file-upload');
	document.getElementById('filename-show').textContent = document.getElementById('file-upload').files[0].name.substr(0, 20);
	filename = f.files[0].name.toLowerCase()
	if (IMAGE_FORMATS.some(s => filename.endsWith(s)))
	{
		const fileReader = new FileReader();
		fileReader.readAsDataURL(f.files[0]);
		fileReader.addEventListener("load", function () {
			document.getElementById('image-preview').setAttribute('src', this.result);
			document.getElementById('image-preview').classList.remove('d-none');
		});
		document.getElementById('submit-asset').disabled = false;
	}
})
