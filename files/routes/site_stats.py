from copy import deepcopy

from flask import g, render_template, request

from files.__main__ import app, limiter
from files.helpers.community_stats import get_community_stats
from files.helpers.config.const import DEFAULT_RATELIMIT
from files.routes.wrappers import auth_required, get_ID


_PERIOD_SECONDS = {
    "30d": 86400,
    "26w": 604800,
}


def _public_snapshot(snapshot):
    """Keep reset bookkeeping internal instead of leaking it into public labels."""
    public = deepcopy(snapshot)
    for section in public.get("sections", []):
        for row in section.get("rows", []):
            label = str(row.get("label") or "")
            row["label"] = label.replace(" since reset", "")
    return public


def _decorate_trends(trends, generated_utc):
    """Attach exact bucket timing for the interactive chart UI.

    community_stats owns the data aggregation; this controller only adds display
    metadata so the browser can show a precise date/value tooltip for whichever
    point the cursor is nearest to.
    """
    public = deepcopy(trends)
    seconds = _PERIOD_SECONDS.get(public.get("key"), 86400)
    bucket_count = max(len(public.get("labels", [])), 1)
    current_bucket = (int(generated_utc) // seconds) * seconds
    public["bucket_seconds"] = seconds
    public["start_utc"] = current_bucket - ((bucket_count - 1) * seconds)
    public["bucket_name"] = "week" if seconds == 604800 else "day"
    return public


@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def toc_participation_stats(v):
    period = request.args.get("period", "30d")
    snapshot, trends = get_community_stats(g.db, period)
    snapshot = _public_snapshot(snapshot)
    trends = _decorate_trends(trends, snapshot["generated_utc"])

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
