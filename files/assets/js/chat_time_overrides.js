(() => {
	const DAY_MS = 24 * 60 * 60 * 1000;
	const localTimeFormatter = new Intl.DateTimeFormat(undefined, {
		hour: 'numeric',
		minute: '2-digit'
	});
	const exactTimeFormatter = new Intl.DateTimeFormat(undefined, {
		day: '2-digit',
		month: 'short',
		year: 'numeric',
		hour: '2-digit',
		minute: '2-digit',
		second: '2-digit',
		timeZoneName: 'short'
	});

	function chatDate(epoch) {
		const value = Number(epoch);
		return Number.isFinite(value) && value > 0 ? new Date(value * 1000) : null;
	}

	function relativeChatTime(epoch) {
		const date = chatDate(epoch);
		if (!date) return '';
		const age = Math.max(0, Date.now() - date.getTime());
		if (age < DAY_MS) return localTimeFormatter.format(date);

		const days = Math.max(1, Math.floor(age / DAY_MS));
		if (days < 30) return `${days}d ago`;

		const months = Math.max(1, Math.floor(days / 30));
		if (months < 12) return `${months} month${months === 1 ? '' : 's'} ago`;

		const years = Math.max(1, Math.floor(days / 365));
		return `${years} year${years === 1 ? '' : 's'} ago`;
	}

	function exactChatTime(epoch) {
		const date = chatDate(epoch);
		return date ? exactTimeFormatter.format(date) : '';
	}

	function applyTimeElement(element, message = {}) {
		if (!element) return;
		const localTime = element.querySelector('.chat-local-time');
		const messageId = element.querySelector('.chat-message-id');
		const epoch = Number(message.time ?? element.dataset.epoch);
		const id = message.id ?? messageId?.textContent?.replace(/^#/, '') ?? '';
		if (!localTime || !Number.isFinite(epoch) || epoch <= 0) return;

		const exact = exactChatTime(epoch);
		localTime.textContent = relativeChatTime(epoch);
		localTime.title = exact;
		localTime.dataset.bsToggle = 'tooltip';
		localTime.dataset.bsPlacement = 'top';
		localTime.setAttribute('aria-label', exact);
		localTime.setAttribute('role', 'text');
		localTime.removeAttribute('href');
		localTime.style.cursor = 'default';

		if (messageId && id) {
			messageId.textContent = `#${id}`;
			messageId.href = `/chat#${id}`;
		}

		element.dataset.epoch = String(epoch);
		element.title = exact;
	}

	window.formatChatTime = relativeChatTime;
	window.updateChatTime = applyTimeElement;

	function refreshChatTimes() {
		document.querySelectorAll('#chat-window .time[data-epoch]').forEach(element => applyTimeElement(element));
		if (typeof window.bs_trigger === 'function') window.bs_trigger(document.getElementById('chat-window'));
	}

	function syncUploadControl() {
		const fileInput = document.getElementById('file');
		const filename = document.getElementById('filename');
		const action = document.querySelector('.chat-upload-action');
		if (!fileInput || !filename || !action) return;
		const file = fileInput.files?.[0];
		filename.innerHTML = '<i class="fas fa-image" aria-hidden="true"></i>';
		action.classList.toggle('has-file', Boolean(file));
		action.title = file ? `Attached: ${file.name}` : 'Attach image';
		action.setAttribute('aria-label', file ? `Attached image: ${file.name}` : 'Attach image');
	}

	document.getElementById('file')?.addEventListener('change', () => setTimeout(syncUploadControl, 0));
	document.getElementById('chatsend')?.addEventListener('click', () => setTimeout(syncUploadControl, 0));
	document.addEventListener('paste', event => {
		if (event.clipboardData?.files?.length) setTimeout(syncUploadControl, 0);
	});

	refreshChatTimes();
	syncUploadControl();
	setInterval(refreshChatTimes, 60_000);
})();
