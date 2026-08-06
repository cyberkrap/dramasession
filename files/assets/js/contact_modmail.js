(() => {
	'use strict';

	function toastError(message) {
		if (typeof showToast === 'function') showToast(false, message);
		else window.alert(message);
	}

	function replyToggleFor(id, trigger) {
		if (trigger?.classList?.contains('contact-thread__reply-toggle')) return trigger;
		return document.querySelector(`#modmail-thread-${id} .contact-thread__reply-toggle`);
	}

	function restoreButton(button) {
		button.disabled = false;
		button.classList.remove('disabled');
		button.innerHTML = button.dataset.originalHtml || '<span>Send reply</span><i class="fas fa-paper-plane"></i>';
	}

	window.toggleContactModmailReply = function toggleContactModmailReply(id, trigger) {
		const composer = document.getElementById(`reply-message-c_${id}`);
		if (!composer) return;

		const thread = composer.closest('details');
		if (thread) thread.open = true;

		const opening = composer.classList.contains('d-none');
		composer.classList.toggle('d-none', !opening);

		const toggle = replyToggleFor(id, trigger);
		if (toggle) toggle.setAttribute('aria-expanded', opening ? 'true' : 'false');

		if (opening) {
			const textarea = document.getElementById(`reply-form-body-${id}`);
			requestAnimationFrame(() => {
				composer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
				textarea?.focus({ preventScroll: true });
			});
		} else if (toggle) {
			toggle.focus({ preventScroll: true });
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

		button.dataset.originalHtml = button.innerHTML;
		button.disabled = true;
		button.classList.add('disabled');
		button.innerHTML = '<span>Sending…</span><i class="fas fa-circle-notch fa-spin"></i>';

		const pair = createXhrWithFormKey('/reply', 'POST', form);
		const xhr = pair[0];
		xhr.onload = () => {
			let data = null;
			try { data = JSON.parse(xhr.responseText); } catch (_) {}

			if (xhr.status >= 200 && xhr.status < 300 && data?.comment) {
				window.location.hash = `modmail-thread-${id}`;
				window.location.reload();
				return;
			}

			const message = typeof getMessageFromJsonData === 'function'
				? getMessageFromJsonData(false, data)
				: (data?.error || data?.message || 'The reply could not be sent.');
			toastError(message);
			restoreButton(button);
		};
		xhr.onerror = () => {
			toastError('The reply could not be sent.');
			restoreButton(button);
		};
		xhr.send(pair[1]);
	};

	document.addEventListener('DOMContentLoaded', () => {
		const target = window.location.hash && document.querySelector(window.location.hash);
		if (target?.matches?.('details.contact-thread')) target.open = true;

		document.querySelectorAll('.contact-thread__composer textarea').forEach((textarea) => {
			textarea.addEventListener('keydown', (event) => {
				if (!((event.ctrlKey || event.metaKey) && event.key === 'Enter')) return;
				event.preventDefault();
				const id = textarea.dataset.id;
				if (id) window.submitContactModmailReply(id);
			});
		});
	});
})();
