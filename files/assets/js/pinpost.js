function pinPost(t, id) {
	postToast(t, `/sticky/${id}`,
		{
		},
		(xhr) => {
			if(xhr.status == 201) {
				t.innerHTML = t.innerHTML.replace(t.textContent, 'Pin for 1 hour');
				t.classList.add('d-none');
			} else {
				t.innerHTML = t.innerHTML.replace(t.textContent, 'Pin permanently');
			}
			t.nextElementSibling.classList.remove('d-none');
		}
	);
}

function unpinPost(t, id) {
	postToast(t, `/unsticky/${id}`,
		{
		},
		() => {
			t.classList.add('d-none');
			const prev = t.previousElementSibling;
			prev.innerHTML = prev.innerHTML.replace(prev.textContent, 'Pin for 1 hour');
			prev.classList.remove('d-none');
		}
	);
}
