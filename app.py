"""
Simple in-memory To-Do List API.

Endpoints:
    POST /tasks           -> add a task
    GET  /tasks            -> list all tasks
    PATCH /tasks/<id>/done -> mark a task as done

Storage is a plain Python dict living in process memory. Restarting the
process wipes all data — that's a deliberate tradeoff, see README.
"""
from flask import Flask, request, jsonify
from itertools import count
from threading import Lock

app = Flask(__name__)

# --- In-memory "database" -----------------------------------------------
tasks = {}
_id_counter = count(1)
_lock = Lock()  # guards tasks + counter against concurrent request access


@app.route("/tasks", methods=["POST"])
def add_task():
    body = request.get_json(silent=True) or {}
    title = body.get("title")

    if not title or not isinstance(title, str) or not title.strip():
        return jsonify({"error": "'title' is required and must be a non-empty string"}), 400

    with _lock:
        task_id = next(_id_counter)
        task = {"id": task_id, "title": title.strip(), "done": False}
        tasks[task_id] = task

    return jsonify(task), 201


@app.route("/tasks", methods=["GET"])
def list_tasks():
    return jsonify(list(tasks.values())), 200


@app.route("/tasks/<int:task_id>/done", methods=["PATCH"])
def mark_done(task_id):
    with _lock:
        task = tasks.get(task_id)
        if task is None:
            return jsonify({"error": f"task {task_id} not found"}), 404
        task["done"] = True

    return jsonify(task), 200


@app.route("/health", methods=["GET"])
def health():
    # Not part of the "core" spec, but handy for the Docker healthcheck
    # and for confirming the container actually came up.
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    # host=0.0.0.0 so it's reachable from outside the container
    app.run(host="0.0.0.0", port=5000)
