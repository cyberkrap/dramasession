from flask import g, render_template
from files.helpers.get import get_accounts_dict

from files.routes.wrappers import auth_required
from files.__main__ import app, cache

_special_leaderboard_query = """
WITH bet_options AS (
	SELECT p.id AS submission_id, so.id AS option_id, so.exclusive, cnt.count
	FROM submission_options so
	JOIN submissions p ON so.submission_id = p.id
	JOIN (
		SELECT option_id, COUNT(*) FROM submission_option_votes
		GROUP BY option_id
	) AS cnt ON so.id = cnt.option_id
	WHERE p.author_id in (30,152) AND p.created_utc > 1668953400
		AND so.exclusive IN (2, 3)
),
submission_payouts AS (
	SELECT
		sq_total.submission_id,
		sq_winners.sum AS bettors,
		floor((sq_total.sum * 200) / sq_winners.sum) AS winner_payout
	FROM (
		SELECT submission_id, SUM(count)
		FROM bet_options GROUP BY submission_id
	) AS sq_total
	JOIN (
		SELECT submission_id, SUM(count)
		FROM bet_options WHERE exclusive = 3 GROUP BY submission_id
	) AS sq_winners ON sq_total.submission_id = sq_winners.submission_id
),
bet_votes AS (
	SELECT
		opt.option_id AS option_id,
		opt.exclusive,
		sov.user_id,
		CASE
			WHEN opt.exclusive = 2 THEN -200
			WHEN opt.exclusive = 3 THEN (submission_payouts.winner_payout - 200)
		END payout
	FROM submission_option_votes sov
	LEFT OUTER JOIN bet_options AS opt
		ON opt.option_id = sov.option_id
	LEFT OUTER JOIN submission_payouts
		ON opt.submission_id = submission_payouts.submission_id
	WHERE opt.option_id IS NOT NULL
),
bettors AS (
	SELECT
		COALESCE(bet_won.user_id, bet_lost.user_id) AS user_id,
		(COALESCE(bet_won.count_won, 0)
			+ COALESCE(bet_lost.count_lost, 0)) AS bets_total,
		COALESCE(bet_won.count_won, 0) AS bets_won
	FROM (
		SELECT user_id, COUNT(*) AS count_won FROM bet_votes
		WHERE exclusive = 3 GROUP BY user_id) AS bet_won
	FULL OUTER JOIN (
		SELECT user_id, COUNT(*) AS count_lost FROM bet_votes
		WHERE exclusive = 2 GROUP BY user_id
	) AS bet_lost ON bet_won.user_id = bet_lost.user_id
)
SELECT
	bettors.user_id,
	bettors.bets_won,
	bettors.bets_total,
	bet_payout.net AS payout
FROM bettors
LEFT OUTER JOIN (
	SELECT user_id, SUM(payout) AS net FROM bet_votes GROUP BY user_id
) AS bet_payout ON bettors.user_id = bet_payout.user_id
ORDER BY payout DESC, bets_won DESC, bets_total ASC;
"""

@cache.memoize()
def _special_leaderboard_get():
	print('worldcup', flush=True)
	result = g.db.execute(_special_leaderboard_query).all()
	return result

@app.get('/events/worldcup2022/leaderboard')
@app.get('/special/worldcup2022/leaderboard')
@auth_required
def get_leaderboard(v):
	result = _special_leaderboard_get()
	if g.is_api_or_xhr: return result
	users = get_accounts_dict([r[0] for r in result],
		v=v, include_shadowbanned=False, graceful=True)
	return render_template("special/worldcup22_leaderboard.html",
		v=v, result=result, users=users)
