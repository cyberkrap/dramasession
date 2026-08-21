from flask import g, render_template, request

from files.__main__ import app, limiter
from files.helpers.community_stats import get_community_stats
from files.helpers.config.const import DEFAULT_RATELIMIT
from files.routes.wrappers import auth_required, get_ID


@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def toc_participation_stats(v):
    period = request.args.get("period", "30d")
    snapshot, trends = get_community_stats(g.db, period)

    if v.client:
        return {
            "generated_utc": snapshot["generated_utc"],
            "headline": snapshot["headline"],
            "sections": snapshot["sections"],
            "houses": snapshot["houses"],
            "trends": trends,
        }

    return render_template(
        "stats.html",
        v=v,
        title="Site Statistics",
        snapshot=snapshot,
        trends=trends,
    )


# The legacy /stats URL is registered in static.py. Replace its endpoint after
# static.py loads instead of registering a competing route.
app.view_functions["participation_stats"] = toc_participation_stats
