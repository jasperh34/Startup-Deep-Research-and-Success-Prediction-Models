# Python Logic Mirror

This package mirrors the portable business logic from the Next.js app:

- company candidate search and ranking
- source query generation, collection, relevance filtering, and dedupe
- source type classification
- OpenAI structured extraction with a strict JSON schema
- investor-style report assembly
- Supabase row/payload helpers for companies, sources, and reports

The live app still runs through the existing Next.js API routes. This Python
layer is a stepping stone toward a FastAPI backend without breaking the current
frontend.

Run the offline smoke path:

```bash
PYTHONPATH=python python3 -m startup_search "twin prime"
```

Run the full top-candidate report path, using `.env.local` for API keys:

```bash
PYTHONPATH=python python3 -m startup_search "twin prime" --report
```

The package intentionally uses the Python standard library for HTTP and env
loading so it does not add dependencies yet. When FastAPI is introduced, this
can be wrapped by route handlers and swapped to official clients where useful.
