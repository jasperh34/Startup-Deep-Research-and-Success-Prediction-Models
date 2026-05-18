# Jasper Startup Search

Jasper Startup Search is a web app for startup research and early diligence.
It helps resolve ambiguous company names, collect relevant public web sources,
extract structured founder and funding details, and generate an investor-style
research brief.

The current product is a Next.js browser UI backed by a Python research API.
The Python backend owns the core workflow:

- company search and disambiguation
- source collection, relevance filtering, and deduplication
- Supabase persistence for companies, sources, and reports
- OpenAI structured extraction from source snippets
- investor-style report generation

## Current Capabilities

- Search for a startup by name and choose the correct company when multiple
  matches exist.
- Collect source evidence from company websites, founder references, funding
  references, news, LinkedIn, Product Hunt, GitHub, YC profiles, jobs pages, and
  registry-style sources.
- Extract structured company details, including founders, funding, traction
  signals, recent news, and risks.
- Persist confirmed companies, source snippets, and generated reports in
  Supabase when credentials are configured.
- Generate a browser-facing research report that can be viewed from local
  history.

## Architecture

```text
Browser UI (Next.js)
        |
        | /api/* rewrites
        v
Python research API
        |
        +-- Tavily web search
        +-- OpenAI structured extraction
        +-- Supabase persistence
        +-- Report assembly
```

The Next.js app proxies `/api/...` requests to the Python API through
`PYTHON_API_URL`. This keeps the frontend focused on interaction and display
while the backend owns search, extraction, and report generation.

## Run Locally

Install dependencies:

```bash
npm install
```

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

## Future: Startup Success Prediction

A planned next major feature is a success prediction layer that estimates a
startup's probability of reaching a future funding milestone. The feature is
inspired by Emily Gavrilenko's Cal Poly thesis,
[Predicting Startup Success Using Publicly Available Data](https://digitalcommons.calpoly.edu/theses/2652/),
which studies whether public company data, funding history, news, search
presence, and social activity can predict whether a startup raises another round
within a fixed time horizon.

The goal is not to replace investor judgment. The goal is to add a consistent,
auditable signal that can help prioritize diligence, surface overlooked
companies, and make the app's research reports more decision-oriented.

### Prediction Roadmap

1. **Historical data model**

   Add durable tables for funding events, observation snapshots, feature
   snapshots, success labels, model versions, and prediction runs. This is
   necessary to avoid look-ahead bias and to make every prediction explainable
   as of a specific date.

2. **Scheduled company monitoring**

   Move beyond report-time collection by adding scheduled source refreshes for
   selected companies. Store time-stamped signals such as source counts, funding
   mentions, hiring activity, news volume, search visibility, and social or
   community traction when available.

3. **Feature engineering**

   Build a backend feature layer that converts collected evidence into model
   inputs, including:

   - company age and months since last funding
   - latest funding stage and number of known investors
   - founder count and founder-background signals
   - source volume by type
   - news and product-launch velocity
   - jobs and hiring indicators
   - geography, sector, and category features
   - description length, readability, and sentiment-style text signals
   - search visibility and web-presence metrics

4. **Baseline scoring**

   Start with a transparent heuristic or logistic baseline that can show a
   probability, confidence level, top drivers, and missing-data warnings inside
   each report. This gives users value before enough labeled data exists for a
   production-grade ML model.

5. **Model training and evaluation**

   Once labeled historical observations are available, train and compare models
   using precision, recall, and F1 for the "funded within horizon" class.
   CatBoost is a strong candidate because the problem includes sparse,
   categorical startup data such as geography, sector, and funding stage.

6. **Prediction API and report integration**

   Add backend endpoints for single-company predictions and model metadata.
   Extend report payloads with success probability, prediction horizon, threshold
   used, model version, top positive drivers, top risk drivers, and missing
   features.

7. **Screener experience**

   Add a screener UI for filtering saved or monitored startups by prediction
   probability, funding stage, region, sentiment/traction quartile, recent signal
   changes, and data completeness.

### Product Principles

- Every prediction should be tied to the information available at prediction
  time.
- The UI should show uncertainty and missing data rather than hiding it behind a
  single score.
- Early versions should prefer transparent scoring over opaque model confidence.
- Model performance should be evaluated on funding-milestone prediction, not
  broad accuracy, because startup outcomes are highly imbalanced.
- Prediction output should support diligence prioritization, not automatic
  investment decisions.
