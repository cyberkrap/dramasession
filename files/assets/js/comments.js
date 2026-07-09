function poll_vote_no_v() {
	showToast(false, "Only logged-in users can vote!");
}

function expandMarkdown(id,type) {
	const ta = document.getElementById('markdown-'+id);
	ta.classList.toggle('d-none');
	document.getElementsByClassName('text-expand-icon-'+id)[0].classList.toggle('fa-expand-alt');
	document.getElementsByClassName('text-expand-icon-'+id)[0].classList.toggle('fa-compress-alt');

	const items = document.getElementsByClassName(`expand-text-${type}-${id}`)
	for (let i=0; i < items.length; i++)
	{
		const e = items[i]
		if (e.innerHTML == 'View source') e.innerHTML = 'Hide source'
		else e.innerHTML = 'View source'
	}
};

function collapse_comment(id) {
	const element = document.getElementById(`comment-${id}`)
	const closed = element.classList.toggle("collapsed")
	const top = element.getBoundingClientRect().y

	if (closed && top < 0) {
		element.scrollIntoView()
		window.scrollBy(0, - 100)
	}

	const flags = document.getElementById(`flaggers-${id}`)
	if (flags) flags.classList.add('d-none')

	vids = element.getElementsByTagName('video')
	for (let i=0; i < vids.length; i++)
	{
		vids[i].pause()
	}

	const ta = document.getElementById('markdown-'+id);
	if (!ta.classList.contains('d-none'))
		expandMarkdown(id,'c')
};
