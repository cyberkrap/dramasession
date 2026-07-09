from typing import Any, Callable, Optional, Tuple, Union

from sqlalchemy import Column, func
from sqlalchemy.orm import scoped_session

from files.helpers.config.const import LEADERBOARD_LIMIT

from .badges import Badge
from .marsey import Marsey
from .user import User
from .userblock import UserBlock

class Leaderboard:
	"""
	Represents an request-context leaderboard. None of this is persisted yet,
	although this is probably a good idea to do at some point.
	"""
	all_users = None
	v_position = 0
	v_value = None
	v_appears_in_ranking = False
	user_func = None
	value_func = None

	def __init__(self, header_name:str, table_header_name:str, html_id:str, table_column_name:str,
				user_relative_url:Optional[str], query_function:Callable[..., Tuple[Any, Any, Any]],
				criteria, v:User, value_func:Optional[Callable[[User], Union[int, Column]]], db:scoped_session, users, limit=LEADERBOARD_LIMIT):
		self.header_name = header_name
		self.table_header_name = table_header_name
		self.html_id = html_id
		self.table_column_name = table_column_name
		self.user_relative_url = user_relative_url
		self.limit = limit
		lb = query_function(criteria, v, db, users, limit)
		self.all_users = lb[0]
		self.v_position = lb[1]
		self.v_value = lb[2]
		self.v_appears_in_ranking = self.v_position and self.v_position <= len(self.all_users)
		if value_func:
			self.user_func = lambda u:u
			self.value_func = value_func
			self.v_value = value_func(v)
		else:
			self.user_func = lambda u:u[0]
			self.value_func = lambda u: u[1] or 0

	@classmethod
	def get_simple_lb(cls, order_by, v:User, db:scoped_session, users, limit:int):
		leaderboard = users.order_by(order_by.desc()).limit(limit).all()
		position = None
		if v not in leaderboard:
			sq = db.query(User.id, func.rank().over(order_by=order_by.desc()).label("rank")).subquery()
			position = db.query(sq.c.id, sq.c.rank).filter(sq.c.id == v.id).limit(1).one()[1]
		return (leaderboard, position, None)

	@classmethod
	def count_and_label(cls, criteria):
		return func.count(criteria).label("count")

	@classmethod
	def rank_filtered_rank_label_by_desc(cls, criteria):
		return func.rank().over(order_by=func.count(criteria).desc()).label("rank")

	@classmethod
	def get_badge_marsey_lb(cls, lb_criteria, v:User, db:scoped_session, users:Any, limit):
		sq = db.query(lb_criteria, cls.count_and_label(lb_criteria), cls.rank_filtered_rank_label_by_desc(lb_criteria)).group_by(lb_criteria).subquery()
		sq_criteria = None
		if lb_criteria == Badge.user_id:
			sq_criteria = User.id == sq.c.user_id
		elif lb_criteria == Marsey.author_id:
			sq_criteria = User.id == sq.c.author_id
		else:
			raise ValueError("This leaderboard function only supports Badge.user_id and Marsey.author_id")

		leaderboard = db.query(User, sq.c.count).join(sq, sq_criteria).order_by(sq.c.count.desc())
		position = db.query(User.id, sq.c.rank, sq.c.count).join(sq, sq_criteria).filter(User.id == v.id).one_or_none()
		if position: position = (position[1], position[2])
		else: position = (leaderboard.count() + 1, 0)
		leaderboard = leaderboard.limit(limit).all()
		return (leaderboard, position[0], position[1])

	@classmethod
	def get_blockers_lb(cls, lb_criteria, v:User, db:scoped_session, users:Any, limit):
		if lb_criteria != UserBlock.target_id:
			raise ValueError("This leaderboard function only supports UserBlock.target_id")
		sq = db.query(lb_criteria, cls.count_and_label(lb_criteria)).group_by(lb_criteria).subquery()
		leaderboard = db.query(User, sq.c.count).join(User, User.id == sq.c.target_id).order_by(sq.c.count.desc())

		sq = db.query(lb_criteria, cls.count_and_label(lb_criteria), cls.rank_filtered_rank_label_by_desc(lb_criteria)).group_by(lb_criteria).subquery()
		position = db.query(sq.c.rank, sq.c.count).join(User, User.id == sq.c.target_id).filter(sq.c.target_id == v.id).limit(1).one_or_none()
		if not position: position = (leaderboard.count() + 1, 0)
		leaderboard = leaderboard.limit(limit).all()
		return (leaderboard, position[0], position[1])

	@classmethod
	def get_hat_lb(cls, lb_criteria, v:User, db:scoped_session, users:Any, limit):
		leaderboard = db.query(User, func.count(lb_criteria)).join(lb_criteria).group_by(User).order_by(func.count(lb_criteria).desc())
		sq = db.query(User.id, cls.count_and_label(lb_criteria), cls.rank_filtered_rank_label_by_desc(lb_criteria)).join(lb_criteria).group_by(User).subquery()
		position = db.query(sq.c.rank, sq.c.count).filter(sq.c.id == v.id).limit(1).one_or_none()
		if not position: position = (leaderboard.count() + 1, 0)
		leaderboard = leaderboard.limit(limit).all()
		return (leaderboard, position[0], position[1])
