(() => {
	const triggerSelector = '.user-name[data-bs-toggle="popover"]';

	function initializePopover(trigger) {
		if (!trigger || trigger.dataset.obsPopoverReady === '1' || typeof bootstrap === 'undefined') return;
		const popoverId = trigger.getAttribute('data-content-id');
		const content = popoverId ? document.getElementById(popoverId) : null;
		if (!content) return;
		const existing = bootstrap.Popover.getInstance(trigger);
		if (existing) existing.dispose();
		trigger.setAttribute('data-bs-trigger', 'click');
		bootstrap.Popover.getOrCreateInstance(trigger, {content: content.innerHTML, html: true, trigger: 'click', container: 'body'});
		trigger.dataset.obsPopoverReady = '1';
	}

	function renameActivity() {
		const activity = document.querySelector('.profile-history');
		if (!activity) return;
		const labels = {'/upvoters':'Upvoters','/downvoters':'Downvoters','/upvoting':'Upvoted','/downvoting':'Downvoted'};
		activity.querySelectorAll('a').forEach(link => {
			for (const [path, label] of Object.entries(labels)) {
				if (link.pathname.endsWith(path)) link.textContent = label;
			}
		});
	}

	document.addEventListener('DOMContentLoaded', () => {
		document.querySelectorAll(triggerSelector).forEach(initializePopover);
		renameActivity();
	});
})();
