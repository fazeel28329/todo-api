# To-Do List API

A minimal to-do list API with in-memory storage. Built with Python + Flask.

## Running it

### Option 1: Locally

```bash
pip install -r requirements.txt
python app.py
```

The API will be listening on `http://localhost:5000`.

### Option 2: Docker

```bash
docker build -t todo-api .
docker run -p 5000:5000 todo-api
```

## Endpoints

### `POST /tasks` — add a task

Request body:
```json
{ "title": "Buy milk" }
```

Response `201 Created`:
```json
{ "id": 1, "title": "Buy milk", "done": false }
```

Returns `400 Bad Request` if `title` is missing or empty.

### `GET /tasks` — list tasks

Response `200 OK`:
```json
[
  { "id": 1, "title": "Buy milk", "done": false },
  { "id": 2, "title": "Walk dog", "done": true }
]
```

### `PATCH /tasks/<id>/done` — mark a task done

Response `200 OK`:
```json
{ "id": 1, "title": "Buy milk", "done": true }
```

Returns `404 Not Found` if the id doesn't exist.

### `GET /health`

Small extra endpoint, not part of the original spec — returns `{"status": "ok"}`. It exists so the Docker `HEALTHCHECK` and CI have something cheap to poll.

### Quick test with curl

```bash
curl -X POST localhost:5000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
curl localhost:5000/tasks
curl -X PATCH localhost:5000/tasks/1/done
```

## Design notes

- **In-memory storage**: a plain dict keyed by an auto-incrementing integer id. Simple, and matches the "no real database needed" requirement. The obvious cost: data is gone on restart, and it won't survive running multiple replicas (each would have its own memory). Fine for this exercise, not fine for production.
- **A lock around the dict/counter**: Flask's dev server can handle concurrent requests, and without a lock two simultaneous `POST`s could race on the id counter. It's a small thing, but it's the kind of bug that's invisible until it isn't.
- **Flask over something heavier**: for 3 endpoints and no persistence, a full framework felt like overkill — Flask (or an equivalent minimal framework in another language) gets out of the way.

## Reflection

**Trickiest part:** honestly, the API and Dockerfile themselves were the easy part — this kind of CRUD scaffolding is well-trodden ground. The part that actually took thought was deciding how much to build beyond the literal ask. It would've been easy to add task deletion, due dates, priorities, a `PUT` for full updates, request validation with a schema library, etc. The brief said "simple" and "2-3 endpoints" on purpose, so I treated scope creep as the thing to actively resist rather than a way to show effort.

**Why I made the choices I did:** I optimized for "someone can clone this and understand the whole thing in two minutes." That's why storage is a plain dict instead of even a lightweight embedded DB like SQLite, why there's no ORM, and why the whole app fits in one file. I did keep the lock around shared state and a `/health` endpoint, because those cost almost nothing and are the first two things I'd actually want if this were real.

**With another day, I'd:**
- Swap the dict for SQLite (still zero external infra to run, but persistence survives a restart) and add a couple of real integration tests instead of my manual curl pass.
- Add pagination and filtering to `GET /tasks` (e.g. `?done=false`) — trivial now, annoying to retrofit once there are real consumers.
- Pin the Docker base image by digest rather than tag, and add a `.dockerignore`.
- Have the GitHub Actions workflow actually run the test suite before the Docker build, and push the image to GHCR on `main` (kept out for now since the brief only asked for "builds successfully").
- Add basic auth or an API key, since right now anyone who can reach the container can read and write everyone's tasks.
