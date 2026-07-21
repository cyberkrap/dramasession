const IMAGE_FORMATS = document.getElementById('IMAGE_FORMATS').value.split(',')
const postText = document.getElementById('post-text')
const inlineFileInput = document.getElementById('file-upload-submit')
const inlineUrlButton = document.getElementById('inline-image-url-btn')
const inlineStatus = document.getElementById('inline-image-status')
let inlineUploadsPending = 0

function storedValue(key) {
	return localStorage.getItem(key) || ''
}

document.getElementById('post-title').value = storedValue('post-title')
postText.value = storedValue('post-text')
document.getElementById('post-url').value = storedValue('post-url')

for (const id of ['post-notify', 'post-new', 'post-nsfw', 'post-private', 'post-ghost']) {
	const element = document.getElementById(id)
	if (element) element.checked = localStorage.getItem(id) === 'true'
}

markdown(postText)

function checkForRequired() {
	const title = document.getElementById('post-title')
	const url = document.getElementById('post-url')
	const text = postText
	const button = document.getElementById('create_button')
	const attachment = document.getElementById('file-upload')
	const hasAttachment = attachment && attachment.files.length > 0

	if (url.value.length > 0 || hasAttachment) {
		text.required = false
		url.required = false
	} else if (text.value.length > 0) {
		text.required = false
		url.required = false
	} else {
		text.required = true
		url.required = true
	}

	const contentIsValid = url.checkValidity() || text.checkValidity() || hasAttachment
	button.disabled = inlineUploadsPending > 0 || !title.checkValidity() || !contentIsValid
}
checkForRequired()

function hide_image() {
	const block = document.getElementById('image-upload-block')
	const url = document.getElementById('post-url').value
	if (url.length >= 1) block.classList.add('d-none')
	else block.classList.remove('d-none')
}

function setInlineStatus(message, isError=false) {
	if (!inlineStatus) return
	inlineStatus.textContent = message
	inlineStatus.classList.toggle('text-danger', isError)
	inlineStatus.classList.toggle('text-success', !isError && Boolean(message))
}

function insertAtCursor(text, start=null, end=null) {
	const insertionStart = start === null ? postText.selectionStart : start
	const insertionEnd = end === null ? postText.selectionEnd : end
	const before = postText.value.slice(0, insertionStart)
	const after = postText.value.slice(insertionEnd)
	const needsLeadingBreak = before && !before.endsWith('\n')
	const needsTrailingBreak = after && !after.startsWith('\n')
	const insertion = `${needsLeadingBreak ? '\n\n' : ''}${text}${needsTrailingBreak ? '\n\n' : ''}`

	postText.value = before + insertion + after
	const newPosition = before.length + insertion.length
	postText.focus()
	postText.setSelectionRange(newPosition, newPosition)
	postText.dispatchEvent(new Event('input', {bubbles: true}))
}

async function parseUploadError(response) {
	try {
		const data = await response.json()
		return data.error || data.message || `Upload failed (${response.status})`
	} catch (_) {
		return `Upload failed (${response.status})`
	}
}

async function uploadInlineImages({files=[], urls=[], cursorStart=null, cursorEnd=null, fallbackText=''}) {
	if (!files.length && !urls.length) return false

	const form = new FormData()
	const formkey = document.querySelector('#submitform input[name="formkey"]')
	if (formkey && formkey.value) form.append('formkey', formkey.value)
	for (const file of files) form.append('file', file)
	for (const url of urls) form.append('url', url)

	inlineUploadsPending += 1
	checkForRequired()
	setInlineStatus(`Uploading ${files.length + urls.length} image${files.length + urls.length === 1 ? '' : 's'}...`)

	try {
		const response = await fetch('/api/images/inline', {
			method: 'POST',
			body: form,
			credentials: 'same-origin',
			headers: {'xhr': 'xhr'},
		})
		if (!response.ok) throw new Error(await parseUploadError(response))

		const data = await response.json()
		if (!data.markdown) throw new Error('The server returned no image URLs.')
		insertAtCursor(data.markdown, cursorStart, cursorEnd)
		setInlineStatus(`${data.urls.length} image${data.urls.length === 1 ? '' : 's'} inserted.`)
		window.setTimeout(() => setInlineStatus(''), 3000)
		return true
	} catch (error) {
		if (fallbackText) insertAtCursor(fallbackText, cursorStart, cursorEnd)
		setInlineStatus(error.message || 'Image upload failed.', true)
		return false
	} finally {
		inlineUploadsPending -= 1
		if (inlineFileInput) inlineFileInput.value = ''
		checkForRequired()
	}
}

if (inlineFileInput) {
	inlineFileInput.addEventListener('change', () => {
		const files = Array.from(inlineFileInput.files).filter(file => file.type.startsWith('image/'))
		if (files.length !== inlineFileInput.files.length) {
			setInlineStatus('Only images can be inserted into the editor.', true)
		}
		if (files.length) {
			uploadInlineImages({
				files,
				cursorStart: postText.selectionStart,
				cursorEnd: postText.selectionEnd,
			})
		}
	})
}

if (inlineUrlButton) {
	inlineUrlButton.addEventListener('click', () => {
		const value = window.prompt('Paste an image URL to import and host on Obsession:')
		if (!value) return
		uploadInlineImages({
			urls: [value.trim()],
			cursorStart: postText.selectionStart,
			cursorEnd: postText.selectionEnd,
		})
	})
}

postText.addEventListener('paste', event => {
	const files = Array.from(event.clipboardData.files || []).filter(file => file.type.startsWith('image/'))
	if (files.length) {
		event.preventDefault()
		uploadInlineImages({
			files,
			cursorStart: postText.selectionStart,
			cursorEnd: postText.selectionEnd,
		})
		return
	}

	const pastedText = event.clipboardData.getData('text/plain').trim()
	if (/^https?:\/\/\S+$/i.test(pastedText)) {
		event.preventDefault()
		uploadInlineImages({
			urls: [pastedText],
			cursorStart: postText.selectionStart,
			cursorEnd: postText.selectionEnd,
			fallbackText: pastedText,
		})
	}
})

postText.addEventListener('dragover', event => {
	if (Array.from(event.dataTransfer.items || []).some(item => item.kind === 'file')) {
		event.preventDefault()
		event.dataTransfer.dropEffect = 'copy'
	}
})

postText.addEventListener('drop', event => {
	const files = Array.from(event.dataTransfer.files || []).filter(file => file.type.startsWith('image/'))
	if (!files.length) return
	event.preventDefault()
	uploadInlineImages({
		files,
		cursorStart: postText.selectionStart,
		cursorEnd: postText.selectionEnd,
	})
})

const attachmentInput = document.getElementById('file-upload')
if (attachmentInput) {
	attachmentInput.addEventListener('change', function() {
		if (!this.files.length) return
		document.getElementById('urlblock').classList.add('d-none')
		document.getElementById('filename-show').textContent = this.files[0].name.substr(0, 20)
		const filename = this.files[0].name.toLowerCase()
		if (IMAGE_FORMATS.some(format => filename.endsWith(format))) {
			const fileReader = new FileReader()
			fileReader.readAsDataURL(this.files[0])
			fileReader.addEventListener('load', function() {
				document.getElementById('image-preview').setAttribute('src', this.result)
			})
		}
		checkForRequired()
	})
}

function savetext() {
	localStorage.setItem('post-title', document.getElementById('post-title').value)
	localStorage.setItem('post-text', postText.value)
	localStorage.setItem('post-url', document.getElementById('post-url').value)

	const sub = document.getElementById('sub')
	if (sub) localStorage.setItem('sub', sub.value)

	for (const id of ['post-notify', 'post-new', 'post-nsfw', 'post-private', 'post-ghost']) {
		const element = document.getElementById(id)
		if (element) localStorage.setItem(id, element.checked)
	}
}

function autoSuggestTitle() {
	const urlField = document.getElementById('post-url')
	const titleField = document.getElementById('post-title')
	if (urlField.checkValidity() && urlField.value.length > 0 && titleField.value === '') {
		const x = new XMLHttpRequest()
		x.withCredentials = true
		x.onreadystatechange = function() {
			if (x.readyState === 4 && x.status === 200 && !titleField.value) {
				titleField.value = JSON.parse(x.responseText).title
				checkForRequired()
			}
		}
		x.open('get', '/submit/title?url=' + encodeURIComponent(urlField.value))
		x.setRequestHeader('xhr', 'xhr')
		x.send(null)
	}
}

function ghost_toggle(t) {
	const followers = document.getElementById('post-notify')
	if (t.checked) {
		followers.checked = false
		followers.disabled = true
	} else followers.disabled = false
}

function checkRepost() {
	const system = document.getElementById('system')
	system.innerHTML = ''
	const url = document.getElementById('post-url').value
	if (url && url.length >= 9) {
		const xhr = new XMLHttpRequest()
		xhr.open('post', '/is_repost')
		xhr.setRequestHeader('xhr', 'xhr')
		const form = new FormData()
		form.append('url', url)
		xhr.onload = function() {
			let data
			try { data = JSON.parse(xhr.response) }
			catch (e) { console.log(e) }
			if (data && data.permalink) {
				const permalinkText = escapeHTML(data.permalink)
				const permalinkURI = encodeURI(data.permalink)
				if (permalinkText) system.innerHTML = `This is a repost of <a href="${permalinkURI}">${permalinkText}</a>`
			}
		}
		xhr.send(form)
	}
}

document.addEventListener('keydown', event => {
	if (!((event.ctrlKey || event.metaKey) && event.key === 'Enter')) return
	document.getElementById('create_button').click()
})

checkRepost()
if (location.pathname === '/submit') {
	const sub = document.getElementById('sub')
	if (sub) sub.value = storedValue('sub')
}
