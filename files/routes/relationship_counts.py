from flask import g, request
from sqlalchemy import func

from files.__main__ import app, limiter
from files.classes import CommentSaveRelationship, SaveRelationship, Subscription
from files.helpers.config.const import DEFAULT_RATELIMIT
from files.routes.wrappers import auth_required, get_ID


MAX_RELATIONSHIP_IDS = 200


def _parse_ids(raw_value):
	if not raw_value:
		return []

	ids = []
	seen = set()
	for value in raw_value.split(','):
		try:
			item_id = int(value)
		except (TypeError, ValueError):
			continue
		if item_id <= 0 or item_id in seen:
			continue
		seen.add(item_id)
		ids.append(item_id)
		if len(ids) >= MAX_RELATIONSHIP_IDS:
			break
	return ids


def _grouped_counts(model, id_column, ids):
	if not ids:
		return {}
	return dict(
		g.db.query(id_column, func.count())
		.filter(id_column.in_(ids))
		.group_by(id_column)
		.all()
	)


@app.get('/relationship-counts')
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def relationship_counts(v):
	post_ids = _parse_ids(request.args.get('post_ids'))
	comment_ids = _parse_ids(request.args.get('comment_ids'))

	post_saves = _grouped_counts(
		SaveRelationship,
		SaveRelationship.submission_id,
		post_ids,
	)
	post_subscriptions = _grouped_counts(
		Subscription,
		Subscription.submission_id,
		post_ids,
	)
	comment_saves = _grouped_counts(
		CommentSaveRelationship,
		CommentSaveRelationship.comment_id,
		comment_ids,
	)

	return {
		'posts': {
			str(post_id): {
				'saves': post_saves.get(post_id, 0),
				'subscriptions': post_subscriptions.get(post_id, 0),
			}
			for post_id in post_ids
		},
		'comments': {
			str(comment_id): {
				'saves': comment_saves.get(comment_id, 0),
			}
			for comment_id in comment_ids
		},
	}
