function view_more(t, pid, sort, offset) {
	btn = document.getElementById("viewbtn");
	btn.disabled = true;
	btn.innerHTML = "Requesting...";
	const form = new FormData();
	const xhr = new XMLHttpRequest();
	ids = t.dataset.ids.toString().replace(/[\[\] ]/g, '')
	xhr.open("get", `/view_more/${pid}/${sort}/${offset}?ids=${ids}`);
	xhr.setRequestHeader('xhr', 'xhr');
	xhr.onload=function(){
		if (xhr.status==200) {
			let e = document.getElementById(`view_more-${offset}`);
			e.innerHTML = xhr.response.replace(/data-src/g, 'src').replace(/data-cfsrc/g, 'src').replace(/style="display:none;visibility:hidden;"/g, '').replace(/data-nonce=".*?"/g, `data-nonce="${nonce}"`);
			register_new_elements(e);
			bs_trigger(e)

			highlight_unread("old-comment-counts")
		}
		btn.disabled = false;
	}
	xhr.send(form)
}
