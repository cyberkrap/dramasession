function removeFollowing(t, username) {
	postToastSwitch(t,'/unfollow/' + username);
	t.parentElement.parentElement.remove();
}
