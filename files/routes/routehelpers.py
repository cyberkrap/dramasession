import time

from random import randint
from typing import Optional, Union, Callable, List
from sqlalchemy.orm import aliased, deferred
from sqlalchemy.sql import case, literal
from sqlalchemy.sql.expression import or_

from flask import g, session

from files.classes import Alt, Comment, User, Submission
from files.helpers.config.const import *
from files.helpers.security import generate_hash, validate_hash
from files.__main__ import cache

def get_raw_formkey(u:User):
	return f"{session['session_id']}+{u.id}+{u.login_nonce}"

def get_formkey(u:Optional[User]):
	if not u: return "" # if no user exists, give them a blank formkey
	return generate_hash(get_raw_formkey(u))

def validate_formkey(u:User, formkey:Optional[str]) -> bool:
	if not formkey: return False
	return validate_hash(get_raw_formkey(u), formkey)

@cache.memoize()
def get_alt_graph_ids(uid:int) -> List[int]:
	alt_graph_cte = g.db.query(literal(uid).label('user_id')).select_from(Alt).cte('alt_graph', recursive=True)

	alt_graph_cte_inner = g.db.query(
		case(
			(Alt.user1 == alt_graph_cte.c.user_id, Alt.user2),
			(Alt.user2 == alt_graph_cte.c.user_id, Alt.user1),
		)
	).select_from(Alt, alt_graph_cte).filter(
		or_(alt_graph_cte.c.user_id == Alt.user1, alt_graph_cte.c.user_id == Alt.user2)
	)

	alt_graph_cte = alt_graph_cte.union(alt_graph_cte_inner)
	return set([x[0] for x in g.db.query(User.id).filter(User.id == alt_graph_cte.c.user_id, User.id != uid).all()])

def get_alt_graph(uid:int) -> List[User]:
	alt_ids = get_alt_graph_ids(uid)
	return g.db.query(User).filter(User.id.in_(alt_ids)).order_by(User.username).all()

def add_alt(user1:int, user2:int):
	if user1 == AEVANN_ID or user2 == AEVANN_ID:
		return
	li = [user1, user2]
	existing = g.db.query(Alt).filter(Alt.user1.in_(li), Alt.user2.in_(li)).one_or_none()
	if not existing:
		new_alt = Alt(user1=user1, user2=user2)
		g.db.add(new_alt)
		g.db.flush()
		cache.delete_memoized(get_alt_graph_ids, user1)
		cache.delete_memoized(get_alt_graph_ids, user2)

def check_for_alts(current:User, include_current_session=False):
	current_id = current.id
	ids = [x[0] for x in g.db.query(User.id).all()]
	past_accs = set(session.get("history", [])) if include_current_session else set()

	for past_id in list(past_accs):
		if past_id not in ids:
			past_accs.remove(past_id)
			continue

		if past_id == current_id: continue

		li = [past_id, current_id]
		add_alt(past_id, current_id)
		other_alts = g.db.query(Alt).filter(Alt.user1.in_(li), Alt.user2.in_(li)).all()
		for a in other_alts:
			if a.deleted:
				if include_current_session:
					try: session["history"].remove(a.user1)
					except: pass
					try: session["history"].remove(a.user2)
					except: pass
				continue # don't propagate deleted alt links
			if a.user1 != past_id: add_alt(a.user1, past_id)
			if a.user1 != current_id: add_alt(a.user1, current_id)
			if a.user2 != past_id: add_alt(a.user2, past_id)
			if a.user2 != current_id: add_alt(a.user2, current_id)

	past_accs.add(current_id)
	if include_current_session:
		session["history"] = list(past_accs)
	g.db.flush()
	for u in get_alt_graph(current.id):
		if u.shadowbanned and not current.shadowbanned and current.id not in DONT_SHADOWBAN:
			current.shadowbanned = u.shadowbanned
			current.ban_reason = u.ban_reason
			g.db.add(current)
		elif current.shadowbanned and not u.shadowbanned and u.id not in DONT_SHADOWBAN:
			u.shadowbanned = current.shadowbanned
			u.ban_reason = current.ban_reason
			g.db.add(u)

		if u.is_muted and not current.is_muted:
			current.is_muted = u.is_muted
			g.db.add(current)
		elif current.is_muted and not u.is_muted:
			u.is_muted = current.is_muted
			g.db.add(u)

		if u.blacklisted_by and not current.blacklisted_by:
			current.blacklisted_by = u.blacklisted_by
			g.db.add(current)
		elif current.blacklisted_by and not u.blacklisted_by:
			u.blacklisted_by = current.blacklisted_by
			g.db.add(u)

def execute_shadowban_viewers_and_voters(v:Optional[User], target:Union[Submission, Comment]):
	if not v or not v.shadowbanned: return
	if not target: return
	if v.id != target.author_id: return
	if not (86400 > time.time() - target.created_utc > 60): return
	ti = max(int((time.time() - target.created_utc)/60), 1)
	max_upvotes = min(ti, 13)
	rand = randint(0, max_upvotes)
	if target.upvotes >= rand: return

	amount = randint(0, 3)
	if amount != 1: return

	target.upvotes += amount
	if isinstance(target, Submission):
		target.views += amount*randint(3, 5)
	g.db.add(target)
