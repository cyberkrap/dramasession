function addParam(e) {
	e = e || window.event;
	let paramExample = e.target.innerText;
	let param = paramExample.split(":")[0];
	let searchInput = document.querySelector("#large_searchbar input");
	searchInput.value = `${searchInput.value} ${param}:`;
	searchInput.focus();
}
