# Jasper Startup Search

Jasper Startup Search is a Next.js frontend backed by a Python research API.

The Python backend now owns the app workflow:

- company search and disambiguation
- source collection and deduplication
- Supabase persistence
- OpenAI structured extraction
- investor-style report generation

The Next.js code is kept for the browser UI.

## Run Locally

Start the app:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

`npm run dev` starts both the Python API and the Next.js frontend. The browser
calls `/api/...` on the Next.js dev server, and Next proxies those requests to
the Python API from `PYTHON_API_URL`.

You can also run the services separately:

```bash
npm run python-api
npm run next-dev
```

## Environment

Copy `.env.local.example` to `.env.local` and fill in:

- `TAVILY_API_KEY` for web search
- `OPENAI_API_KEY` for structured extraction
- `NEXT_PUBLIC_SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` for database writes

If `TAVILY_API_KEY` is empty, the Python API returns mock candidates so the UI
flow still works.

## Python API

The API is implemented with the Python standard library for now, so it runs
without adding backend dependencies:

```bash
PYTHONPATH=python python3 -m startup_search.server
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```
