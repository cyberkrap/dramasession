marked.use({
	extensions: [
		{
			name: 'mention',
			level: 'inline',
			start: function(src){
				const match = src.match(/@[a-zA-Z0-9_\-]+/);
				return match != null ? match.index : -1;
			},
			tokenizer: function(src) {
				const rule = /^@[a-zA-Z0-9_\-]+/;
				const match = rule.exec(src);
				if(match){
					return {
						type: 'mention',
						raw: match[0],
						text: match[0].trim().slice(1),
						tokens: []
					};
				}
			},
			renderer(token) {
				const u = token.raw;
				return `<a href="/${u}"><img loading="lazy" src="/${u}/pic" class="pp20"> ${u}</a>`;
			}
		}
	]
});

const reDisableBeforeUnload = /^\/submit|^\/h\/[a-zA-Z0-9_\-]{3,20}\/submit/;

function markdown(t) {
	let input = t.value;

	if (!reDisableBeforeUnload.test(location.pathname))
	{
		if (!window.onbeforeunload)
		{
			window.onbeforeunload = function (e) {
				e = e || window.event;
				if (e) {
					e.returnValue = 'Any string';
				}
				return 'Any string';
			};
		}
		else if (!input) {
			window.onbeforeunload = null
		}
	}

	if (!input.includes('```') && !input.includes('<pre>'))
		input = input.replace(/\n/g, '\n\n')
	input = input.replace(/\|\|(.*?)\|\|/g, '<spoiler>$1</spoiler>')
	input = input.replace(/(\n|^)>([^ >][^\n]*)/g, '$1<g>\>$2</g>')

	const emojis = Array.from(input.matchAll(/:([a-z0-9_\-!#@]{1,36}):(?![^`]*`)/gi))
	if(emojis != null){
		for(i = 0; i < emojis.length; i++){
			const old = emojis[i][0];
			if (old.includes('marseyrandom')) continue
			let emoji = old.replace(/[:!@#]/g,'').toLowerCase();
			const mirroredClass = old.indexOf('!') == -1 ? '' : 'mirrored';
			const emojiClass = old.indexOf('#') == -1 ? 'emoji' : 'emoji-lg';
			if (emoji.endsWith('pat') && emoji != 'marseyunpettablepat') {
				emoji = emoji.substr(0, emoji.length - 3);
				const url = old.indexOf('@') != -1 ? `/@${emoji}/pic` : `/e/${emoji}.webp`;
				input = input.replace(old, `<span class="pat-preview ${mirroredClass}" data-bs-toggle="tooltip"><img loading="lazy" src="/i/hand.webp"><img loading="lazy" class="${emojiClass}" src="${url}"></span>`);
			} else {
				input = input.replace(old, `<img loading="lazy" class="${emojiClass} ${mirroredClass}" src="/e/${emoji}.webp">`);
			}
		}
	}

	let options = Array.from(input.matchAll(/\$\$([^\$\n]+)\$\$(?![^`]*`)/gi))
	if(options != null){
		for(i = 0; i < options.length; i++){
			const option = options[i][0];
			const option2 = option.replace(/\$\$/g, '').replace(/\n/g, '')
			input = input.replace(option, '');
			input += `<div class="custom-control"><input type="checkbox" class="custom-control-input" id="option-${i}"><label class="custom-control-label" for="option-${i}">${option2} - <a>0 votes</a></label></div>`;
		}
	}

	options = Array.from(input.matchAll(/&&([^&\n]+)&&(?![^`]*`)/gi))
	if(options != null){
		for(i = 0; i < options.length; i++){
			const option = options[i][0];
			const option2 = option.replace(/&&/g, '').replace(/\n/g, '')
			input = input.replace(option, '');
			input += `<div class="custom-control"><input type="radio" name="choice" class="custom-control-input" id="option-${i}"><label class="custom-control-label" for="option-${i}">${option2} - <a>0 votes</a></label></div>`;
		}
	}

	input = marked(input)
	input = input.replace(/\n\n/g, '<br>')

	const preview = document.getElementById(t.dataset.preview)

	preview.innerHTML = input

	const expandable = preview.querySelectorAll('img[alt]');
	for (const element of expandable) {
		element.onclick = () => {expandImage()};
	}
}

function charLimit(form, text) {

	const input = document.getElementById(form);

	text = document.getElementById(text);

	const length = input.value.length;

	const maxLength = input.getAttribute("maxlength");

	if (length >= maxLength) {
		text.style.color = "#E53E3E";
	}
	else if (length >= maxLength * .72){
		text.style.color = "#FFC107";
	}
	else {
		text.style.color = "#A0AEC0";
	}

	text.innerText = length + ' / ' + maxLength;
}

function remove_dialog() {
	window.onbeforeunload = null;
}
