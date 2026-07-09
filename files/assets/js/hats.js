function equip_hat(t, hat_id, hat_name) {
	const profile_pic_hat = document.getElementById("profile-pic-35-hat");
	function extra_actions(xhr) {
		if(xhr.status == 200) {
			profile_pic_hat.src = `/i/hats/${hat_name}.webp?h=7`
			profile_pic_hat.classList.remove('d-none')
		}
	}

	postToastSwitch(t, `/equip_hat/${hat_id}`, `equip-${hat_id}`, `unequip-${hat_id}`, `d-none`, extra_actions)
}
