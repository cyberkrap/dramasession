(() => {
	'use strict';

	const selector = 'textarea[id^="reply-form-body-"]';
	const installed = new WeakSet();
	const pendingUploads = new WeakMap();
	const savedSelections = new WeakMap();

	function composerFor(textarea) {
		return textarea.closest('[id^="reply-message-"]');
	}

	function replyButtonFor(textarea) {
		const id = textarea.id.replace('reply-form-body-', '');
		return document.getElementById(`save-reply-to-${id}`);
	}

	function setPending(textarea, delta) {
		const next = Math.max(0, (pendingUploads.get(textarea) || 0) + delta);
		pendingUploads.set(textarea, next);
		const button = replyButtonFor(textarea);
		if (button) {
			button.disabled = next > 0;
			button.classList.toggle('disabled', next > 0);
		}
	}

	function ensureMeta(composer, textarea) {
		let meta = composer.querySelector('.message-inline-image-meta');
		if (meta) return meta;

		meta = document.createElement('div');
		meta.className = 'message-inline-image-meta';
		meta.innerHTML = '<span class="message-inline-image-status" aria-live="polite"></span><span class="message-inline-image-help">Images upload immediately and are inserted where your cursor is. You can also paste or drop images into the text box.</span>';
		const inputGroup = textarea.closest('.input-group');
		if (inputGroup) inputGroup.after(meta);
		return meta;
	}

	function setStatus(textarea, message, isError = false) {
		const composer = composerFor(textarea);
		if (!composer) return;
		const status = ensureMeta(composer, textarea).querySelector('.message-inline-image-status');
		status.textContent = message;
		status.classList.toggle('text-danger', isError);
		status.classList.toggle('text-success', !isError && Boolean(message));
	}

	function rememberSelection(textarea) {
		savedSelections.set(textarea, {
			start: textarea.selectionStart,
			end: textarea.selectionEnd,
		});
	}

	function selectionFor(textarea) {
		return savedSelections.get(textarea) || {
			start: textarea.selectionStart,
			end: textarea.selectionEnd,
		};
	}

	function insertAt(textarea, markdown, selection) {
		const start = Math.max(0, Math.min(selection.start, textarea.value.length));
		const end = Math.max(start, Math.min(selection.end, textarea.value.length));
		const before = textarea.value.slice(0, start);
		const after = textarea.value.slice(end);
		const leading = before && !before.endsWith('\n') ? '\n\n' : '';
		const trailing = after && !after.startsWith('\n') ? '\n\n' : '';
		const insertion = `${leading}${markdown}${trailing}`;

		textarea.value = before + insertion + after;
		const caret = before.length + insertion.length;
		textarea.focus();
		textarea.setSelectionRange(caret, caret);
		rememberSelection(textarea);
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

	async function upload(textarea, {files = [], urls = [], selection = null, fallbackText = ''}) {
		if (!files.length && !urls.length) return false;
		const target = selection || selectionFor(textarea);
		const form = new FormData();
		const key = typeof formkey === 'function' ? formkey() : null;
		if (key) form.append('formkey', key);
		files.forEach(file => form.append('file', file));
		urls.forEach(url => form.append('url', url));

		setPending(textarea, 1);
		setStatus(textarea, `Uploading ${files.length + urls.length} image${files.length + urls.length === 1 ? '' : 's'}...`);

		try {
			const response = await fetch('/api/images/inline', {
				method: 'POST',
				body: form,
				credentials: 'same-origin',
				headers: {'xhr': 'xhr'},
			});
			if (!response.ok) throw new Error(await uploadError(response));

			const data = await response.json();
			if (!data.markdown) throw new Error('The server returned no image URLs.');
			insertAt(textarea, data.markdown, target);
			setStatus(textarea, `${data.urls.length} image${data.urls.length === 1 ? '' : 's'} inserted.`);
			window.setTimeout(() => setStatus(textarea, ''), 3000);
			return true;
		} catch (error) {
			if (fallbackText) insertAt(textarea, fallbackText, target);
			setStatus(textarea, error.message || 'Image upload failed.', true);
			return false;
		} finally {
			setPending(textarea, -1);
		}
	}

	function install(textarea) {
		if (!(textarea instanceof HTMLTextAreaElement) || installed.has(textarea)) return;
		const composer = composerFor(textarea);
		if (!composer) return;
		const input = composer.querySelector('input[type="file"][id^="file-upload-reply-"]');
		if (!input) return;

		installed.add(textarea);
		input.multiple = true;
		input.accept = 'image/*';
		input.removeAttribute('name');

		const label = composer.querySelector(`label[for="${CSS.escape(input.id)}"]`);
		const filename = label?.querySelector('[id^="filename-show-reply-"]');
		const toolbar = input.closest('.comment-format');
		if (toolbar) toolbar.classList.add('inline-editor-toolbar');
		if (label) label.classList.add('inline-editor-control', 'inline-editor-control-square');

		const resetFilename = () => {
			input.value = '';
			if (filename) filename.innerHTML = '<i class="fas fa-images"></i>';
		};
		resetFilename();

		if (label) {
			label.title = 'Upload images at the cursor';
			label.addEventListener('pointerdown', () => rememberSelection(textarea));
			label.addEventListener('keydown', () => rememberSelection(textarea));
		}

		const emoji = toolbar?.querySelector('button[data-onclick*="loadEmojis"]');
		if (emoji) emoji.classList.add('inline-editor-control', 'inline-editor-control-square');

		let urlButton = composer.querySelector('.message-inline-image-url');
		if (!urlButton && toolbar) {
			urlButton = document.createElement('button');
			urlButton.type = 'button';
			urlButton.className = 'btn btn-secondary message-inline-image-url inline-editor-control inline-editor-control-wide';
			urlButton.innerHTML = '<i class="fas fa-link" aria-hidden="true"></i><span>Image URL</span>';
			urlButton.title = 'Import an image URL at the cursor';
			label ? label.after(urlButton) : toolbar.append(urlButton);
		}

		ensureMeta(composer, textarea);
		['focus', 'click', 'keyup', 'select'].forEach(type => textarea.addEventListener(type, () => rememberSelection(textarea)));

		input.addEventListener('change', () => {
			const allFiles = Array.from(input.files || []);
			const files = allFiles.filter(file => file.type.startsWith('image/'));
			if (files.length !== allFiles.length) setStatus(textarea, 'Only images can be inserted into messages.', true);
			if (!files.length) {
				resetFilename();
				return;
			}
			const target = selectionFor(textarea);
			upload(textarea, {files, selection: target}).finally(resetFilename);
		});

		urlButton?.addEventListener('pointerdown', () => rememberSelection(textarea));
		urlButton?.addEventListener('click', () => {
			const value = window.prompt('Paste an image URL to import and host on Obsession:');
			if (!value) return;
			upload(textarea, {urls: [value.trim()], selection: selectionFor(textarea)});
		});

		textarea.addEventListener('paste', event => {
			const files = Array.from(event.clipboardData?.files || []).filter(file => file.type.startsWith('image/'));
			const target = {start: textarea.selectionStart, end: textarea.selectionEnd};
			if (files.length) {
				event.preventDefault();
				upload(textarea, {files, selection: target});
				return;
			}

			const pasted = event.clipboardData?.getData('text/plain')?.trim() || '';
			if (/^https?:\/\/\S+$/i.test(pasted)) {
				event.preventDefault();
				upload(textarea, {urls: [pasted], selection: target, fallbackText: pasted});
			}
		});

		textarea.addEventListener('dragover', event => {
			if (Array.from(event.dataTransfer?.items || []).some(item => item.kind === 'file')) {
				event.preventDefault();
				event.dataTransfer.dropEffect = 'copy';
			}
		});

		textarea.addEventListener('drop', event => {
			const files = Array.from(event.dataTransfer?.files || []).filter(file => file.type.startsWith('image/'));
			if (!files.length) return;
			event.preventDefault();
			upload(textarea, {
				files,
				selection: {start: textarea.selectionStart, end: textarea.selectionEnd},
			});
		});
	}

	function scan(root = document) {
		if (root instanceof HTMLTextAreaElement && root.matches(selector)) install(root);
		root.querySelectorAll?.(selector).forEach(install);
	}

	function start() {
		scan();
		new MutationObserver(mutations => {
			for (const mutation of mutations) {
				for (const node of mutation.addedNodes) {
					if (node instanceof Element) scan(node);
				}
			}
		}).observe(document.body, {childList: true, subtree: true});
	}

	if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, {once: true});
	else start();
})();