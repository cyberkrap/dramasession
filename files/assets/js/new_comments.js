const comments = JSON.parse(localStorage.getItem("comment-counts")) || {}
let pid
let pcc

for (let twoattrs of document.getElementsByClassName("twoattrs")) {
	twoattrs = twoattrs.value.split(',')
	pid = twoattrs[0]
	pcc = twoattrs[1]
	const lastCount = comments[pid]
	if (lastCount) {
		const newComments = pcc - lastCount.c
		if (newComments > 0) {
			elems = document.getElementsByClassName(`${pid}-new-comments`)
			for (const elem of elems)
			{
				elem.textContent = ` (+${newComments})`
				elem.classList.remove("d-none")
			}
		}
	}
}

const LAST_CACHE_CLEAN_ID = "last-cache-clean"
const EXPIRE_INTERVAL_MILLIS = 5 * 24 * 60 * 60 * 1000
const CACHE_CLEAN_INTERVAL = 60 * 60 * 1000

function cleanCache() {
	const lastCacheClean = JSON.parse(localStorage.getItem(LAST_CACHE_CLEAN_ID)) || Date.now()
	const now = Date.now()

	if (now - lastCacheClean > CACHE_CLEAN_INTERVAL) {
		const comments = JSON.parse(localStorage.getItem("comment-counts")) || {}

		for (let [key, value] of Object.entries(comments)) {
			if (now - value.t > EXPIRE_INTERVAL_MILLIS) {
				delete comments[key]
			}
		}
		localStorage.setItem("comment-counts", JSON.stringify(comments))
	}
	localStorage.setItem(LAST_CACHE_CLEAN_ID, JSON.stringify(now))
}

setTimeout(cleanCache, 500)
