function unbanDomain(t, domain) {
	postToastSwitch(t,'/admin/unban_domain/' + domain);
	t.parentElement.parentElement.remove();
}
