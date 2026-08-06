(() => {
	'use strict';

	function toastError(message) {
		if (typeof showToast === 'function') showToast(false, message);
		else window.alert(message);
	}

	window.toggleContactModmailReply = function toggleContactModmailReply(id) {
		const composer = document.getElementById(`reply-message-c_${id}`);
		if (!composer) return;
		composer.classList.toggle('d-none');
		if (!composer.classList.contains('d-none')) {
			const textarea = document.getElementById(`reply-form-body-${id}`);
			textarea?.focus();
		}
	};

	window.submitContactModmailReply = function submitContactModmailReply(id) {
		const textarea = document.getElementById(`reply-form-body-${id}`);
		const button = document.getElementById(`save-reply-to-${id}`);
		if (!textarea || !button) return;

		const body = textarea.value.trim();
		if (!body) {
			toastError('Write a reply first.');
			textarea.focus();
			return;
		}

		const form = new FormData();
		form.append('parent_id', id);
		form.append('body', body);

		const input = document.getElementById(`file-upload-reply-c_${id}`);
		for (const file of Array.from(input?.files || [])) form.append('file', file);

		button.disabled = true;
		button.classList.add('disabled');
		button.textContent = 'Sending…';

		const pair = createXhrWithFormKey('/reply', 'POST', form);
		const xhr = pair[0];
		xhr.onload = () => {
			let data = null;
			try { data = JSON.parse(xhr.responseText); } catch (_) {}

			if (xhr.status >= 200 && xhr.status < 300 && data?.comment) {
				window.location.reload();
				return;
			}

			const message = typeof getMessageFromJsonData === 'function'
				? getMessageFromJsonData(false, data)
				: (data?.error || data?.message || 'The reply could not be sent.');
			toastError(message);
			button.disabled = false;
			button.classList.remove('disabled');
			button.textContent = 'Reply';
		};
		xhr.onerror = () => {
			toastError('The reply could not be sent.');
			button.disabled = false;
			button.classList.remove('disabled');
			button.textContent = 'Reply';
		};
		xhr.send(pair[1]);
	};
})();
