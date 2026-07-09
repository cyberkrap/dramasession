from copy import deepcopy

MODACTION_TYPES = {
	'chud': {
		"str": 'chudded {self.target_link}',
		"icon": 'fa-snooze',
		"color": 'bg-danger'
	},
	'approve_app': {
		"str": 'approved an application by {self.target_link}',
		"icon": 'fa-robot',
		"color": 'bg-success'
	},
	'badge_grant': {
		"str": 'granted badge to {self.target_link}',
		"icon": 'fa-badge',
		"color": 'bg-success'
	},
	'badge_remove': {
		"str": 'removed badge from {self.target_link}',
		"icon": 'fa-badge',
		"color": 'bg-danger'
	},
	'ban_comment': {
		"str": 'removed {self.target_link}',
		"icon": 'fa-comment',
		"color": 'bg-danger'
	},
	'ban_domain': {
		"str": 'banned a domain',
		"icon": 'fa-globe',
		"color": 'bg-danger'
	},
	'ban_post': {
		"str": 'removed post {self.target_link}',
		"icon": 'fa-feather-alt',
		"color": 'bg-danger'
	},
	'ban_user': {
		"str": 'banned user {self.target_link}',
		"icon": 'fa-user-slash',
		"color": 'bg-danger'
	},
	'blacklist_user': {
		"str": 'blacklisted user {self.target_link} from restricted holes',
		"icon": 'fa-lock',
		"color": 'bg-danger'
	},
	'delete_report': {
		"str": 'deleted report on {self.target_link}',
		"icon": 'fa-flag',
		"color": 'bg-danger'
	},
	'disable_bots': {
		"str": 'disabled bots',
		"icon": 'fa-robot',
		"color": 'bg-danger'
	},
	'disable_fart_mode': {
		"str": 'disabled fart mode',
		"icon": 'fa-gas-pump-slash',
		"color": 'bg-danger'
	},
	'disable_read_only_mode': {
		"str": 'disabled read only mode',
		"icon": 'fa-book',
		"color": 'bg-danger'
	},
	'disable_signups': {
		"str": 'disabled signups',
		"icon": 'fa-users',
		"color": 'bg-danger'
	},
	'disable_login_required': {
		"str": 'disabled login required',
		"icon": 'fa-users',
		"color": 'bg-danger'
	},
	'disable_under_attack': {
		"str": 'disabled under attack mode',
		"icon": 'fa-shield',
		"color": 'bg-muted'
	},
	'disable_under_siege': {
		"str": 'disabled under siege mode',
		"icon": 'fa-shield',
		"color": 'bg-muted'
	},
	'disable_dm_images': {
		"str": 'disabled DM images',
		"icon": 'fa-images',
		"color": 'bg-muted'
	},
	'distinguish_comment': {
		"str": 'distinguished {self.target_link}',
		"icon": 'fa-crown',
		"color": 'bg-success'
	},
	'distinguish_post': {
		"str": 'distinguished {self.target_link}',
		"icon": 'fa-crown',
		"color": 'bg-success'
	},
	'distribute': {
		"str": 'distributed bet winnings to voters on {self.target_link}',
		"icon": 'fa-dollar-sign',
		"color": 'bg-success'
	},
	'edit_post': {
		"str": 'edited {self.target_link}',
		"icon": 'fa-edit',
		"color": 'bg-primary'
	},
	'edit_rules': {
		"str": 'edited the rules',
		"icon": 'fa-columns',
		"color": 'bg-primary'
	},
	'enable_bots': {
		"str": 'enabled bots',
		"icon": 'fa-robot',
		"color": 'bg-success'
	},
	'enable_fart_mode': {
		"str": 'enabled fart mode',
		"icon": 'fa-gas-pump',
		"color": 'bg-success'
	},
	'enable_read_only_mode': {
		"str": 'enabled read only mode',
		"icon": 'fa-book',
		"color": 'bg-success'
	},
	'enable_signups': {
		"str": 'enabled signups',
		"icon": 'fa-users',
		"color": 'bg-success'
	},
	'enable_login_required': {
		"str": 'enabled login required',
		"icon": 'fa-users',
		"color": 'bg-success'
	},
	'enable_under_attack': {
		"str": 'enabled under attack mode',
		"icon": 'fa-shield',
		"color": 'bg-success'
	},
	'enable_under_siege': {
		"str": 'enabled under siege mode',
		"icon": 'fa-shield',
		"color": 'bg-success',
	},
	'enable_dm_images': {
		"str": 'enabled DM images',
		"icon": 'fa-images',
		"color": 'bg-success',
	},
	'flair_post': {
		"str": 'set a flair on {self.target_link}',
		"icon": 'fa-tag',
		"color": 'bg-primary'
	},
	'link_accounts': {
		"str": 'linked {self.target_link}',
		"icon": 'fa-link',
		"color": 'bg-success'
	},
	'delink_accounts': {
		"str": 'delinked {self.target_link}',
		"icon": 'fa-link-slash',
		"color": 'bg-danger'
	},
	'make_admin': {
		"str": 'made {self.target_link} an admin',
		"icon": 'fa-user-crown',
		"color": 'bg-success'
	},
	'mod_mute_user': {
		"str": 'muted reports from user {self.target_link}',
		"icon": 'fa-file-signature',
		"color": 'bg-danger'
	},
	'mod_unmute_user': {
		"str": 'unmuted reports from user {self.target_link}',
		"icon": 'fa-file-signature',
		"color": 'bg-success'
	},
	'move_hole': {
		"str": 'changed hole of {self.target_link}',
		"icon": 'fa-manhole',
		"color": 'bg-primary'
	},
	'nuke_user': {
		"str": 'removed all content of {self.target_link}',
		"icon": 'fa-radiation-alt',
		"color": 'bg-danger'
	},
	'pin_comment': {
		"str": 'pinned {self.target_link}',
		"icon": 'fa-thumbtack fa-rotate--45',
		"color": 'bg-success'
	},
	'pin_post': {
		"str": 'pinned post {self.target_link}',
		"icon": 'fa-thumbtack fa-rotate--45',
		"color": 'bg-success'
	},
	'progstack_comment': {
		"str": 'Applied progressive stack on {self.target_link}',
		"icon": 'fa-bullhorn',
		"color": 'bg-success'
	},
	'progstack_post': {
		"str": 'Applied progressive stack on post {self.target_link}',
		"icon": 'fa-bullhorn',
		"color": 'bg-success'
	},
	'clear_cloudflare_cache': {
		"str": 'cleared cloudflare cache',
		"icon": 'fab fa-cloudflare',
		"color": 'bg-muted'
	},
	'reject_app': {
		"str": 'rejected an application request by {self.target_link}',
		"icon": 'fa-robot',
		"color": 'bg-muted'
	},
	'remove_admin': {
		"str": 'removed {self.target_link} as admin',
		"icon": 'fa-user-crown',
		"color": 'bg-danger'
	},
	'revert': {
		"str": 'reverted {self.target_link} mod actions',
		"icon": 'fa-history',
		"color": 'bg-danger'
	},
	'revoke_app': {
		"str": 'revoked an application by {self.target_link}',
		"icon": 'fa-robot',
		"color": 'bg-muted'
	},
	'set_flair_locked': {
		"str": "set {self.target_link}'s flair (locked)",
		"icon": 'fa-award',
		"color": 'bg-primary'
	},
	'set_flair_notlocked': {
		"str": "set {self.target_link}'s flair (not locked)",
		"icon": 'fa-award',
		"color": 'bg-primary'
	},
	'set_new': {
		"str": 'changed the default sorting of comments on {self.target_link} to `new`',
		"icon": 'fa-sparkles',
		"color": 'bg-primary'
	},
	'set_hot': {
		"str": 'changed the default sorting of comments on {self.target_link} to `hot`',
		"icon": 'fa-fire',
		"color": 'bg-primary'
	},
	'set_nsfw': {
		"str": 'set {self.target_link} as +18',
		"icon": 'fa-eye-evil',
		"color": 'bg-danger'
	},
	'set_nsfw_comment': {
		"str": 'set {self.target_link} as +18',
		"icon": 'fa-eye-evil',
		"color": 'bg-danger'
	},
	'shadowban': {
		"str": 'shadowbanned {self.target_link}',
		"icon": 'fa-eye-slash',
		"color": 'bg-danger'
	},
	'unchud': {
		"str": 'unchudded {self.target_link}',
		"icon": 'fa-snooze',
		"color": 'bg-success'
	},
	'unban_comment': {
		"str": 'reinstated {self.target_link}',
		"icon": 'fa-comment',
		"color": 'bg-success'
	},
	'unban_domain': {
		"str": 'unbanned a domain',
		"icon": 'fa-globe',
		"color": 'bg-success'
	},
	'unban_post': {
		"str": 'reinstated post {self.target_link}',
		"icon": 'fa-feather-alt',
		"color": 'bg-success'
	},
	'unban_user': {
		"str": 'unbanned user {self.target_link}',
		"icon": 'fa-user',
		"color": 'bg-success'
	},
	'unblacklist_user': {
		"str": 'unblacklisted user {self.target_link} from restricted holes',
		"icon": 'fa-lock-open',
		"color": 'bg-success'
	},
	'undistinguish_comment': {
		"str": 'un-distinguished {self.target_link}',
		"icon": 'fa-crown',
		"color": 'bg-muted'
	},
	'undistinguish_post': {
		"str": 'un-distinguished {self.target_link}',
		"icon": 'fa-crown',
		"color": 'bg-muted'
	},
	'unnuke_user': {
		"str": 'approved all content of {self.target_link}',
		"icon": 'fa-radiation-alt',
		"color": 'bg-success'
	},
	'unpin_comment': {
		"str": 'unpinned {self.target_link}',
		"icon": 'fa-thumbtack fa-rotate--45',
		"color": 'bg-muted'
	},
	'unpin_post': {
		"str": 'unpinned post {self.target_link}',
		"icon": 'fa-thumbtack fa-rotate--45',
		"color": 'bg-muted'
	},
	'unset_nsfw': {
		"str": 'unset {self.target_link} as +18',
		"icon": 'fa-eye-evil',
		"color": 'bg-success'
	},
	'unset_nsfw_comment': {
		"str": 'unset {self.target_link} as +18',
		"icon": 'fa-eye-evil',
		"color": 'bg-success'
	},
	'unshadowban': {
		"str": 'unshadowbanned {self.target_link}',
		"icon": 'fa-eye',
		"color": 'bg-success'
	},
	'update_hat': {
		"str": 'updated hat image',
		"icon": 'fa-hat-cowboy',
		"color": 'bg-success'
	},
	'update_marsey': {
		"str": 'updated marsey',
		"icon": 'fa-cat',
		"color": 'bg-success'
	},
}

MODACTION_PRIVILEGED_TYPES = {'shadowban', 'unshadowban',
							'mod_mute_user', 'mod_unmute_user',
							'link_accounts', 'delink_accounts',
							'progstack_post', 'progstack_comment'}
MODACTION_PRIVILEGED__TYPES = {'progstack_post', 'progstack_comment'}
MODACTION_TYPES_FILTERED = deepcopy({t:v for t,v in MODACTION_TYPES.items()
                                     if not t in MODACTION_PRIVILEGED_TYPES})
MODACTION_TYPES__FILTERED = deepcopy({t:v for t,v in MODACTION_TYPES.items()
                                     if not t in MODACTION_PRIVILEGED__TYPES})
AEVANN_MODACTION_TYPES = {'ban_user','unban_user',
						'shadowban','unshadowban',
						'progstack_post','progstack_comment'}
