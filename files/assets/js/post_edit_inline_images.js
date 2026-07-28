(() => {
	'use strict';

	const initialized = new WeakSet();

	function imageFilesFromTransfer(transfer) {
		const files = Array.from(transfer?.files || []).filter(file => file.type?.startsWith('image/'));
		if (files.length) return files;
		return Array.from(transfer?.items || [])
			.filter(item => item.kind === 'file' && item.type?.startsWith('image/'))
			.map(item => item.getAsFile())
			.filter(Boolean);
	}

	function insertAtCursor(textarea, text, start = null, end = null) {
		const insertionStart = start === null ? textarea.selectionStart : start;
		const insertionEnd = end === null ? textarea.selectionEnd : end;
		const before = textarea.value.slice(0, insertionStart);
		const after = textarea.value.slice(insertionEnd);
		const leading = before && !before.endsWith('\n') ? '\n\n' : '';
		const trailing = after && !after.startsWith('\n') ? '\n\n' : '';
		const insertion = `${leading}${text}${trailing}`;

		textarea.value = before + insertion + after;
		const cursor = before.length + insertion.length;
		textarea.focus();
		textarea.setSelectionRange(cursor, cursor);
		textarea.dispatchEvent(new Event('input', {bubbles: true}));
	}

	async function uploadError(response) {
		try {
			const data = await response.json();
			return data.error || data.message || `Upload failed (${response.status})`;
		} catch (_) {
			return `Upload failed (${response.status})`;
		}
	}

	function initializeEditor(textarea) {
		if (!(textarea instanceof HTMLTextAreaElement) || initialized.has(textarea)) return;
		const wrapper = textarea.closest('.comment-write');
		const form = textarea.form || wrapper?.querySelector('form');
		const toolbar = wrapper?.querySelector('.comment-format');
		if (!(wrapper instanceof Element) || !(form instanceof HTMLFormElement) || !(toolbar instanceof Element)) return;
		initialized.add(textarea);
		toolbar.classList.add('obs-post-edit-toolbar');

		const uploadInput = toolbar.querySelector('input[type="file"][id^="file-upload-edit-"]');
		const uploadLabel = uploadInput ? toolbar.querySelector(`label[for="${CSS.escape(uploadInput.id)}"]`) : null;
		if (!(uploadInput instanceof HTMLInputElement) || !(uploadLabel instanceof HTMLLabelElement)) return;

		// Reuse the original attachment control instead of adding a duplicate button.
		uploadInput.accept = 'image/*';
		uploadInput.multiple = true;
		uploadInput.removeAttribute('name');
		uploadInput.removeAttribute('data-onchange');
		uploadLabel.className = 'format btn btn-secondary obs-post-edit-tool';
		uploadLabel.title = 'Upload images at the cursor';
		uploadLabel.setAttribute('aria-label', 'Upload images');
		uploadLabel.replaceChildren();
		const uploadIcon = document.createElement('i');
		uploadIcon.className = 'fas fa-images';
		uploadIcon.setAttribute('aria-hidden', 'true');
		uploadLabel.append(uploadIcon, uploadInput);

		const hiddenLink = toolbar.querySelector('small.format.d-none');
		if (hiddenLink) hiddenLink.remove();

		const urlButton = document.createElement('button');
		urlButton.type = 'button';
		urlButton.className = 'format btn btn-secondary obs-post-edit-tool obs-post-edit-url';
		urlButton.title = 'Import an image URL at the cursor';
		urlButton.innerHTML = '<i class="fas fa-link" aria-hidden="true"></i><span>Image URL</span>';
		toolbar.append(urlButton);

		const info = document.createElement('div');
		info.className = 'obs-post-edit-upload-info';
		const status = document.createElement('span');
		status.className = 'obs-post-edit-upload-status';
		status.setAttribute('aria-live', 'polite');
		const help = document.createElement('span');
		help.className = 'obs-post-edit-upload-help';
		help.textContent = 'Paste, drop, upload, or import images. They are inserted at your cursor.';
		info.append(status, help);
		toolbar.insertAdjacentElement('afterend', info);

		const formkey = form.querySelector('input[name="formkey"]');
		const saveButton = form.querySelector('button[type="submit"]');
		let pending = 0;
		let saveWasDisabled = false;

		function setStatus(message, error = false) {
			status.textContent = message;
			status.classList.toggle('text-danger', error);
			status.classList.toggle('text-success', !error && Boolean(message));
			info.classList.toggle('has-status', Boolean(message));
		}

		function setPending(delta) {
			if (pending === 0 && delta > 0 && saveButton instanceof HTMLButtonElement) saveWasDisabled = saveButton.disabled;
			pending = Math.max(0, pending + delta);
			if (saveButton instanceof HTMLButtonElement) saveButton.disabled = pending > 0 || saveWasDisabled;
		}

		async function upload({files = [], urls = [], start = null, end = null, fallbackText = ''}) {
			if (!files.length && !urls.length) return;
			const data = new FormData();
			if (formkey?.value) data.append('formkey', formkey.value);
			files.forEach(file => data.append('file', file));
			urls.forEach(url => data.append('url', url));

			setPending(1);
			setStatus(`Uploading ${files.length + urls.length} image${files.length + urls.length === 1 ? '' : 's'}...`);
			try {
				const response = await fetch('/api/images/inline', {
					method: 'POST',
					body: data,
					credentials: 'same-origin',
					headers: {'xhr': 'xhr'},
				});
				if (!response.ok) throw new Error(await uploadError(response));
				const result = await response.json();
				if (!result.markdown) throw new Error('The server returned no image URLs.');
				insertAtCursor(textarea, result.markdown, start, end);
				const count = Array.isArray(result.urls) ? result.urls.length : files.length + urls.length;
				setStatus(`${count} image${count === 1 ? '' : 's'} inserted.`);
				window.setTimeout(() => {
					if (!pending) setStatus('');
				}, 3000);
			} catch (error) {
				if (fallbackText) insertAtCursor(textarea, fallbackText, start, end);
				setStatus(error?.message || 'Image upload failed.', true);
			} finally {
				uploadInput.value = '';
				setPending(-1);
			}
		}

		uploadInput.addEventListener('change', () => {
			const files = Array.from(uploadInput.files || []).filter(file => file.type?.startsWith('image/'));
			if (files.length !== (uploadInput.files?.length || 0)) setStatus('Only images can be inserted into the editor.', true);
			if (files.length) upload({files, start: textarea.selectionStart, end: textarea.selectionEnd});
		});

		urlButton.addEventListener('click', () => {
			const value = window.prompt('Paste an image URL to import and host on Obsession:');
			if (!value?.trim()) return;
			upload({urls: [value.trim()], start: textarea.selectionStart, end: textarea.selectionEnd});
		});

		textarea.addEventListener('paste', event => {
			const files = imageFilesFromTransfer(event.clipboardData);
			if (files.length) {
				event.preventDefault();
				upload({files, start: textarea.selectionStart, end: textarea.selectionEnd});
				return;
			}
			const text = event.clipboardData?.getData('text/plain')?.trim() || '';
			if (/^https?:\/\/\S+$/i.test(text)) {
				event.preventDefault();
				upload({urls: [text], start: textarea.selectionStart, end: textarea.selectionEnd, fallbackText: text});
			}
		});

		textarea.addEventListener('dragover', event => {
			if (!imageFilesFromTransfer(event.dataTransfer).length) return;
			event.preventDefault();
			event.dataTransfer.dropEffect = 'copy';
		});

		textarea.addEventListener('drop', event => {
			const files = imageFilesFromTransfer(event.dataTransfer);
			if (!files.length) return;
			event.preventDefault();
			upload({files, start: textarea.selectionStart, end: textarea.selectionEnd});
		});
	}

	function scan(root = document) {
		if (root instanceof HTMLTextAreaElement && root.id.startsWith('post-edit-box-')) initializeEditor(root);
		root.querySelectorAll?.('textarea[id^="post-edit-box-"]').forEach(initializeEditor);
	}

	function initialize() {
		scan(document);
		const observer = new MutationObserver(mutations => {
			for (const mutation of mutations) {
				for (const node of mutation.addedNodes) if (node instanceof Element) scan(node);
			}
		});
		observer.observe(document.body, {childList: true, subtree: true});
	}

	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize, {once: true});
	else initialize();
})();