function post(url) {
	const xhr = new XMLHttpRequest();
	xhr.open("POST", url);
	xhr.setRequestHeader('xhr', 'xhr');
	const form = new FormData()
	form.append("formkey", formkey());
	xhr.onload = function() {location.reload();};
	xhr.send(form);
};

function updatebgselection(){
	const bgselector = document.getElementById("backgroundSelector");
	const backgrounds = [
		{
			folder: "glitter",
			backgrounds:
			[
				"1.webp",
				"2.webp",
				"3.webp",
				"4.webp",
				"5.webp",
			]
		},
		{
			folder: "anime",
			backgrounds:
			[
				"1.webp",
				"2.webp",
				"3.webp",
				"4.webp",
				"5.webp",
				"6.webp",
			]
		},
		{
			folder: "fantasy",
			backgrounds:
			[
				"1.webp",
				"2.webp",
				"3.webp",
				"4.webp",
				"5.webp",
				"6.webp",
			]
		},
		{
			folder: "solarpunk",
			backgrounds:
			[
				"1.webp",
				"2.webp",
				"3.webp",
				"4.webp",
				"5.webp",
				"6.webp",
				"7.webp",
				"8.webp",
				"9.webp",
				"10.webp",
				"11.webp",
				"12.webp",
				"13.webp",
				"14.webp",
				"15.webp",
				"16.webp",
				"17.webp",
				"18.webp",
				"19.webp",
			]
		},
		{
			folder: "pixelart",
			backgrounds:
			[
				"1.webp",
				"2.webp",
				"3.webp",
				"4.webp",
				"5.webp",
			]
		},
	]
		let bgContainer = document.getElementById(`bgcontainer`);
		let str = '';
		let bgsToDisplay = backgrounds[bgselector.selectedIndex].backgrounds;
		let bgsDir = backgrounds[bgselector.selectedIndex].folder;
		for (i=0; i < bgsToDisplay.length; i++) {
			let onclickPost = bgsDir + "/" + bgsToDisplay[i];
			str += `<button class="btn btn-secondary bg-button"><img loading="lazy" class='bg-image' src="/i/backgrounds/${bgsDir}/${bgsToDisplay[i]}?v=2000" alt="${bgsToDisplay[i]}-background" data-nonce="${nonce}" data-onclick="post('/settings/personal?background=${onclickPost}')"></button>`;
		}
		bgContainer.innerHTML = str;

		if (typeof register_new_elements === "function") {
			register_new_elements(bgContainer)
		}
	}
	updatebgselection();

document.onpaste = function(event) {
	const focused = document.activeElement;
	if (focused.id == 'bio-text') {
		const files = structuredClone(event.clipboardData.files);

		if (files.length > 4)
		{
			alert("You can't upload more than 4 files at one time!")
			return
		}

		if (files.length)
		{
			f=document.getElementById('file-upload');
			let filename = ''
			for (const file of files)
				filename += file.name + ', '
			filename = filename.toLowerCase().slice(0, -2)
			f.files = files;
			document.getElementById('filename-show').textContent = filename;
		}
	}
}

const sr_toggle = document.getElementById("slurreplacer");
const sr_link = document.getElementById('slurreplacer-perma-link');
const pr_toggle = document.getElementById("profanityreplacer");
const pr_link = document.getElementById('profanityreplacer-perma-link');
sr_toggle.addEventListener('change', function () {
	sr_link.hidden = !sr_toggle.checked;
});
pr_toggle.addEventListener('change', function () {
	pr_link.hidden = !pr_toggle.checked;
});
