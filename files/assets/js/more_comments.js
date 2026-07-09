function more_comments(cid, sort) {
	btn = document.getElementById(`btn-${cid}`);
	btn.disabled = true;
	btn.innerHTML = "Requesting...";
	const form = new FormData();
	form.append("formkey", formkey());
	form.append("sort", sort);
	const xhr = new XMLHttpRequest();
	xhr.open("get", `/more_comments/${cid}`);
	xhr.setRequestHeader('xhr', 'xhr');
	xhr.onload=function(){
		if (xhr.status==200) {
			let e = document.getElementById(`replies-of-c_${cid}`)
			e.innerHTML = xhr.response.replace(/data-src/g, 'src').replace(/data-cfsrc/g, 'src').replace(/style="display:none;visibility:hidden;"/g, '').replace(/data-nonce=".*?"/g, `data-nonce="${nonce}"`);
			register_new_elements(e);
			bs_trigger(e)

			highlight_unread("old-comment-counts")
		}
		btn.disabled = false;
	}
	xhr.send(form)
}
