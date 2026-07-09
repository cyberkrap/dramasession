function badge_timestamp(t) {
	const date = formatDate(new Date(t.dataset.until*1000));
	const text = t.getAttribute("data-bs-original-title")
	t.setAttribute("data-bs-original-title", `${text} ${date.toString()}`);
	t.removeAttribute("data-onmouseover")
}
