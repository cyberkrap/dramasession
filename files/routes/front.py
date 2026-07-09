
from sqlalchemy import or_, not_

from files.classes.submission import Submission
from files.classes.votes import Vote
from files.helpers.awards import award_timers
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.sorting_and_time import *
from files.routes.wrappers import *
from files.__main__ import app, cache, limiter

@app.get("/")
@app.get("/h/<sub>")
@app.get("/s/<sub>")
@limiter.limit("3/second;30/minute;5000/hour;10000/day")
@auth_desired_with_logingate
def front_all(v, sub=None, subdomain=None):
	if sub:
		sub = get_sub_by_name(sub, graceful=True)
		if sub and not User.can_see(v, sub):
			abort(403)

	if (request.path.startswith('/h/') or request.path.startswith('/s/')) and not sub: abort(404)

	try: page = max(int(request.values.get("page", 1)), 1)
	except: abort(400)

	if v:
		defaultsorting = v.defaultsorting
		if sub or SITE_NAME != 'rDrama': defaulttime = 'all'
		else: defaulttime = v.defaulttime
	else:
		defaultsorting = "hot"
		if sub or SITE_NAME != 'rDrama': defaulttime = 'all'
		else: defaulttime = DEFAULT_TIME_FILTER

	sort=request.values.get("sort", defaultsorting)
	t=request.values.get('t', defaulttime)

	try: gt=int(request.values.get("after", 0))
	except: gt=0

	try: lt=int(request.values.get("before", 0))
	except: lt=0

	if sort == 'hot': default = True
	else: default = False

	pins = session.get(sort, default)
	holes = session.get('holes', True)

	ids, next_exists = frontlist(sort=sort,
					page=page,
					t=t,
					v=v,
					filter_words=v.filter_words if v else [],
					gt=gt,
					lt=lt,
					sub=sub,
					site=SITE,
					pins=pins,
					holes=holes
					)

	posts = get_posts(ids, v=v, eager=True)

	if v:
		if v.hidevotedon: posts = [x for x in posts if not hasattr(x, 'voted') or not x.voted]
		award_timers(v)

	if v and v.client: return {"data": [x.json(g.db) for x in posts], "next_exists": next_exists}
	return render_template("home.html", v=v, listing=posts, next_exists=next_exists, sort=sort, t=t, page=page, sub=sub, home=True, pins=pins, holes=holes)


LIMITED_WPD_HOLES = ('gore', 'aftermath', 'selfharm', 'meta', 'discussion', 'social', 'music', 'request')

@cache.memoize()
def frontlist(v=None, sort="hot", page=1, t="all", ids_only=True, filter_words='', gt=0, lt=0, sub=None, site=None, pins=True, holes=True):
	posts = g.db.query(Submission)

	if v and v.hidevotedon:
		posts = posts.outerjoin(Vote,
					and_(Vote.submission_id == Submission.id, Vote.user_id == v.id)
				).filter(Vote.submission_id == None)

	if sub: posts = posts.filter(Submission.sub == sub.name)
	elif v: posts = posts.filter(or_(Submission.sub == None, Submission.sub.notin_(v.all_blocks)))

	if gt: posts = posts.filter(Submission.created_utc > gt)
	if lt: posts = posts.filter(Submission.created_utc < lt)

	if not gt and not lt:
		posts = apply_time_filter(t, posts, Submission)

	posts = posts.filter(
		Submission.is_banned == False,
		Submission.private == False,
		Submission.deleted_utc == 0,
	)

	if pins and not gt and not lt:
		if sub: posts = posts.filter(Submission.hole_pinned == None)
		else: posts = posts.filter(Submission.stickied == None)

	if not sub and not holes:
		posts = posts.filter(or_(Submission.sub == None, Submission.sub == 'changelog'))

	if v:
		posts = posts.filter(Submission.author_id.notin_(v.userblocks))

	if v and filter_words:
		for word in filter_words:
			word = word.replace('\\', '').replace('_', '\_').replace('%', '\%').strip()
			posts=posts.filter(not_(Submission.title.ilike(f'%{word}%')))

	posts = sort_objects(sort, posts, Submission,
		include_shadowbanned=(v and v.can_see_shadowbanned))

	if v: size = v.frontsize or 0
	else: size = PAGE_SIZE

	if SITE_NAME == 'WPD' and sort == "hot" and sub == None:
		posts = posts.offset(size * (page - 1)).limit(201).all()

		to_remove = []
		for h in LIMITED_WPD_HOLES:
			to_remove += [x.id for x in posts if x.sub == h][1:]

		posts = [x for x in posts if x.id not in to_remove]
	else:
		posts = posts.offset(size * (page - 1)).limit(size+1).all()

	next_exists = (len(posts) > size)
	posts = posts[:size]

	if pins and page == 1 and not gt and not lt:
		if sub:
			pins = g.db.query(Submission).filter(Submission.sub == sub.name, Submission.hole_pinned != None)
		else:
			pins = g.db.query(Submission).filter(Submission.stickied != None, Submission.is_banned == False)

			if v:
				pins = pins.filter(or_(Submission.sub == None, Submission.sub.notin_(v.all_blocks)))
				for pin in pins:
					if pin.stickied_utc and int(time.time()) > pin.stickied_utc:
						pin.stickied = None
						pin.stickied_utc = None
						g.db.add(pin)


		if v: pins = pins.filter(Submission.author_id.notin_(v.userblocks))
		if SITE_NAME == 'rDrama':
			pins = pins.order_by(Submission.author_id != LAWLZ_ID)
		pins = pins.order_by(Submission.created_utc.desc()).all()
		posts = pins + posts

	if ids_only: posts = [x.id for x in posts]
	return posts, next_exists


@app.get("/random_post")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def random_post(v:User):

	p = g.db.query(Submission.id).filter(Submission.deleted_utc == 0, Submission.is_banned == False, Submission.private == False).order_by(func.random()).first()

	if p: p = p[0]
	else: abort(404)

	return redirect(f"/post/{p}")


@app.get("/random_user")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def random_user(v:User):
	u = g.db.query(User.username).filter(User.song != None, User.shadowbanned == None).order_by(func.random()).first()

	if u: u = u[0]
	else: abort(404, "No users have set a profile anthem so far!")

	return redirect(f"/@{u}")

@cache.memoize()
def comment_idlist(v=None, page=1, sort="new", t="day", gt=0, lt=0, site=None):
	comments = g.db.query(Comment.id) \
		.outerjoin(Comment.post) \
		.filter(
			or_(Comment.parent_submission != None, Comment.wall_user_id != None),
		)

	if v.admin_level < PERMS['POST_COMMENT_MODERATION']:
		comments = comments.filter(
			Comment.is_banned == False,
			Comment.deleted_utc == 0,
			Submission.private == False,
			Comment.author_id.notin_(v.userblocks),
		)

	if gt: comments = comments.filter(Comment.created_utc > gt)
	if lt: comments = comments.filter(Comment.created_utc < lt)

	if not gt and not lt:
		comments = apply_time_filter(t, comments, Comment)

	comments = sort_objects(sort, comments, Comment,
		include_shadowbanned=(v and v.can_see_shadowbanned))

	comments = comments.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE + 1).all()
	return [x[0] for x in comments]

@app.get("/comments")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def all_comments(v:User):
	try: page = max(int(request.values.get("page", 1)), 1)
	except: page = 1

	sort=request.values.get("sort", "new")
	t=request.values.get("t", "hour")

	try: gt=int(request.values.get("after", 0))
	except: gt=0

	try: lt=int(request.values.get("before", 0))
	except: lt=0
	idlist = comment_idlist(v=v,
							page=page,
							sort=sort,
							t=t,
							gt=gt,
							lt=lt,
							site=SITE
							)

	comments = get_comments(idlist, v=v)
	next_exists = len(idlist) > PAGE_SIZE
	idlist = idlist[:PAGE_SIZE]

	if v.client: return {"data": [x.json(g.db) for x in comments]}
	return render_template("home_comments.html", v=v, sort=sort, t=t, page=page, comments=comments, standalone=True, next_exists=next_exists)
