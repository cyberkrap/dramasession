function removePost(t,post_id,button1,button2,cls) {
	url="/remove_post/"+post_id

	postToastSwitch(t, url,
		button1,
		button2,
		cls,
		() => {
			if (location.pathname == '/admin/reported/posts')
			{
				document.getElementById("flaggers-"+post_id).remove()
				document.getElementById("post-"+post_id).remove()
			}
			else
			{
				document.getElementById("post-"+post_id).classList.add("banned");
			}
		}
	);
}


function approvePost(t,post_id,button1,button2,cls) {
	url="/approve_post/"+post_id

	postToastSwitch(t, url,
		button1,
		button2,
		cls,
		() => {
			if (location.pathname == '/admin/reported/posts')
			{
				document.getElementById("flaggers-"+post_id).remove()
				document.getElementById("post-"+post_id).remove()
			}
			else
			{
				document.getElementById("post-"+post_id).classList.remove("banned");
			}
		}
	);
}
