document.getElementById('new_email').addEventListener('input', function () {
	document.getElementById("email-password").classList.remove("d-none");
	document.getElementById("email-password-label").classList.remove("d-none");
	document.getElementById("emailpasswordRequired").classList.remove("d-none");
});
const twoStepModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('2faModal'))

function emailVerifyText() {
	document.getElementById("email-verify-text").innerHTML = "Verification email sent! Please check your inbox.";
}

function block_user() {
	const usernameField = document.getElementById("block-username");
	const isValidUsername = usernameField.checkValidity();
	username = usernameField.value;
	if (isValidUsername) {
		const xhr = new XMLHttpRequest();
		xhr.open("post", "/settings/block");
		xhr.setRequestHeader('xhr', 'xhr');
		f=new FormData();
		f.append("username", username);
		f.append("formkey", formkey());
		xhr.onload=function(){
			if (xhr.status<300) {
				location.reload();
			}
			else {
				showToast(false, "Error, please try again later.");
			}
		}
		xhr.send(f)
	}
}

function unblock_user(t, url) {
	postToast(t, url,
		{
		},
		() => {
			t.parentElement.parentElement.remove();
		}
	);
}

document.getElementById('2faToggle').addEventListener('change', () => {twoStepModal.show()})
