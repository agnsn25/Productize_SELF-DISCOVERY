import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .routes import discover, infer, structures

# Resolve frontend dir relative to this file (backend/app/main.py -> frontend/)
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="SELF-DISCOVER API", lifespan=lifespan, docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(discover.router)
app.include_router(infer.router)
app.include_router(structures.router)


# ── Page routes (registered before static mount so they take priority) ──


@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/docs", include_in_schema=False)
async def serve_docs():
    return FileResponse(FRONTEND_DIR / "docs.html")


@app.get("/pricing", include_in_schema=False)
async def serve_pricing():
    return FileResponse(FRONTEND_DIR / "pricing.html")


@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui():
    custom_page = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{app.title} — API Reference</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css" />
  <link rel="stylesheet" href="/static/style.css" />
  <style>
    /* Hide Swagger's own topbar */
    .swagger-ui .topbar {{ display: none !important; }}
  </style>
</head>
<body>
  <nav class="navbar">
    <div class="navbar-inner">
      <div class="navbar-left">
        <a href="/" class="brand">
          <span class="brand-s">S</span>elf
          <span class="brand-dash">-</span>
          <span class="brand-d">D</span>iscover
          <span class="brand-api"><span class="brand-a">A</span>PI</span>
        </a>
        <span class="brand-subtitle">API Reference</span>
      </div>
      <div class="navbar-right">
        <a href="/" class="nav-link">Overview</a>
        <a href="/docs" class="nav-link">Documentation</a>
        <a href="/api/docs" class="nav-link active-link">API Reference</a>
      </div>
    </div>
  </nav>

  <div id="swagger-ui"></div>

  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({{
      url: "{app.openapi_url}",
      dom_id: '#swagger-ui',
      presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
      layout: "BaseLayout"
    }});
  </script>
</body>
</html>"""
    return HTMLResponse(custom_page)


# ── Static files (must be last — catch-all mount) ──

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
