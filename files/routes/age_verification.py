"""Hosted Didit age-verification flow and contribution gates."""

import os
from urllib.parse import urlencode, urlsplit

import requests
from flask import abort, g, jsonify, redirect, render_template, request, session

from files.__main__ import app, limiter
from files.classes import Comment, Submission, User
from files.helpers.age_verification import (
    apply_didit_status,
    create_didit_session,
    didit_configured,
    didit_enabled,
    is_age_verified,
    record_webhook_event,
    retrieve_didit_decision,
    safe_internal_path,
    user_id_from_vendor_data,
    validate_didit_decision,
    verify_didit_webhook,
    webhook_event_seen,
)
from files.helpers.config.const import DEFAULT_RATELIMIT, SITE
from files.routes.wrappers import *


_CONTRIBUTION_ENDPOINTS = {
    "submit_get": "post",
    "submit_post": "post",
    "comment": "comment",
}
_NSFW_ENDPOINTS = {"post_id", "post_pid_comment_cid"}
_AGE_ROUTE_ENDPOINTS = {
    "age_verification_page",
    "age_verification_start",
    "age_verification_return",
    "didit_webhook",
}


def _same_site_referrer_path() -> str:
    referrer = str(request.referrer or "")
    if not referrer:
        return "/"
    parsed = urlsplit(referrer)
    if parsed.hostname and parsed.hostname.rstrip(".").lower() != SITE.rstrip(".").lower():
        return "/"
    value = parsed.path or "/"
    if parsed.query:
        value += "?" + parsed.query
    return safe_internal_path(value)


def _requested_next() -> str:
    candidate = request.values.get("next")
    if candidate:
        return safe_internal_path(candidate)
    if request.method == "GET":
        return safe_internal_path(request.full_path or request.path)
    return _same_site_referrer_path()


def _verification_redirect(reason: str):
    next_path = _requested_next()
    get_logged_in_user()
    if getattr(g, "is_api_or_xhr", False):
        return jsonify({
            "error": "age_verification_required",
            "message": "Age verification is required for this action.",
            "verification_path": "/age-verification",
            "reason": reason,
        }), 451
    query = urlencode({"next": next_path, "reason": reason})
    return redirect(f"/age-verification?{query}")


@app.before_request
def enforce_age_verification_gate():
    if not didit_enabled():
        return None
    endpoint = str(request.endpoint or "")
    if endpoint in _AGE_ROUTE_ENDPOINTS or endpoint in {"healthz", "static"}:
        return None

    if endpoint in _CONTRIBUTION_ENDPOINTS:
        user = get_logged_in_user()
        if user and not is_age_verified(user):
            return _verification_redirect(_CONTRIBUTION_ENDPOINTS[endpoint])
        return None

    if endpoint in _NSFW_ENDPOINTS:
        view_args = request.view_args or {}
        pid = view_args.get("pid")
        if not pid and endpoint == "post_pid_comment_cid" and view_args.get("cid"):
            pid_row = (
                g.db.query(Comment.parent_submission)
                .filter(Comment.id == int(view_args["cid"]))
                .one_or_none()
            )
            pid = pid_row[0] if pid_row else None
        if not pid:
            return None
        row = (
            g.db.query(Submission.over_18)
            .filter(Submission.id == int(pid))
            .one_or_none()
        )
        if row and bool(row[0]):
            user = get_logged_in_user()
            if not user or not is_age_verified(user):
                return _verification_redirect("nsfw")
    return None


@app.get("/age-verification")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_desired
def age_verification_page(v):
    next_path = safe_internal_path(request.values.get("next"), "/")
    status = str(request.values.get("status") or "").strip().lower()
    reason = str(request.values.get("reason") or "").strip().lower()
    return render_template(
        "age_verification.html",
        v=v,
        next_path=next_path,
        reason=reason,
        result_status=status,
        verified=bool(v and is_age_verified(v)),
        configured=didit_configured(),
        gate_enabled=didit_enabled(),
    )


@app.post("/age-verification/start")
@limiter.limit("5/hour;10/day", key_func=get_ID)
@auth_required
def age_verification_start(v):
    next_path = safe_internal_path(request.values.get("next"), "/")
    if is_age_verified(v):
        return redirect(next_path)
    if request.values.get("consent") != "yes":
        return render_template(
            "age_verification.html",
            v=v,
            next_path=next_path,
            reason=str(request.values.get("reason") or ""),
            result_status="",
            verified=False,
            configured=didit_configured(),
            gate_enabled=didit_enabled(),
            error="You must consent to the verification checks before continuing.",
        ), 400
    if not didit_configured():
        return render_template(
            "age_verification.html",
            v=v,
            next_path=next_path,
            reason=str(request.values.get("reason") or ""),
            result_status="",
            verified=False,
            configured=False,
            gate_enabled=didit_enabled(),
            error="Age verification is not fully configured yet.",
        ), 503

    try:
        data = create_didit_session(v)
    except (requests.RequestException, RuntimeError) as exc:
        app.logger.exception("Unable to create Didit verification session")
        return render_template(
            "age_verification.html",
            v=v,
            next_path=next_path,
            reason=str(request.values.get("reason") or ""),
            result_status="",
            verified=False,
            configured=True,
            gate_enabled=didit_enabled(),
            error=f"Verification could not start: {str(exc)[:240]}",
        ), 502

    v.age_verification_consent_utc = int(__import__("time").time())
    v.age_verification_session_id = str(data["session_id"])
    v.age_verification_provider = "didit"
    v.age_verification_status = str(data.get("status") or "not started").strip().lower()
    g.db.add(v)
    session["age_verification_next"] = next_path
    return redirect(str(data["url"]))


@app.get("/age-verification/return")
@limiter.limit("30/hour", key_func=get_ID)
@auth_desired
def age_verification_return(v):
    session_id = str(
        request.values.get("verificationSessionId")
        or request.values.get("session_id")
        or ""
    ).strip()
    next_path = safe_internal_path(session.pop("age_verification_next", "/"), "/")
    if not session_id:
        return redirect("/age-verification?status=missing")

    try:
        decision = retrieve_didit_decision(session_id)
        user_id = validate_didit_decision(decision, session_id)
    except (requests.RequestException, RuntimeError) as exc:
        app.logger.exception("Unable to retrieve Didit verification decision")
        query = urlencode({"status": "error", "next": next_path, "detail": str(exc)[:180]})
        return redirect(f"/age-verification?{query}")

    if v and int(v.id) != int(user_id):
        abort(403, "This verification session belongs to another account.")
    user = g.db.query(User).filter(User.id == user_id).one_or_none()
    if not user:
        abort(404)
    normalized = apply_didit_status(
        g.db,
        user,
        session_id,
        decision.get("status"),
    )
    query = urlencode({"status": normalized or "unknown", "next": next_path})
    return redirect(f"/age-verification?{query}")


@app.post("/webhooks/didit")
@limiter.exempt
def didit_webhook():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "invalid_json"}), 400
    signature = request.headers.get("X-Signature-V2", "")
    timestamp = request.headers.get("X-Timestamp", "")
    if not verify_didit_webhook(payload, signature, timestamp):
        return jsonify({"error": "invalid_signature"}), 401

    webhook_type = str(payload.get("webhook_type") or "")
    if webhook_type not in {"status.updated", "data.updated"}:
        return jsonify({"ok": True, "ignored": True}), 200
    workflow_id = str(os.environ.get("DIDIT_WORKFLOW_ID") or "").strip()
    if workflow_id and str(payload.get("workflow_id") or "") != workflow_id:
        return jsonify({"ok": True, "ignored": True}), 200

    event_id = str(payload.get("event_id") or "").strip()
    session_id = str(payload.get("session_id") or "").strip()
    user_id = user_id_from_vendor_data(payload.get("vendor_data"))
    if not event_id or not session_id or not user_id:
        return jsonify({"error": "invalid_envelope"}), 400
    if webhook_event_seen(g.db, event_id):
        return jsonify({"ok": True, "duplicate": True}), 200

    user = g.db.query(User).filter(User.id == user_id).one_or_none()
    if not user:
        return jsonify({"ok": True, "ignored": True}), 200
    status = str(payload.get("status") or "")
    apply_didit_status(g.db, user, session_id, status)
    record_webhook_event(
        g.db,
        event_id,
        session_id,
        user_id,
        status,
        webhook_type,
    )
    return jsonify({"ok": True}), 200
