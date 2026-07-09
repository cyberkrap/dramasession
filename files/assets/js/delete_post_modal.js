function delete_postModal(t, id) {
	document.getElementById("deletePostButton").addEventListener('click', function() {
		postToast(t, `/delete_post/${id}`,
			{
			},
			() => {
				if (location.pathname == '/admin/reported/posts')
				{
					document.getElementById("flaggers-"+id).remove()
					document.getElementById("post-"+id).remove()
				}
				else
				{
					document.getElementById(`post-${id}`).classList.add('deleted');
					document.getElementById(`delete-${id}`).classList.add('d-none');
					document.getElementById(`undelete-${id}`).classList.remove('d-none');
					document.getElementById(`delete2-${id}`).classList.add('d-none');
					document.getElementById(`undelete2-${id}`).classList.remove('d-none');
				}
			}
		);
	});
}
