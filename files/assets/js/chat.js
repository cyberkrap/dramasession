const chatState = {
	messages: new Map(),
	loadingHistory: false,
	hasMoreHistory: true,
	filters: {},
	pendingAround: null,
};

const socket = io({
	path: '/socket.io/',
	transports: ['websocket', 'polling'],
	reconnection: true,
});

const chatlineTemplate = document.querySelector('#chat-line-template .chat-line');
const chatgroupTemplate = document.querySelector('#chat-group-template .chat-group');
const box = document.getElementById('chat-window');
const textbox = document.getElementById('input-text');
const fileInput = document.getElementById('file');
const sendButton = document.getElementById('chatsend');
const statusElement = document.getElementById('chat-status');
const vid = Number(document.getElementById('vid').value);
const siteName = document.getElementById('site_name').value;
const slurreplacer = document.getElementById('slurreplacer').value;
const adminLevel = Number(document.getElementById('admin_level')?.value || 0);
const canModerateChat = adminLevel > 1;
const initialData = document.getElementById('chat-initial-data');
const initialMessages = initialData ? JSON.parse(initialData.textContent || '[]') : [];
const initialHasMore = document.getElementById('chat-has-more');
const loadMoreButton = document.getElementById('chat-load-more');
const mentionSuggestions = document.getElementById('chat-mention-suggestions');
const mobileOnlinePanel = document.getElementById('mobile-online-panel');
const onlineTrigger = document.getElementById('online2');

chatState.hasMoreHistory = initialHasMore ? initialHasMore.value === '1' : true;
for (const message of initialMessages) chatState.messages.set(String(message.id), message);

let notifs = 0;
let focused = true;
let isTyping = false;
let alertIcon = true;
let pendingDelete = null;
let mentionState = { items: [], index: -1, request: 0, token: null };

function chatEscapeHtml(value) {
	return String(value ?? '').replace(/[&<>'"]/g, character => ({
		'&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
	}[character]));
}

function formatChatTime(epoch) {
	if (!epoch) return '';
	return new Intl.DateTimeFormat(undefined, {hour: 'numeric', minute: '2-digit'}).format(new Date(Number(epoch) * 1000));
}

function updateChatTime(element, message) {
	const localTime = element.querySelector('.chat-local-time');
	const messageId = element.querySelector('.chat-message-id');
	if (!localTime || !messageId) return;
	localTime.textContent = formatChatTime(message.time);
	localTime.href = `/chat#${message.id}`;
	messageId.textContent = `#${message.id}`;
	messageId.href = `/chat#${message.id}`;
	element.dataset.epoch = message.time;
	element.title = new Date(Number(message.time) * 1000).toLocaleString();
}

function setChatStatus(message, temporary = false) {
	if (!statusElement) return;
	statusElement.textContent = message || '';
	statusElement.classList.toggle('d-none', !message);
	if (temporary && message) setTimeout(() => {
		if (statusElement.textContent === message) statusElement.textContent = '';
	}, 3000);
}

function renderChatBody(message) {
	return String(slurreplacer !== '0' ? message.text_censored : message.text_html || '')
		.replace(/data-src/g, 'src')
		.replace(/data-cfsrc/g, 'src')
		.replace(/style="display:none;visibility:hidden;"/g, '');
}

function removalNoticeHtml(message, hasOriginal) {
	const username = chatEscapeHtml(message.removed_by);
	const margin = hasOriginal ? 'margin-top:7px;' : '';
	return `<div class="chat-removal-notice${hasOriginal ? ' chat-removal-notice-admin' : ''}" style="display:block;${margin}padding:6px 8px;color:#ff6b7d;background:rgba(220,35,58,.12);border-left:3px solid #dc233a;border-radius:2px;font-size:.82rem;line-height:1.3;font-style:italic;">This message was removed by <a href="/@${username}" style="color:#ff6b7d;font-weight:700;">@${username}</a> (Admin).</div>`;
}

function setChatControlVisible(control, visible) {
	if (!control) return;
	control.classList.toggle('d-none', !visible);
	control.style.setProperty('display', visible ? 'inline-flex' : 'none', 'important');
}

function populateGroup(group, message) {
	group.dataset.userId = String(message.user_id);
	const userlink = group.querySelector('.userlink');
	const username = group.querySelector('.chat-username');
	const avatar = group.querySelector('.avatar-pic');
	const hat = group.querySelector('.avatar-hat');
	const userId = group.querySelector('.user_id');
	const adminIcon = group.querySelector('.chat-admin-icon');
	if (userlink) {
		userlink.href = `/@${encodeURIComponent(message.username)}`;
		userlink.style.color = `#${message.namecolor || 'ffffff'}`;
		userlink.classList.toggle('chat-admin-user', Boolean(message.distinguish_by));
	}
	if (username) {
		username.textContent = message.username;
		const distinguished = Boolean(message.distinguish_by);
		const patron = Boolean(message.patron) && !distinguished;
		username.classList.toggle('mod', distinguished);
		username.classList.toggle('patron', patron);
		if (patron) username.style.backgroundColor = '#' + (message.namecolor || 'ffffff');
		else username.style.removeProperty('background-color');
	}
	if (avatar) avatar.src = `/pp/${message.user_id}`;
	if (hat) {
		if (message.hat) hat.src = `${message.hat}?h=7`;
		else hat.removeAttribute('src');
	}
	if (userId) userId.value = message.user_id;
	if (adminIcon) adminIcon.classList.toggle('d-none', !message.distinguish_by);
	updateChatTime(group.querySelector('.time'), message);
}

function populateLine(line, message) {
	line.id = String(message.id);
	line.classList.toggle('chat-mention', String(message.text_html || '').includes(`/id/${vid}`));
	line.classList.toggle('chat-admin-message', Boolean(message.distinguish_by));
	line.classList.toggle('chat-distinguished', Boolean(message.distinguish_by));
	line.classList.toggle('chat-removed', Boolean(message.removed_by));

	const messageElement = line.querySelector('.chat-message');
	const rawText = line.querySelector('.text');
	const quoteElement = line.querySelector('.quotes');
	const quoteLink = line.querySelector('.QuotedMessageLink');
	const quoteUser = line.querySelector('.QuotedUser');
	const quoteText = line.querySelector('.QuotedMessage');
	const bodyHtml = renderChatBody(message);
	const showRemovedOriginal = Boolean(
		message.removed_by
		&& (message.viewer_can_see_removed || canModerateChat)
		&& bodyHtml.trim()
	);

	if (rawText) rawText.textContent = message.text || '';
	line.classList.toggle('chat-removed-with-original', showRemovedOriginal);
	if (message.removed_by) {
		messageElement.innerHTML = showRemovedOriginal
			? `<div class="chat-removed-original">${bodyHtml}</div>${removalNoticeHtml(message, true)}`
			: removalNoticeHtml(message, false);
	} else {
		messageElement.innerHTML = bodyHtml;
	}
	if (message.quotes && chatState.messages.has(String(message.quotes))) {
		const quoted = chatState.messages.get(String(message.quotes));
		quoteElement.classList.remove('d-none');
		quoteLink.href = `#${quoted.id}`;
		quoteUser.textContent = quoted.username;
		quoteText.textContent = quoted.text || '[removed]';
	} else {
		quoteElement.classList.add('d-none');
		quoteLink.removeAttribute('href');
		quoteUser.textContent = '';
		quoteText.textContent = '';
	}

	const deleteButton = line.querySelector('.del:not(.delmsg)');
	const deleteConfirmButton = line.querySelector('.delmsg');
	const quoteButton = line.querySelector('.quote');
	if (message.removed_by) {
		setChatControlVisible(deleteButton, false);
		setChatControlVisible(deleteConfirmButton, false);
		setChatControlVisible(quoteButton, false);
	} else {
		setChatControlVisible(deleteButton, true);
		setChatControlVisible(deleteConfirmButton, false);
		setChatControlVisible(quoteButton, true);
	}
	line.dataset.messageId = message.id;
}

function buildGroup(message) {
	const group = chatgroupTemplate.cloneNode(true);
	populateGroup(group, message);
	return group;
}

function buildLine(message) {
	const line = chatlineTemplate.cloneNode(true);
	populateLine(line, message);
	return line;
}

function sortedMessages() {
	return [...chatState.messages.values()].sort((a, b) => Number(a.id) - Number(b.id));
}

function updateLoadMoreButton() {
	if (!loadMoreButton) return;
	const atTop = box.scrollTop < 80;
	const filtered = chatState.filters && !filtersAreEmpty(chatState.filters);
	const visible = atTop && chatState.hasMoreHistory && !filtered;
	loadMoreButton.classList.toggle('d-none', !visible);
	loadMoreButton.disabled = chatState.loadingHistory;
	loadMoreButton.textContent = chatState.loadingHistory ? 'Loading messages...' : 'Load more messages';
}

function renderAll() {
	const fragment = document.createDocumentFragment();
	let currentGroup = null;
	for (const message of sortedMessages()) {
		if (!currentGroup || currentGroup.dataset.userId !== String(message.user_id)) {
			currentGroup = buildGroup(message);
			fragment.appendChild(currentGroup);
		}
		currentGroup.appendChild(buildLine(message));
	}
	box.replaceChildren(fragment);
	if (typeof bs_trigger === 'function') bs_trigger(box);
	updateLoadMoreButton();
}

function scrollToBottom() {
	box.scrollTop = box.scrollHeight;
}

function isAtBottom() {
	return box.scrollHeight - box.scrollTop - box.clientHeight < 80;
}

function flash() {
	const title = document.querySelector('title');
	const icon = document.querySelector("link[rel~='icon']");
	if (notifs >= 1 && !focused) {
		if (title) title.textContent = `[+${notifs}] Chat`;
		if (icon) {
			icon.href = alertIcon ? `/i/${siteName}/alert.ico?v=3009` : `/i/${siteName}/icon.webp?v=3009`;
			alertIcon = !alertIcon;
		}
		setTimeout(flash, 500);
	} else {
		if (icon) icon.href = `/i/${siteName}/icon.webp?v=3009`;
		if (title) title.textContent = 'Chat';
		notifs = 0;
	}
	if (isTyping) {
		isTyping = false;
		socket.emit('typing', false);
	}
}

function clearComposer() {
	textbox.value = '';
	textbox.style.height = 'auto';
	isTyping = false;
	socket.emit('typing', false);
	document.getElementById('quotes').classList.add('d-none');
	document.getElementById('quotes_id').value = '';
	document.getElementById('filename').innerHTML = '<i class="fas fa-image"></i>';
	fileInput.value = '';
}

function send() {
	const text = textbox.value.trim();
	const files = fileInput.files;
	if ((!text && !files.length) || !socket.connected) return;
	sendButton.disabled = true;
	socket.emit('speak', {
		message: text,
		quotes: document.getElementById('quotes_id').value,
		file: files.length ? files[0] : '',
		distinguished: Boolean(document.getElementById('chat-send-official')?.checked),
	});
	clearComposer();
	setTimeout(() => { sendButton.disabled = false; }, 250);
	scrollToBottom();
}

function quote(button) {
	const line = button.closest('.chat-line');
	const message = chatState.messages.get(String(line?.id));
	if (!message) return;
	document.getElementById('quotes').classList.remove('d-none');
	document.getElementById('QuotedMessage').textContent = (message.text || '').split('\n').pop();
	document.getElementById('QuotedUser').textContent = message.username;
	document.getElementById('quotes_id').value = message.id;
	document.getElementById('QuotedMessageLink').href = `#${message.id}`;
	textbox.focus();
}

function del(button) {
	const line = button.closest('.chat-line');
	if (!line?.id) return;
	pendingDelete = line.id;
	socket.emit('delete', line.id);
}

function collectFilters() {
	const author = document.getElementById('chat-filter-author');
	const keyword = document.getElementById('chat-filter-keyword');
	const mentions = document.getElementById('chat-filter-mentions');
	const attachment = document.getElementById('chat-filter-attachment');
	const fromInput = document.getElementById('chat-filter-from');
	const toInput = document.getElementById('chat-filter-to');
	if (!author || !keyword || !mentions || !attachment || !fromInput || !toInput) return {};
	const from = fromInput.valueAsNumber;
	const to = toInput.valueAsNumber;
	return {
		author: author.value.trim(),
		keyword: keyword.value.trim(),
		mentions: mentions.value.trim(),
		has_attachment: attachment.checked,
		from_ts: Number.isFinite(from) ? Math.floor(from / 1000) : '',
		to_ts: Number.isFinite(to) ? Math.floor(to / 1000) : '',
	};
}

function filtersAreEmpty(filters) {
	return !filters.author && !filters.keyword && !filters.mentions && !filters.has_attachment && !filters.from_ts && !filters.to_ts;
}

function applyFilters() {
	const summary = document.getElementById('chat-filter-summary');
	chatState.filters = collectFilters();
	if (filtersAreEmpty(chatState.filters)) chatState.filters = {};
	if (summary) summary.textContent = filtersAreEmpty(chatState.filters) ? 'Recent public chat' : 'Filtered chat history';
	chatState.loadingHistory = true;
	socket.emit('history', {filters: chatState.filters, limit: 100});
}

function clearFilters() {
	for (const input of document.querySelectorAll('#chat-filters input')) {
		if (input.type === 'checkbox') input.checked = false;
		else input.value = '';
	}
	chatState.filters = {};
	const summary = document.getElementById('chat-filter-summary');
	if (summary) summary.textContent = 'Recent public chat';
	chatState.loadingHistory = true;
	socket.emit('history', {filters: {}, limit: 100});
}

function loadOlderMessages() {
	if (chatState.loadingHistory || !chatState.hasMoreHistory || chatState.filters && !filtersAreEmpty(chatState.filters)) return;
	const first = box.querySelector('.chat-line');
	const before = Number(first?.id);
	if (!Number.isInteger(before) || before < 1) return;
	chatState.loadingHistory = true;
	updateLoadMoreButton();
	socket.emit('history', {before, limit: 100});
}

function requestOlderMessages() {
	updateLoadMoreButton();
}

function jumpToHash() {
	const target = Number(window.location.hash.slice(1));
	if (!Number.isInteger(target) || target < 1) return;
	if (chatState.messages.has(String(target))) {
		setTimeout(() => document.getElementById(String(target))?.scrollIntoView({block: 'center'}), 50);
		return;
	}
	chatState.pendingAround = target;
	chatState.loadingHistory = true;
	socket.emit('history', {around: target, limit: 50});
}

socket.on('connect', () => {
	setChatStatus('');
	jumpToHash();
});

socket.on('disconnect', () => setChatStatus('Reconnecting…'));
socket.on('connect_error', () => setChatStatus('Chat connection unavailable', true));
socket.on('chat_error', message => setChatStatus(message, true));

socket.on('speak', message => {
	const wasAtBottom = isAtBottom();
	if (chatState.messages.has(String(message.id))) return;
	chatState.messages.set(String(message.id), message);
	notifs += 1;
	if (notifs === 1) setTimeout(flash, 500);
	renderAll();
	if (wasAtBottom || Number(message.user_id) === vid) scrollToBottom();
});

socket.on('history', result => {
	const mode = result.mode || 'replace';
	const oldHeight = box.scrollHeight;
	const oldTop = box.scrollTop;
	if (mode === 'replace' || mode === 'filter' || mode === 'around') chatState.messages.clear();
	for (const message of result.messages || []) chatState.messages.set(String(message.id), message);
	chatState.hasMoreHistory = Boolean(result.has_more);
	chatState.loadingHistory = false;
	renderAll();
	if (mode === 'prepend') box.scrollTop = box.scrollHeight - oldHeight + oldTop;
	else if (mode === 'around' && chatState.pendingAround) {
		const target = chatState.pendingAround;
		chatState.pendingAround = null;
		setTimeout(() => document.getElementById(String(target))?.scrollIntoView({block: 'center'}), 50);
	} else if (mode === 'filter' || mode === 'replace') scrollToBottom();
	updateLoadMoreButton();
});

socket.on('delete', data => {
	const message = chatState.messages.get(String(data.id));
	if (!message) return;
	message.removed_by = data.removed_by;
	message.removed_by_id = data.removed_by_id;
	message.viewer_can_see_removed = canModerateChat;
	if (!canModerateChat) {
		message.text = '';
		message.text_html = '';
		message.text_censored = '';
	}
	chatState.messages.set(String(data.id), message);
	renderAll();
});

socket.on('online', data => {
	const users = data[0] || [];
	document.querySelectorAll('.board-chat-count').forEach(element => element.textContent = users.length);
	let online = '';
	for (const user of users) {
		const username = chatEscapeHtml(user[0]);
		const patron = Boolean(user[3]);
		online += '<li>';
		if (adminLevel && data[1] && Object.keys(data[1]).includes(String(user[0]).toLowerCase())) online += '<b class="text-danger muted">X</b> ';
		const usernameMarkup = patron ? `<span class="patron" style="background-color:#${chatEscapeHtml(user[2])}">${username}</span>` : username;
		online += `<a class="font-weight-bold" target="_blank" href="/@${encodeURIComponent(user[0])}" style="color:#${chatEscapeHtml(user[2])}"><img loading="lazy" class="mr-1" src="/pp/${Number(user[1])}">${usernameMarkup}</a></li>`;
	}
	const onlineElement = document.getElementById('online');
	if (onlineElement) onlineElement.innerHTML = online;
	const mobileOnlineElement = document.getElementById('online-mobile');
	if (mobileOnlineElement) mobileOnlineElement.innerHTML = online;
});

function closeMobileOnline() {
	if (!mobileOnlinePanel || !onlineTrigger) return;
	mobileOnlinePanel.classList.remove('is-open');
	mobileOnlinePanel.setAttribute('aria-hidden', 'true');
	onlineTrigger.setAttribute('aria-expanded', 'false');
}

onlineTrigger?.addEventListener('click', event => {
	if (!window.matchMedia('(max-width: 991.98px)').matches || !mobileOnlinePanel) return;
	event.preventDefault();
	const open = !mobileOnlinePanel.classList.contains('is-open');
	mobileOnlinePanel.classList.toggle('is-open', open);
	mobileOnlinePanel.setAttribute('aria-hidden', String(!open));
	onlineTrigger.setAttribute('aria-expanded', String(open));
});

mobileOnlinePanel?.querySelector('.chat-mobile-online-close')?.addEventListener('click', closeMobileOnline);

socket.on('typing', users => {
	const typingIndicator = document.getElementById('typing-indicator');
	const loadingIndicator = document.getElementById('loading-indicator');
	if (!users.length) {
		typingIndicator.textContent = '';
		loadingIndicator.classList.add('d-none');
	} else {
		typingIndicator.innerHTML = users.length === 1 ? `<b>${chatEscapeHtml(users[0])}</b> is typing…` : `<b>${chatEscapeHtml(users[0])}</b> and <b>${chatEscapeHtml(users[1])}</b> are typing…`;
		loadingIndicator.classList.remove('d-none');
	}
});

document.addEventListener('click', event => {
	if (mobileOnlinePanel?.classList.contains('is-open') && !event.target.closest('#mobile-online-panel, #online2')) {
		closeMobileOnline();
	}
	const quoteButton = event.target.closest('.quote');
	if (quoteButton) return quote(quoteButton);
	const deleteButton = event.target.closest('.delmsg');
	if (deleteButton) return del(deleteButton);
	const confirmButton = event.target.closest('.del:not(.delmsg)');
	if (confirmButton) {
		const parent = confirmButton.parentElement;
		setChatControlVisible(parent.querySelector('.delmsg'), true);
		setChatControlVisible(confirmButton, false);
		return;
	}
	if (event.target.id === 'cancel') {
		document.getElementById('quotes').classList.add('d-none');
		document.getElementById('quotes_id').value = '';
	}
});

document.addEventListener('keydown', event => {
	if (event.key === 'Escape' && mobileOnlinePanel?.classList.contains('is-open')) closeMobileOnline();
});

textbox.addEventListener('keydown', event => {
	if (event.key === 'ArrowDown' && mentionState.items.length) {
		event.preventDefault();
		mentionState.index = Math.min(mentionState.index + 1, mentionState.items.length - 1);
		renderMentionSuggestions();
		return;
	}
	if (event.key === 'ArrowUp' && mentionState.items.length) {
		event.preventDefault();
		mentionState.index = Math.max(mentionState.index - 1, 0);
		renderMentionSuggestions();
		return;
	}
	if (event.key === 'Escape' && mentionState.items.length) {
		event.preventDefault();
		hideMentionSuggestions();
		return;
	}
	if (event.key === 'Enter' && mentionState.items.length && mentionState.index >= 0) {
		event.preventDefault();
		selectMention(mentionState.items[mentionState.index]);
		return;
	}
	if (event.key === 'Enter' && !event.shiftKey) {
		event.preventDefault();
		send();
	}
});

textbox.addEventListener('input', () => {
	void updateMentionSuggestions();
	textbox.style.height = 'auto';
	textbox.style.height = `${Math.min(textbox.scrollHeight, 160)}px`;
	const hasText = Boolean(textbox.value.trim());
	if (!hasText && isTyping) {
		isTyping = false;
		socket.emit('typing', false);
	} else if (hasText && !isTyping) {
		isTyping = true;
		socket.emit('typing', true);
	}
});

fileInput.addEventListener('change', () => {
	const file = fileInput.files[0];
	document.getElementById('filename').textContent = file ? file.name : '';
});

document.addEventListener('paste', event => {
	if (!event.clipboardData?.files?.length || typeof DataTransfer === 'undefined') return;
	const transfer = new DataTransfer();
	for (const file of event.clipboardData.files) transfer.items.add(file);
	fileInput.files = transfer.files;
	document.getElementById('filename').textContent = transfer.files[0]?.name || '';
});

function hideMentionSuggestions() {
	mentionState.items = [];
	mentionState.index = -1;
	mentionState.token = null;
	if (mentionSuggestions) {
		mentionSuggestions.classList.add('d-none');
		mentionSuggestions.replaceChildren();
	}
}

function positionMentionSuggestions() {
	if (!mentionSuggestions || mentionSuggestions.classList.contains('d-none')) return;
	const rect = textbox.getBoundingClientRect();
	mentionSuggestions.style.position = 'fixed';
	mentionSuggestions.style.left = Math.max(8, rect.left) + 'px';
	mentionSuggestions.style.bottom = Math.max(8, window.innerHeight - rect.top + 6) + 'px';
}

function renderMentionSuggestions() {
	if (!mentionSuggestions) return;
	mentionSuggestions.replaceChildren();
	if (!mentionState.items.length) {
		mentionSuggestions.classList.add('d-none');
		return;
	}
	mentionState.items.forEach((item, index) => {
		const button = document.createElement('button');
		button.type = 'button';
		button.className = 'chat-mention-suggestion' + (index === mentionState.index ? ' active' : '');
		button.dataset.username = item.username;
		button.setAttribute('role', 'option');
		button.setAttribute('aria-selected', String(index === mentionState.index));
		button.textContent = '@' + item.username;
		mentionSuggestions.appendChild(button);
	});
	mentionSuggestions.classList.remove('d-none');
	positionMentionSuggestions();
}

async function updateMentionSuggestions() {
	const cursor = textbox.selectionStart;
	const before = textbox.value.slice(0, cursor);
	const match = before.match(/(^|[\s])@([A-Za-z0-9_-]{1,30})$/);
	if (!match) {
		hideMentionSuggestions();
		return;
	}
	const query = match[2];
	const token = {start: cursor - query.length - 1, end: cursor, query: query};
	mentionState.token = token;
	const request = ++mentionState.request;
	try {
		const response = await fetch('/api/users/suggest?q=' + encodeURIComponent(query), {headers: {'Accept': 'application/json'}});
		if (!response.ok || request !== mentionState.request) return;
		const payload = await response.json();
		mentionState.items = Array.isArray(payload.data) ? payload.data : [];
		mentionState.index = mentionState.items.length ? 0 : -1;
		renderMentionSuggestions();
	} catch (error) {
		if (request === mentionState.request) hideMentionSuggestions();
	}
}

function selectMention(item) {
	const token = mentionState.token;
	if (!token) return;
	const replacement = '@' + item.username + ' ';
	textbox.value = textbox.value.slice(0, token.start) + replacement + textbox.value.slice(token.end);
	const caret = token.start + replacement.length;
	textbox.setSelectionRange(caret, caret);
	hideMentionSuggestions();
	textbox.focus();
	textbox.dispatchEvent(new Event('input', {bubbles: true}));
}
mentionSuggestions?.addEventListener('click', event => {
	const option = event.target.closest('.chat-mention-suggestion');
	if (!option) return;
	const item = mentionState.items.find(entry => entry.username === option.dataset.username);
	if (item) selectMention(item);
});
sendButton.addEventListener('click', send);

loadMoreButton?.addEventListener('click', loadOlderMessages);
const filterToggle = document.getElementById('chat-filter-toggle');
if (filterToggle) {
	filterToggle.addEventListener('click', event => {
		const filters = document.getElementById('chat-filters');
		const open = filters.classList.toggle('d-none') === false;
		event.currentTarget.setAttribute('aria-expanded', String(open));
	});
	document.getElementById('chat-filter-apply')?.addEventListener('click', applyFilters);
	document.getElementById('chat-filter-clear')?.addEventListener('click', clearFilters);
	for (const input of document.querySelectorAll('#chat-filters input')) input.addEventListener('keydown', event => {
		if (event.key === 'Enter') applyFilters();
	});
}

box.addEventListener('scroll', requestOlderMessages);
window.addEventListener('blur', () => { focused = false; });
window.addEventListener('focus', () => { focused = true; });
window.addEventListener('hashchange', jumpToHash);

renderAll();
setTimeout(scrollToBottom, 50);