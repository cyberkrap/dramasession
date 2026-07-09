function removeComment(t,comment_id,button1,button2,cls) {
	url="/remove_comment/"+comment_id

	postToastSwitch(t, url,
		button1,
		button2,
		cls,
		() => {
			if (location.pathname == '/admin/reported/comments')
			{
				document.getElementById("post-info-"+comment_id).remove()
				document.getElementById("comment-"+comment_id).remove()
			}
			else
			{
				try {
					document.getElementById("comment-"+comment_id+"-only").classList.add("banned");
				} catch(e) {
					document.getElementById("context").classList.add("banned");
				}
			}
		}
	);
}

function approveComment(t,comment_id,button1,button2,cls) {
	url="/approve_comment/"+comment_id

	postToastSwitch(t, url,
		button1,
		button2,
		cls,
		() => {
			if (location.pathname == '/admin/reported/comments')
			{
				document.getElementById("post-info-"+comment_id).remove()
				document.getElementById("comment-"+comment_id).remove()
			}
			else
			{
				try {
					document.getElementById("comment-"+comment_id+"-only").classList.remove("banned");
				} catch(e) {
					document.getElementById("context").classList.remove("banned");
				}
			}
		}
	);
}
