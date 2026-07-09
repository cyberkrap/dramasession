const IMAGE_FORMATS = document.getElementById('IMAGE_FORMATS').value.split(',')

document.getElementById('post-title').value = localStorage.getItem("post-title")
document.getElementById('post-text').value = localStorage.getItem("post-text")
document.getElementById('post-url').value = localStorage.getItem("post-url")

document.getElementById('post-notify').checked = localStorage.getItem("post-notify") == 'true'
document.getElementById('post-new').checked = localStorage.getItem("post-new") == 'true'
document.getElementById('post-nsfw').checked = localStorage.getItem("post-nsfw") == 'true'
document.getElementById('post-private').checked = localStorage.getItem("post-private") == 'true'
document.getElementById('post-ghost').checked = localStorage.getItem("post-ghost") == 'true'

markdown(document.getElementById("post-text"));

function checkForRequired() {
	const title = document.getElementById("post-title");
	const url = document.getElementById("post-url");
	const text = document.getElementById("post-text");
	const button = document.getElementById("create_button");
	const image = document.getElementById("file-upload");
	const image2 = document.getElementById("file-upload-submit");

	if (url.value.length > 0 || image.files.length > 0 || image2.files.length > 0) {
		text.required = false;
		url.required=false;
	} else if (text.value.length > 0 || image.files.length > 0 || image2.files.length > 0) {
		url.required = false;
	} else {
		text.required = true;
		url.required = true;
	}

	const isValidTitle = title.checkValidity();
	const isValidURL = url.checkValidity();
	const isValidText = text.checkValidity();

	if (isValidTitle && (isValidURL || image.files.length > 0 || image2.files.length > 0)) {
		button.disabled = false;
	} else if (isValidTitle && isValidText) {
		button.disabled = false;
	} else {
		button.disabled = true;
	}
}
checkForRequired();

function hide_image() {
	x=document.getElementById('image-upload-block');
	url=document.getElementById('post-url').value;
	if (url.length>=1){
		x.classList.add('d-none');
	}
	else {
		x.classList.remove('d-none');
	}
}

document.onpaste = function(event) {
	files = structuredClone(event.clipboardData.files);

	if (files.length > 4)
	{
		alert("You can't upload more than 4 files at one time!")
		return
	}

	filename = files[0]

	if (filename)
	{
		filename = filename.name.toLowerCase()
		if (document.activeElement.id == 'post-text') {
			let filename = ''
			for (const file of files)
				filename += file.name + ', '
			filename = filename.toLowerCase().slice(0, -2)
			document.getElementById('file-upload-submit').value = files;
			document.getElementById('filename-show-submit').textContent = filename;
		}
		else {
			f=document.getElementById('file-upload');
			f.files = files;
			document.getElementById('filename-show').textContent = filename;
			document.getElementById('urlblock').classList.add('d-none');
			if (IMAGE_FORMATS.some(s => filename.endsWith(s)))
			{
				const fileReader = new FileReader();
				fileReader.readAsDataURL(f.files[0]);
				fileReader.addEventListener("load", function () {document.getElementById('image-preview').setAttribute('src', this.result);});
			}
			document.getElementById('post-url').value = null;
			localStorage.setItem("post-url", "")
			document.getElementById('image-upload-block').classList.remove('d-none')
		}
		checkForRequired();
	}
}

document.getElementById('file-upload').addEventListener('change', function(){
	f=document.getElementById('file-upload');
	document.getElementById('urlblock').classList.add('d-none');
	document.getElementById('filename-show').textContent = document.getElementById('file-upload').files[0].name.substr(0, 20);
	filename = f.files[0].name.toLowerCase()
	if (IMAGE_FORMATS.some(s => filename.endsWith(s)))
	{
		const fileReader = new FileReader();
		fileReader.readAsDataURL(f.files[0]);
		fileReader.addEventListener("load", function () {document.getElementById('image-preview').setAttribute('src', this.result);});
	}
	checkForRequired();
})

function savetext() {
	localStorage.setItem("post-title", document.getElementById('post-title').value)
	localStorage.setItem("post-text", document.getElementById('post-text').value)
	localStorage.setItem("post-url", document.getElementById('post-url').value)

	let sub = document.getElementById('sub')
	if (sub) localStorage.setItem("sub", sub.value)

	localStorage.setItem("post-notify", document.getElementById('post-notify').checked)
	localStorage.setItem("post-new", document.getElementById('post-new').checked)
	localStorage.setItem("post-nsfw", document.getElementById('post-nsfw').checked)
	localStorage.setItem("post-private", document.getElementById('post-private').checked)
	localStorage.setItem("post-ghost", document.getElementById('post-ghost').checked)
}


function autoSuggestTitle()	{

	const urlField = document.getElementById("post-url");

	const titleField = document.getElementById("post-title");

	const isValidURL = urlField.checkValidity();

	if (isValidURL && urlField.value.length > 0 && titleField.value === "") {

		const x = new XMLHttpRequest();
		x.withCredentials=true;
		x.onreadystatechange = function() {
			if (x.readyState == 4 && x.status == 200 && !titleField.value) {

				title=JSON.parse(x.responseText)["title"];
				titleField.value=title;
				checkForRequired()
			}
		}
		x.open('get','/submit/title?url=' + urlField.value);
		x.setRequestHeader('xhr', 'xhr');
		x.send(null);

	};

};

function ghost_toggle(t) {
	const followers = document.getElementById("post-notify")
	if (t.checked == true) {
		followers.checked = false;
		followers.disabled = true;
	} else {
		followers.disabled = false;
	}
}

function checkRepost() {
	const system = document.getElementById('system')
	system.innerHTML = "";
	const url = document.getElementById('post-url').value
	const min_repost_check = 9;

	if (url && url.length >= min_repost_check) {
		const xhr = new XMLHttpRequest();
		xhr.open("post", "/is_repost");
		xhr.setRequestHeader('xhr', 'xhr');
		const form = new FormData()
		form.append("url", url);

		xhr.onload=function(){
			try {data = JSON.parse(xhr.response)}
			catch(e) {console.log(e)}

			if (data && data["permalink"]) {
				const permalinkText = escapeHTML(data["permalink"]);
				const permalinkURI = encodeURI(data["permalink"]);
				if (permalinkText) {
					system.innerHTML = `This is a repost of <a href="${permalinkURI}">${permalinkText}</a>`;
				}
			}
		}
		xhr.send(form)
	}
}

document.addEventListener('keydown', (e) => {
	if(!((e.ctrlKey || e.metaKey) && e.key === "Enter"))
		return;

	const submitButton = document.getElementById('create_button')

	submitButton.click();
});

checkRepost();

if (location.href == '/submit') {
	const sub = document.getElementById('sub')
	if (sub) sub.value = localStorage.getItem("sub")
}
