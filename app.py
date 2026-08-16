"""
Flask front end for the returns-processing agent.

Flow:
    1. Customer logs in with customer_id/username + password
       (checked against customer_data.CUSTOMERS password hashes).
    2. Dashboard lists their past chat sessions (from session_index.json)
       with a "start new chat" button.
    3. Sending a message calls the agent deployed on ECS Fargate
       (agent_service_client.invoke) -- the agent itself, its tools, and
       session memory all live inside that container/service, not here.

RUN:
    pip install flask requests
    export AGENT_URL="https://your-express-mode-url"
    export FLASK_SECRET_KEY="something-random"   # optional, has a dev default
    python app.py

Then open http://127.0.0.1:5000
"""

import functools
import os

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

import agent_service_client
import session_index
from customer_data import authenticate, get_customer

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def current_customer() -> dict | None:
    customer_id = session.get("customer_id")
    return get_customer(customer_id) if customer_id else None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return redirect(url_for("dashboard") if "username" in session else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if "username" in session:
            return redirect(url_for("dashboard"))
        return render_template("login.html", error=None)

    identifier = request.form.get("identifier", "")
    password = request.form.get("password", "")
    customer = authenticate(identifier, password)

    if not customer:
        return render_template("login.html", error="Invalid ID/username or password."), 401

    session["username"] = customer["username"]
    session["customer_id"] = customer["customer_id"]
    session["full_name"] = customer["full_name"]
    return redirect(request.args.get("next") or url_for("dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    username = session["username"]
    entries = session_index.list_sessions(username)
    sessions_view = [
        {
            "session_id": e["session_id"],
            "created_at": e["created_at"],
            "last_active": e["last_active"],
            "preview": session_index.preview_for(e),
            "message_count": len(e["messages"]),
        }
        for e in entries
    ]
    return render_template(
        "dashboard.html",
        full_name=session["full_name"],
        customer_id=session["customer_id"],
        sessions=sessions_view,
    )


@app.route("/sessions/new", methods=["POST"])
@login_required
def new_session():
    session_id = session_index.create_session(session["username"], session["customer_id"])
    return redirect(url_for("chat_page", session_id=session_id))


@app.route("/chat/<session_id>")
@login_required
def chat_page(session_id):
    entry = session_index.get_session(session["username"], session_id)
    if entry is None:
        return "Session not found, or it doesn't belong to you.", 404
    return render_template(
        "chat.html",
        full_name=session["full_name"],
        session_id=session_id,
        messages=entry["messages"],
    )


@app.route("/api/chat/<session_id>/message", methods=["POST"])
@login_required
def send_message(session_id):
    username = session["username"]
    if not session_index.user_owns_session(username, session_id):
        return jsonify({"error": "Session not found, or it doesn't belong to you."}), 404

    user_text = (request.get_json(silent=True) or {}).get("message", "").strip()
    if not user_text:
        return jsonify({"error": "Message cannot be empty."}), 400

    customer = current_customer()
    session_index.append_message(username, session_id, "user", user_text)

    try:
        reply_text = agent_service_client.invoke(session_id, user_text, customer)
    except Exception as exc:
        return jsonify({"error": f"Agent call failed: {exc}"}), 503

    session_index.append_message(username, session_id, "assistant", reply_text)
    return jsonify({"reply": reply_text})


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)