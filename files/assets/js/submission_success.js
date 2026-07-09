history.pushState(null, null, `/post/${pid}`);
localStorage.setItem("post-title", "")
localStorage.setItem("post-text", "")
localStorage.setItem("post-url", "")
localStorage.setItem("sub", "")

localStorage.setItem("post-notify", true)
localStorage.setItem("post-new", false)
localStorage.setItem("post-nsfw", false)
localStorage.setItem("post-private", false)
localStorage.setItem("post-ghost", false)
