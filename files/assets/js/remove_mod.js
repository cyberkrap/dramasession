function removeMod(form) {
	sendFormXHR(form,
		() => {
			form.parentElement.parentElement.remove();
		}
	)
}
