function removeFollower(t, username) {
	postToastSwitch(t,'/remove_follow/' + username);
	t.parentElement.parentElement.remove();
}
