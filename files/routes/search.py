import re
import time
from calendar import timegm

from sqlalchemy import *

from files.helpers.regex import *
from files.helpers.sorting_and_time import *
from files.routes.wrappers import *
from files.__main__ import app

search_operator_hole = HOLE_NAME

valid_params = [
	'author',
	'domain',
	'over18',
	'post',
	'before',
	'after',
	'title',
	search_operator_hole,
]

def searchparse(text):
	text = text.lower()

	criteria = {x[0]:x[1] for x in query_regex.findall(text)}
	for x in criteria:
		if x in valid_params:
			text = text.replace(f"{x}:{criteria[x]}", "")

	text = text.strip()
	if text:
		criteria['full_text'] = text
		criteria['q'] = []
		for m in search_token_regex.finditer(text):
			token = m[1] if m[1] else m[2]
			# Escape SQL pattern matching special characters
			token = token.replace('\\', '').replace('_', '\_').replace('%', '\%')
			criteria['q'].append(token)

	return criteria

@app.get("/search/posts")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def searchposts(v:User):
	query = request.values.get("q", '').strip()
	if not query:
		abort(403, "Empty searches aren't allowed!")

	try: page = max(1, int(request.values.get("page", 1)))
	except: abort(400, "Invalid page input!")

	sort = request.values.get("sort", "new").lower()
	t = request.values.get('t', 'all').lower()

	criteria=searchparse(query)

	posts = g.db.query(Submission.id) \
				.join(Submission.author) \
				.filter(Submission.author_id.notin_(v.userblocks))

	if v.admin_level < PERMS['POST_COMMENT_MODERATION']:
		posts = posts.filter(
			Submission.deleted_utc == 0,
			Submission.is_banned == False,
			Submission.private == False)

	if 'author' in criteria:
		posts = posts.filter(Submission.ghost == False)
		author = get_user(criteria['author'], v=v, include_shadowbanned=False)
		if not author.is_visible_to(v):
			if v.client:
				abort(403, f"@{author.username}'s profile is private; You can't use the 'author' syntax on them")
			return render_template("search.html",
								v=v,
								query=query,
								total=0,
								page=page,
								listing=[],
								sort=sort,
								t=t,
								next_exists=False,
								domain=None,
								domain_obj=None,
								error=f"@{author.username}'s profile is private; You can't use the 'author' syntax on them."
								), 403
		else: posts = posts.filter(Submission.author_id == author.id)

	if 'q' in criteria:
		if('title' in criteria):
			words = [or_(Submission.title.ilike('%'+x+'%')) \
					for x in criteria['q']]
		else:
			words = [or_(Submission.title.ilike('%'+x+'%'), Submission.body.ilike('%'+x+'%')) \
					for x in criteria['q']]
		posts = posts.filter(*words)

	if 'over18' in criteria: posts = posts.filter(Submission.over_18==True)

	if 'domain' in criteria:
		domain=criteria['domain']

		domain = domain.replace('\\', '').replace('_', '\_').replace('%', '').strip()

		posts=posts.filter(
			or_(
				Submission.url.ilike("https://"+domain+'/%'),
				Submission.url.ilike("https://"+domain+'/%'),
				Submission.url.ilike("https://"+domain),
				Submission.url.ilike("https://"+domain),
				Submission.url.ilike("https://www."+domain+'/%'),
				Submission.url.ilike("https://www."+domain+'/%'),
				Submission.url.ilike("https://www."+domain),
				Submission.url.ilike("https://www."+domain),
				Submission.url.ilike("https://old." + domain + '/%'),
				Submission.url.ilike("https://old." + domain + '/%'),
				Submission.url.ilike("https://old." + domain),
				Submission.url.ilike("https://old." + domain)
				)
			)

	if search_operator_hole in criteria:
		posts = posts.filter(Submission.sub == criteria[search_operator_hole])

	if 'after' in criteria:
		after = criteria['after']
		try: after = int(after)
		except:
			try: after = timegm(time.strptime(after, "%Y-%m-%d"))
			except: abort(400)
		posts = posts.filter(Submission.created_utc > after)

	if 'before' in criteria:
		before = criteria['before']
		try: before = int(before)
		except:
			try: before = timegm(time.strptime(before, "%Y-%m-%d"))
			except: abort(400)
		posts = posts.filter(Submission.created_utc < before)

	posts = apply_time_filter(t, posts, Submission)

	posts = sort_objects(sort, posts, Submission,
		include_shadowbanned=(v and v.can_see_shadowbanned))

	total = posts.count()

	posts = posts.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE+1).all()

	ids = [x[0] for x in posts]

	next_exists = (len(ids) > PAGE_SIZE)
	ids = ids[:PAGE_SIZE]

	posts = get_posts(ids, v=v, eager=True)

	if v.client: return {"total":total, "data":[x.json(g.db) for x in posts]}

	return render_template("search.html",
						v=v,
						query=query,
						total=total,
						page=page,
						listing=posts,
						sort=sort,
						t=t,
						next_exists=next_exists
						)

@app.get("/search/comments")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def searchcomments(v:User):
	query = request.values.get("q", '').strip()
	if not query:
		abort(403, "Empty searches aren't allowed!")

	try: page = max(1, int(request.values.get("page", 1)))
	except: abort(400, "Invalid page input!")

	sort = request.values.get("sort", "new").lower()
	t = request.values.get('t', 'all').lower()

	criteria = searchparse(query)

	comments = g.db.query(Comment.id).outerjoin(Comment.post) \
		.filter(
			or_(Comment.parent_submission != None, Comment.wall_user_id != None),
			Comment.author_id.notin_(v.userblocks),
		)


	if 'post' in criteria:
		try: post = int(criteria['post'])
		except: abort(404)
		comments = comments.filter(Comment.parent_submission == post)


	if 'author' in criteria:
		comments = comments.filter(Comment.ghost == False)
		author = get_user(criteria['author'], v=v, include_shadowbanned=False)
		if not author.is_visible_to(v):
			if v.client:
				abort(403, f"@{author.username}'s profile is private; You can't use the 'author' syntax on them")

			return render_template("search_comments.html", v=v, query=query, total=0, page=page, comments=[], sort=sort, t=t, next_exists=False, error=f"@{author.username}'s profile is private; You can't use the 'author' syntax on them!"), 403

		else: comments = comments.filter(Comment.author_id == author.id)

	if 'q' in criteria:
		tokens = map(lambda x: re.sub(r'[\0():|&*!<>]', '', x), criteria['q'])
		tokens = filter(lambda x: len(x) > 0, tokens)
		tokens = map(lambda x: re.sub(r"'", "\\'", x), tokens)
		tokens = map(lambda x: x.strip(), tokens)
		tokens = map(lambda x: re.sub(r'\s+', ' <-> ', x), tokens)
		comments = comments.filter(Comment.body_ts.match(
			' & '.join(tokens),
			postgresql_regconfig='english'))

	if 'over18' in criteria: comments = comments.filter(Comment.over_18 == True)

	if search_operator_hole in criteria:
		comments = comments.filter(Submission.sub == criteria[search_operator_hole])

	comments = apply_time_filter(t, comments, Comment)

	if v.admin_level < PERMS['POST_COMMENT_MODERATION']:
		private = [x[0] for x in g.db.query(Submission.id).filter(Submission.private == True).all()]

		comments = comments.filter(
			Comment.is_banned==False,
			Comment.deleted_utc == 0,
			or_(
				Comment.parent_submission.notin_(private),
				Comment.wall_user_id != None
			)
		)


	if 'after' in criteria:
		after = criteria['after']
		try: after = int(after)
		except:
			try: after = timegm(time.strptime(after, "%Y-%m-%d"))
			except: abort(400)
		comments = comments.filter(Comment.created_utc > after)

	if 'before' in criteria:
		before = criteria['before']
		try: before = int(before)
		except:
			try: before = timegm(time.strptime(before, "%Y-%m-%d"))
			except: abort(400)
		comments = comments.filter(Comment.created_utc < before)

	comments = sort_objects(sort, comments, Comment,
		include_shadowbanned=(v and v.can_see_shadowbanned))

	total = comments.count()

	comments = comments.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE+1).all()

	ids = [x[0] for x in comments]

	next_exists = (len(ids) > PAGE_SIZE)
	ids = ids[:PAGE_SIZE]

	comments = get_comments(ids, v=v)

	if v.client: return {"total":total, "data":[x.json(db=g.db) for x in comments]}
	return render_template("search_comments.html", v=v, query=query, total=total, page=page, comments=comments, sort=sort, t=t, next_exists=next_exists, standalone=True)


@app.get("/search/users")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def searchusers(v:User):

	query = request.values.get("q", '').strip()

	try: page = max(1, int(request.values.get("page", 1)))
	except: abort(400, "Invalid page input!")

	sort = request.values.get("sort", "new").lower()
	t = request.values.get('t', 'all').lower()
	term=query.lstrip('@')
	term = term.replace('\\','').replace('_','\_').replace('%','')

	users=g.db.query(User).filter(
		or_(
			User.username.ilike(f'%{term}%'),
			User.original_username.ilike(f'%{term}%')
		)
	)

	if v.admin_level < PERMS['USER_SHADOWBAN']:
		users = users.filter(User.shadowbanned == None)

	users=users.order_by(User.username.ilike(term).desc(), User.stored_subscriber_count.desc())

	total=users.count()

	users = users.offset(PAGE_SIZE * (page-1)).limit(PAGE_SIZE+1).all()
	next_exists=(len(users)>PAGE_SIZE)
	users=users[:PAGE_SIZE]

	if v.client: return {"data": [x.json for x in users]}
	return render_template("search_users.html", v=v, query=query, total=total, page=page, users=users, sort=sort, t=t, next_exists=next_exists)
