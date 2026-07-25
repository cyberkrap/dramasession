def install_chat_presence_fix(chat_module):
	if getattr(chat_module, '_live_presence_fix_installed', False):
		return

	@chat_module.socketio.on('disconnect')
	@chat_module.chat_access_required
	def disconnect_with_live_presence(v):
		for item in chat_module.online[:]:
			if item[:2] == [v.username, v.id]:
				chat_module.online.remove(item)
				break
		chat_module.refresh_online()
		if v.username in chat_module.typing:
			chat_module.typing.remove(v.username)
			chat_module.emit('typing', chat_module.typing, broadcast=True)
		return '', 204

	chat_module._live_presence_fix_installed = True
