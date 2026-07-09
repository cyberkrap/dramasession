function timeSince(timeStamp) {
	const now = new Date(),
		secondsPast = (now.getTime() - timeStamp) / 1000;
	if (secondsPast < 60) {
		return parseInt(secondsPast) + 's';
	}
	if (secondsPast < 3600) {
		return parseInt(secondsPast / 60) + 'm';
	}
	if (secondsPast <= 86400) {
		return parseInt(secondsPast / 3600) + 'h';
	}
	if (secondsPast > 86400) {
		day = timeStamp.getDate();
		month = timeStamp.toDateString().match(/ [a-zA-Z]*/)[0].replace(" ", "");
		year = timeStamp.getFullYear() == now.getFullYear() ? "" : " " + timeStamp.getFullYear();
		return day + " " + month + year;
	}
}

const ua=window.navigator.userAgent
let socket

socket=io()

const chatline = document.getElementsByClassName('chat-line')[0]
const box = document.getElementById('chat-window')
const textbox = document.getElementById('input-text')
const icon = document.querySelector("link[rel~='icon']")

const vid = document.getElementById('vid').value
const site_name = document.getElementById('site_name').value
const slurreplacer = document.getElementById('slurreplacer').value

let notifs = 0;
let focused = true;
let is_typing = false;
let alert=true;

function flash(){
	let title = document.getElementsByTagName('title')[0]
	if (notifs >= 1 && !focused){
		title.innerHTML = `[+${notifs}] Chat`;
		if (alert) {
			icon.href = `/i/${site_name}/alert.ico?v=3009`
			alert=false;
		}
		else {
			icon.href = `/i/${site_name}/icon.webp?v=3009`
			alert=true;
		}
		setTimeout(flash, 500)
	}
	else {
		icon.href = `/i/${site_name}/icon.webp?v=3009`
		notifs = 0
		title.innerHTML = 'Chat';
	}

	if (is_typing) {
		is_typing = false
		socket.emit('typing', false);
	}
}


socket.on('speak', function(json) {
	let text = json['text']
	let text_html

	if (slurreplacer != '0') text_html = json['text_censored']
	else text_html = json['text_html']

	chatline.classList.remove('chat-mention');
	if (text_html.includes(`<a href="/id/${vid}">`)){
		chatline.classList.add('chat-mention');
	}

	notifs = notifs + 1;
	if (notifs == 1) {
		setTimeout(flash, 500);
	}

	const users = document.getElementsByClassName('user_id');
	const last_user = users[users.length-1].value;
	const scrolled_down = (box.scrollHeight - box.scrollTop <= window.innerHeight)

	if (last_user != json['user_id']) {
		document.getElementsByClassName('avatar-pic')[0].src = '/pp/' + json["user_id"]

		if (json['hat'])
			document.getElementsByClassName('avatar-hat')[0].src = json['hat'] + "?h=7"
		else
			document.getElementsByClassName('avatar-hat')[0].removeAttribute("src")

		const userlink = document.getElementsByClassName('userlink')[0]

		userlink.innerHTML = userlink.innerHTML.replace(userlink.textContent, json['username'])
		userlink.href = '/@' + json['username']
		userlink.style.color = '#' + json['namecolor']

		document.getElementsByClassName('user_id')[0].value = json['user_id']

		if (Date.now() - json['time']*1000 > 5000)
			document.getElementsByClassName('time')[0].innerHTML = timeSince(json['time']*1000) + ' ago'
		else
			document.getElementsByClassName('time')[0].innerHTML = "just now"
	}

	document.getElementsByClassName('chat-line')[0].id = json['id']
	document.getElementsByClassName('text')[0].innerHTML = escapeHTML(text)
	document.getElementsByClassName('chat-message')[0].innerHTML = text_html.replace(/data-src/g, 'src').replace(/data-cfsrc/g, 'src').replace(/style="display:none;visibility:hidden;"/g, '')

	document.getElementsByClassName('quotes')[0].classList.add("d-none")
	if (json['quotes']) {
		const quoted = document.getElementById(json['quotes'])
		if (quoted) {
			const quoted_user = quoted.parentElement.querySelector('.user_id').value
			if (quoted_user == vid){
				chatline.classList.add('chat-mention');
			}
			document.getElementsByClassName('quotes')[0].classList.remove("d-none")
			document.getElementsByClassName('QuotedMessageLink')[0].href = '#' + json['quotes']
			document.getElementsByClassName('QuotedUser')[0].innerHTML = quoted.parentElement.querySelector('.userlink').textContent
			document.getElementsByClassName('QuotedMessage')[0].innerHTML = quoted.querySelector('.text').innerHTML
		}
	}

	let line = document.getElementsByClassName('chat-line')[0].cloneNode(true)
	register_new_elements(line);
	bs_trigger(line)
	if (last_user == json['user_id']) {
		box.querySelector('.chat-group:last-child').append(line)
	}
	else {
		const chatgroup = document.getElementsByClassName('chat-group')[0].cloneNode(true)
		chatgroup.append(line)
		box.append(chatgroup)
	}

	if (scrolled_down || json['user_id'] == vid)
		box.scrollTo(0, box.scrollHeight)
})

function send() {
	const text = textbox.value.trim()
	const files = document.getElementById('file').files
	if (text || files)
	{
		let sending;
		if (files[0]) sending = files[0]
		else sending = ''
		socket.emit('speak', {
			"message": text,
			"quotes": document.getElementById('quotes_id').value,
			"file": sending,
		});
		textbox.value = ''
		is_typing = false
		socket.emit('typing', false);
		autoExpand(textbox);
		document.getElementById("quotes").classList.add("d-none")
		document.getElementById('quotes_id').value = null;
		document.getElementById("filename").innerHTML = '<i class="fas fa-image" style="font-size:1.3rem!important"></i>'
		document.getElementById('file').value = null;
		box.scrollTo(0, box.scrollHeight);
		setTimeout(function () {
			box.scrollTo(0, box.scrollHeight)
		}, 200);
	}
}


function quote(t) {
	document.getElementById("quotes").classList.remove("d-none")

	const text = t.parentElement.getElementsByClassName("text")[0].innerHTML.replace(/\*/g,"\\*").split('\n').pop()
	document.getElementById('QuotedMessage').innerHTML = text

	const username = t.parentElement.parentElement.parentElement.parentElement.getElementsByClassName('userlink')[0].textContent
	document.getElementById('QuotedUser').innerHTML = username

	const id = t.parentElement.parentElement.parentElement.id
	document.getElementById('quotes_id').value = id
	document.getElementById('QuotedMessageLink').href = `#${id}`

	textbox.focus()
}

textbox.addEventListener("keyup", function(e) {
	if (e.key === 'Enter') {
		e.preventDefault();
		send();
	}
})

socket.on('online', function(data){
	document.getElementsByClassName('board-chat-count')[0].innerHTML = data[0].length
	const admin_level = parseInt(document.getElementById('admin_level').value)
	let online = ''
	let online2 = '<b>Users Online</b>'
	for (const u of data[0])
	{
		online += `<li>`
		if (admin_level && Object.keys(data[1]).includes(u[0].toLowerCase()))
			online += '<b class="text-danger muted" data-bs-toggle="tooltip" title="Muted">X</b> '
		online += `<a class="font-weight-bold" target="_blank" href="/@${u[0]}" style="color:#${u[2]}"><img loading="lazy" class="mr-1" src="/pp/${u[1]}">${u[0]}</a></li>`
		online2 += `<br>@${u[0]}`
	}
	document.getElementById('online').innerHTML = online
	bs_trigger(document.getElementById('online'))
	document.getElementById('online2').setAttribute("data-bs-original-title", online2);
	document.getElementById('online3').innerHTML = online
	bs_trigger(document.getElementById('online3'))
})

window.addEventListener('blur', function(){
	focused=false
})
window.addEventListener('focus', function(){
	focused=true
})


textbox.addEventListener("input", function() {
	text = textbox.value
	if (!text && is_typing==true){
		is_typing=false;
		socket.emit('typing', false);
	}
	else if (text && is_typing==false) {
		is_typing=true;
		socket.emit('typing', true);
	}
})


socket.on('typing', function (users){
	if (users.length==0){
		document.getElementById('typing-indicator').innerHTML = '';
		document.getElementById('loading-indicator').classList.add('d-none');
	}
	else if (users.length==1){
		document.getElementById('typing-indicator').innerHTML = '<b>'+users[0]+"</b> is typing...";
		document.getElementById('loading-indicator').classList.remove('d-none');
	}
	else if (users.length==2){
		document.getElementById('typing-indicator').innerHTML = '<b>'+users[0]+"</b> and <b>"+users[1]+"</b> are typing...";
		document.getElementById('loading-indicator').classList.remove('d-none');
	}
	else {
		document.getElementById('typing-indicator').innerHTML = '<b>'+users[0]+"</b>, <b>"+users[1]+"</b>, and <b>"+users[2]+"</b> are typing...";
		document.getElementById('loading-indicator').classList.remove('d-none');
	}
})


function del(t) {
	const chatline = t.parentElement.parentElement.parentElement
	socket.emit('delete', chatline.id);
	chatline.remove()
}

socket.on('delete', function(text) {
	const text_spans = document.getElementsByClassName('text')
	for(const span of text_spans) {
		if (span.innerHTML == text)
		{
			span.parentElement.parentElement.parentElement.parentElement.parentElement.remove()
		}
	}
})

document.addEventListener('click', function (e) {
	if (e.target.classList.contains('fa-trash-alt')) {
		e.target.nextElementSibling.classList.remove('d-none');
		e.target.classList.add('d-none');
	}
	else {
		for (const btn of document.querySelectorAll('.delmsg:not(.d-none)')) {
			btn.classList.add('d-none');
			btn.previousElementSibling.classList.remove('d-none');
		}
	}
	
	if (e.target.id == "cancel") {
		document.getElementById("quotes").classList.add("d-none");
		document.getElementById('quotes_id').value = null;
	}
});

document.onpaste = function(event) {
	files = structuredClone(event.clipboardData.files);

	filename = files[0]

	if (filename)
	{
		filename = filename.name.toLowerCase()
		f=document.getElementById('file');
		f.files = files;
		document.getElementById('filename').textContent = filename;
	}
}

box.scrollTo(0, box.scrollHeight)
setTimeout(function () {
	box.scrollTo(0, box.scrollHeight)
}, 200);
setTimeout(function () {
	box.scrollTo(0, box.scrollHeight)
}, 500);
setTimeout(function () {
	box.scrollTo(0, box.scrollHeight)
}, 1000);
setTimeout(function () {
	box.scrollTo(0, box.scrollHeight)
}, 1500);
document.addEventListener('DOMContentLoaded', function () {
	box.scrollTo(0, box.scrollHeight)
});
