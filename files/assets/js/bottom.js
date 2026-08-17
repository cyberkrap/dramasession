
function execute(element, attr) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		return
	}
	const funcs = element.getAttribute(`data-${attr}`).split(';')
	for (const func of funcs) {
		if (func) {
			const split = func.split('(')
			const name = split[0]
			const args = split[1].replace(/[')]/g, "").split(',').map(a => a.trim());
			if (args[0] == 'this') args[0] = element
			try {
				window[name](...args);
			}
			catch (e) {
				console.log(e)
				console.log(name)
			}
		}
	}
}

const onsubmit = document.querySelectorAll('[data-onsubmit]');
for (const element of onsubmit) {
	element.addEventListener('submit', (event)=>{
		event.preventDefault();
		execute(element, 'onsubmit')
	});
}

const onfocus = document.querySelectorAll('[data-onfocus]');
for (const element of onfocus) {
	element.addEventListener('focus', () => {execute(element, 'onfocus')});
}

const onclick_submit = document.querySelectorAll('[onclick_submit]');
for (const element of onclick_submit) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.addEventListener('click', () => {element.form.submit()});
}

const onchange_submit = document.querySelectorAll('[onchange_submit]');
for (const element of onchange_submit) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.addEventListener('change', () => {element.form.submit()});
}

const undisable_element = document.querySelectorAll('[data-undisable_element]');
for (const element of undisable_element) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.addEventListener('input', () => {
		document.getElementById(element.dataset.undisable_element).disabled = false;
	});
}

const setting_switchs = document.getElementsByClassName('setting_switch');
for (const element of setting_switchs) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.addEventListener('change', () => {
		postToastSwitch(element,`/settings/personal?${element.name}=${element.checked}`);
	});
}

const setting_selects = document.getElementsByClassName('setting_select');
for (const element of setting_selects) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.addEventListener('change', () => {
		if (element.dataset.reload)
			postToastReload(element,`/settings/personal?${element.name}=${element.value}`);
		else
			postToast(element,`/settings/personal?${element.name}=${element.value}`);
	});
}

const reload_page = document.getElementById('reload_page')
if (reload_page) {
	reload_page.addEventListener('click', () => {location.reload()});
}

const TH = document.getElementsByTagName('th')
for (const element of TH) {
	if (element.classList.contains("disable-sort-click"))
                continue;

	element.addEventListener('click', () => {sort_table(element)});
}

function register_new_elements(e) {
	const showmores = document.getElementsByClassName('showmore')
	for (const element of showmores) {
		element.onclick = () => {showmore(element)};
	}
	
	const onclick = e.querySelectorAll('[data-onclick]');
	for (const element of onclick) {
		element.onclick = () => {execute(element, 'onclick')};
	}

	const oninput = e.querySelectorAll('[data-oninput]');
	for (const element of oninput) {
		element.oninput = () => {execute(element, 'oninput')};
	}

	const onmouseover = e.querySelectorAll('[data-onmouseover]');
	for (const element of onmouseover) {
		element.onmouseover = () => {execute(element, 'onmouseover')};
	}

	const onchange = e.querySelectorAll('[data-onchange]');
	for (const element of onchange) {
		element.onchange = () => {execute(element, 'onchange')};
	}

	const expandable = document.querySelectorAll('.in-comment-image, img[alt^="![]("]');
	for (const element of expandable) {
		element.onclick = () => {expandImage()};
	}

	const toggleelement = e.querySelectorAll('[data-toggleelement]');
	for (const element of toggleelement) {
		element.addEventListener('click', () => {
			document.getElementById(element.dataset.toggleelement).classList.toggle(element.dataset.toggleattr);
		});
	}

}

function moveMobileActionModalsToBody(root) {
    const scope = root && root.querySelectorAll ? root : document;
    const selector = '.modal.d-md-none[id^="actionsModal"], .modal.d-md-none[id^="adminModal-"], .modal.d-md-none[id^="commentActionsModal-"], .modal.d-md-none[id^="commentAdminModal-"]';
    const modals = [];
    if (scope.matches && scope.matches(selector)) modals.push(scope);
    scope.querySelectorAll(selector).forEach(modal => modals.push(modal));
    modals.forEach(modal => {
        if (modal.parentElement !== document.body) {
            document.body.appendChild(modal);
        }
    });
}

/* Inline image composers have a dedicated Image URL button. A normal pasted
   http(s) link must stay ordinary text instead of being sent to the image
   importer. Clipboard image files still use the existing paste-upload path. */
function preservePlainUrlPaste(event) {
	const textarea = event.target;
	if (!(textarea instanceof HTMLTextAreaElement) || !textarea.closest('.inline-image-composer')) return;
	const clipboard = event.clipboardData;
	if (!clipboard) return;
	if (Array.from(clipboard.files || []).some(file => String(file.type || '').startsWith('image/'))) return;

	const pasted = clipboard.getData('text/plain') || '';
	if (!/^https?:\/\/\S+$/i.test(pasted.trim())) return;

	event.preventDefault();
	event.stopImmediatePropagation();
	const start = Number.isInteger(textarea.selectionStart) ? textarea.selectionStart : textarea.value.length;
	const end = Number.isInteger(textarea.selectionEnd) ? textarea.selectionEnd : start;
	textarea.setRangeText(pasted, start, end, 'end');
	textarea.dispatchEvent(new Event('input', {bubbles: true}));
}

document.addEventListener('paste', preservePlainUrlPaste, true);

moveMobileActionModalsToBody(document);
const mobileModalObserver = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
        mutation.addedNodes.forEach(node => {
            if (node.nodeType === Node.ELEMENT_NODE) {
                moveMobileActionModalsToBody(node);
            }
        });
    });
});
mobileModalObserver.observe(document.body, { childList: true, subtree: true });

register_new_elements(document);
bs_trigger(document);