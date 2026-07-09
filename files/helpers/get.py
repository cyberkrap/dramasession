from typing import Callable, Iterable, List, Optional, Union

from flask import *
from sqlalchemy import and_, any_, or_
from sqlalchemy.orm import joinedload, selectinload, Query

from files.classes import Comment, CommentVote, Hat, Sub, Submission, User, UserBlock, Vote
from files.helpers.config.const import AUTOJANNY_ID
from files.__main__ import cache

def sanitize_username(username:str) -> str:
	if not username: return username
	return username.replace('\\', '').replace('_', '\_').replace('%', '').replace('(', '').replace(')', '').strip()

def get_id(username:str, graceful=False) -> Optional[int]:
	username = sanitize_username(username)
	if not username:
		if graceful: return None
		abort(404)
	user = g.db.query(
		User.id
		).filter(
		or_(
			User.username.ilike(username),
			User.original_username.ilike(username)
			)
		).one_or_none()

	if not user:
		if graceful: return None
		abort(404)

	return user[0]

def get_user(username:Optional[str], v:Optional[User]=None, graceful=False, include_blocks=False, include_shadowbanned=True) -> Optional[User]:
	if not username:
		if graceful: return None
		abort(404)

	username = sanitize_username(username)
	if not username:
		if graceful: return None
		abort(404)
	user = g.db.query(
		User
		).filter(
		or_(
			User.username.ilike(username),
			User.original_username.ilike(username)
			)
		)

	user = user.one_or_none()

	if not user or (user.shadowbanned and not (include_shadowbanned or (v and v.can_see_shadowbanned))):
		if graceful: return None
		abort(404)

	if v and include_blocks:
		user = add_block_props(user, v)
	return user

def get_users(usernames:Iterable[str], graceful=False) -> List[User]:
	if not usernames: return []
	usernames = [sanitize_username(n) for n in usernames]
	if not any(usernames):
		if graceful and len(usernames) == 0: return []
		abort(404)
	users = g.db.query(User).filter(
		or_(
			User.username.ilike(any_(usernames)),
			User.original_username.ilike(any_(usernames))
			)
		).all()

	if len(users) != len(usernames) and not graceful:
		abort(404)

	return users

def get_account(id:Union[str, int], v:Optional[User]=None, graceful=False, include_blocks=False, include_shadowbanned=True) -> Optional[User]:
	try:
		id = int(id)
	except:
		if graceful: return None
		abort(404)

	user = g.db.get(User, id)

	if not user or (user.shadowbanned and not (include_shadowbanned or (v and v.can_see_shadowbanned))):
		if not graceful: abort(404)
		else: return None

	if include_blocks:
		user = add_block_props(user, v)
	return user


def get_accounts_dict(ids:Union[Iterable[str], Iterable[int]], v:Optional[User]=None, graceful=False, include_shadowbanned=True) -> Optional[dict[int, User]]:
	if not ids: return {}
	try:
		ids = set([int(id) for id in ids])
	except:
		if graceful: return None
		abort(404)

	users = g.db.query(User).filter(User.id.in_(ids))
	if not (include_shadowbanned or (v and v.can_see_shadowbanned)):
		users = users.filter(User.shadowbanned == None)
	users = users.all()
	if len(users) != len(ids) and not graceful: abort(404)
	return {u.id:u for u in users}

def get_post(i:Union[str, int], v:Optional[User]=None, graceful=False) -> Optional[Submission]:
	try: i = int(i)
	except:
		if graceful: return None
		else: abort(404)

	if not i:
		if graceful: return None
		else: abort(404)

	if v:
		vt = g.db.query(Vote).filter_by(user_id=v.id, submission_id=i).subquery()
		blocking = v.blocking.subquery()

		post = g.db.query(
			Submission,
			vt.c.vote_type,
			blocking.c.target_id,
		)

		post=post.filter(Submission.id == i
		).outerjoin(
			vt,
			vt.c.submission_id == Submission.id,
		).outerjoin(
			blocking,
			blocking.c.target_id == Submission.author_id,
		)

		post=post.one_or_none()

		if not post:
			if graceful: return None
			else: abort(404)

		x = post[0]
		x.voted = post[1] or 0
		x.is_blocking = post[2] or 0
	else:
		post = g.db.get(Submission, i)
		if not post:
			if graceful: return None
			else: abort(404)
		x=post

	return x


def get_posts(pids:Iterable[int], v:Optional[User]=None, eager:bool=False, extra:Optional[Callable[[Query], Query]]=None) -> List[Submission]:
	if not pids: return []

	if v:
		vt = g.db.query(Vote.vote_type, Vote.submission_id).filter(
			Vote.submission_id.in_(pids),
			Vote.user_id==v.id
			).subquery()

		blocking = v.blocking.subquery()
		blocked = v.blocked.subquery()

		query = g.db.query(
			Submission,
			vt.c.vote_type,
			blocking.c.target_id,
			blocked.c.target_id,
		).filter(
			Submission.id.in_(pids)
		).outerjoin(
			vt, vt.c.submission_id==Submission.id
		).outerjoin(
			blocking,
			blocking.c.target_id == Submission.author_id,
		).outerjoin(
			blocked,
			blocked.c.user_id == Submission.author_id,
		)
	else:
		query = g.db.query(Submission).filter(Submission.id.in_(pids))

	if extra: query = extra(query)

	if eager:
		query = query.options(
			selectinload(Submission.author).options(
				selectinload(User.hats_equipped.and_(Hat.equipped == True)) \
					.joinedload(Hat.hat_def, innerjoin=True),
				selectinload(User.badges),
				selectinload(User.sub_mods),
				selectinload(User.sub_exiles),
			),
			selectinload(Submission.flags),
			selectinload(Submission.awards),
			selectinload(Submission.options),
		)

	results = query.all()

	if v:
		output = [p[0] for p in results]
		for i in range(len(output)):
			output[i].voted = results[i][1] or 0
			output[i].is_blocking = results[i][2] or 0
			output[i].is_blocked = results[i][3] or 0
	else:
		output = results

	return sorted(output, key=lambda x: pids.index(x.id))

def get_comment(i:Union[str, int], v:Optional[User]=None, graceful=False) -> Optional[Comment]:
	try: i = int(i)
	except:
		if graceful: return None
		abort(404)

	if not i:
		if graceful: return None
		else: abort(404)

	comment=g.db.get(Comment, i)
	if not comment:
		if graceful: return None
		else: abort(404)

	return add_vote_and_block_props(comment, v, CommentVote)

def add_block_props(target:Union[Submission, Comment, User], v:Optional[User]):
	if not v: return target
	id = None

	if any(isinstance(target, cls) for cls in {Submission, Comment}):
		id = target.author_id
	elif isinstance(target, User):
		id = target.id
	else:
		raise TypeError("add_block_props only supports non-None submissions, comments, and users")

	if hasattr(target, 'is_blocking') and hasattr(target, 'is_blocked'):
		return target

	if v.id == id or id == AUTOJANNY_ID: # users can't block or be blocked by themselves or AutoJanny
		target.is_blocking = False
		target.is_blocked = False
		return target

	block = g.db.query(UserBlock).filter(
		or_(
			and_(
				UserBlock.user_id == v.id,
				UserBlock.target_id == id
			),
			and_(
				UserBlock.user_id == id,
				UserBlock.target_id == v.id
			)
		)
	).first()
	target.is_blocking = block and block.user_id == v.id
	target.is_blocked = block and block.target_id == v.id
	return target

def add_vote_props(target:Union[Submission, Comment], v:Optional[User], vote_cls):
	if hasattr(target, 'voted'): return target

	vt = g.db.query(vote_cls.vote_type).filter_by(user_id=v.id)
	if vote_cls == Vote:
		vt = vt.filter_by(submission_id=target.id)
	elif vote_cls == CommentVote:
		vt = vt.filter_by(comment_id=target.id)
	else:
		vt = None
	if vt: vt = vt.one_or_none()
	target.voted = vt.vote_type if vt else 0
	return target

def add_vote_and_block_props(target:Union[Submission, Comment], v:Optional[User], vote_cls):
	if not v: return target
	target = add_block_props(target, v)
	return add_vote_props(target, v, vote_cls)

def get_comments(cids:Iterable[int], v:Optional[User]=None, extra:Optional[Callable[[Query], Query]]=None) -> List[Comment]:
	if not cids: return []
	if v:
		output = get_comments_v_properties(v, True, None, Comment.id.in_(cids))[1] # TODO: support 'extra' for get_comments_v_properties
	else:
		output = g.db.query(Comment).join(Comment.author)
		if extra: output = extra(output)
		output = output.filter(User.shadowbanned == None, Comment.id.in_(cids)).all()
	return sorted(output, key=lambda x: cids.index(x.id))

def get_comments_v_properties(v:User, include_shadowbanned=True, should_keep_func:Optional[Callable[[Comment], bool]]=None, *criterion):
	if not v:
		raise TypeError("A user is required")
	votes = g.db.query(CommentVote.vote_type, CommentVote.comment_id).filter_by(user_id=v.id).subquery()
	blocking = v.blocking.subquery()
	blocked = v.blocked.subquery()
	comments = g.db.query(
		Comment,
		votes.c.vote_type,
		blocking.c.target_id,
		blocked.c.target_id,
	)

	if not include_shadowbanned and not v.can_see_shadowbanned:
		comments = comments.join(Comment.author).filter(User.shadowbanned == None)

	comments = comments.filter(*criterion)
	comments = comments.outerjoin(
		votes,
		votes.c.comment_id == Comment.id,
	).outerjoin(
		blocking,
		blocking.c.target_id == Comment.author_id,
	).outerjoin(
		blocked,
		blocked.c.user_id == Comment.author_id,
	)
	queried = comments.all()
	output = []
	dump = []
	for c in queried:
		comment = c[0]
		comment.voted = c[1] or 0
		comment.is_blocking = c[2] or 0
		comment.is_blocked = c[3] or 0
		if not should_keep_func or should_keep_func(c[0]): output.append(comment)
		else: dump.append(comment)
	return (comments, output)

def get_sub_by_name(sub:str, v:Optional[User]=None, graceful=False) -> Optional[Sub]:
	if not sub:
		if graceful: return None
		else: abort(404)
	sub = sub.replace('/h/', '').strip().lower()
	if not sub:
		if graceful: return None
		else: abort(404)
	sub = g.db.get(Sub, sub)
	if not sub:
		if graceful: return None
		else: abort(404)
	return sub

@cache.memoize()
def get_profile_picture(identifier:Union[int, str]) -> str:
	if isinstance(identifier, int):
		x = get_account(identifier, graceful=True)
	else:
		x = get_user(identifier, graceful=True)

	return x.profile_url if x else 'not_found'

def get_error():
	if request.referrer and request.referrer.split('?')[0] == request.base_url:
		return request.values.get("error")
	else:
		return None

def get_msg():
	if request.referrer and request.referrer.split('?')[0] == request.base_url:
		return request.values.get("msg")
	else:
		return None
