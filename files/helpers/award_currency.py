def _balance(user, currency):
	value = getattr(user, currency, 0)
	try:
		return int(value or 0)
	except (TypeError, ValueError):
		return 0


def currency_label(currency):
	return "Wishbux" if currency == "marseybux" else "Wishcoins"


def can_afford_award(user, price):
	return user.can_spend("marseybux", price) or user.can_spend("coins", price)


def preferred_award_currency(user, price, requested=None):
	aliases = {
		"marseybux": "marseybux",
		"wishbux": "marseybux",
		"bux": "marseybux",
		"mb": "marseybux",
		"coins": "coins",
		"wishcoins": "coins",
	}
	requested = aliases.get((requested or "").lower())

	candidates = []
	if requested:
		candidates.append(requested)

	# Wishbux is the default whenever the account has any. If it cannot cover
	# the purchase, Wishcoins remain a fallback instead of blocking the user.
	if _balance(user, "marseybux") > 0:
		candidates.append("marseybux")
	candidates.append("coins")
	candidates.append("marseybux")

	seen = set()
	ordered = []
	for currency in candidates:
		if currency not in seen:
			seen.add(currency)
			ordered.append(currency)

	for currency in ordered:
		if user.can_spend(currency, price):
			return currency

	return ordered[0]


def charge_award(user, price, requested=None):
	preferred = preferred_award_currency(user, price, requested)
	fallback = "coins" if preferred == "marseybux" else "marseybux"

	if user.charge_account(preferred, price):
		return preferred
	if user.charge_account(fallback, price):
		return fallback
	return None
