# Martian Map — EVA navigation for Mars

**NASA Space Apps Challenge 2026 · "Interplanetary Survival Guide: Martian Map"**

A "Google Maps for Mars" that plans a safe, science-rich Marswalk (on foot or by rover) from real NASA / USGS data:

- **Route planning** — A* search on slope grids built from USGS HiRISE (~1 m), CTX (20 m) and MOLA (463 m) elevation models, refined at ~2 m along the track; steep slopes, loose soil and (optionally) radiation exposure are penalised. Separate outbound and return routes.
- **Astronaut needs** — oxygen budget of the selected suit (xEMU, AxEMU, EMU, A7LB…), payload, water and food, walking/climbing/descending metabolic costs, Apollo walk-back rule for rovers.
- **Weather** — Mars24 solar time, sunrise/sunset, Mars Climate Database v6 (temperature, pressure, wind, dust, frost), checked and corrected against real Perseverance (MEDA) and Curiosity (REMS) readings.
- **Radiation** — dose estimate from Curiosity RAD measurements corrected for local atmospheric pressure, topographic shielding (sky-view), natural shelters along the route, solar-flare guidance.
- **Ground & geology** — THEMIS-based soil type (sand, dust, rock), geologic units, faults, scarps and contacts from the USGS geologic map of Mars → points of interest.
- **Navigation without GPS** — dead-reckoning route sheet (heading, distance, steps, sun position) and an offline "preloaded map" export (HTML), plus GeoJSON / GPX.
- French / English interface.

## Use of Super Intelligence (SI)
- **Idea and design — the team.** The challenge choice, the needs analysis (oxygen, weather, radiation, terrain, navigation, points of interest; see our FigJam board), the reference suit and every design decision come from Team Trajectory Error.
- **Code — AI-assisted.** The source code (`index.html`, `serve.py`) was written with an AI assistant (Claude, by Anthropic) from the team's specifications, then tested on real Martian sites and corrected by the team. This is also stated in the source files' headers and metadata.
- **Research and text — AI-assisted.** The assistant helped find data sources and scientific references and draft the documentation and English translation; every model is documented with its source in the app ("Model assumptions", "Known limitations").
- No AI-generated images, video or audio are used. No NASA branding is generated or modified.

## Run locally
```
python serve.py
```
then open http://localhost:8000 (Python 3, no dependencies). `serve.py` serves the page and relays requests to NASA/USGS/LMD servers that do not allow direct browser access (CORS); only whitelisted domains are relayed.

## Deploy
The repository contains `render.yaml`: on Render.com, *New → Blueprint* (or *Web Service*, start command `python serve.py`).

## Data sources
NASA Mars Trek (WMTS basemaps) · USGS Astrogeology STAC (HiRISE & CTX DTMs and orthoimages, THEMIS mosaics) · MOLA global DEM · USGS SIM 3292 Geologic Map of Mars (OGC API) · THEMIS thermal inertia / night IR (ASU / USGS) · Mars Climate Database v6 (LMD / ESA / CNES) · NASA/JPL MEDA & REMS weather feeds · MSL RAD publications (Hassler et al. 2014; Guo et al. 2017, 2018) · NASA-STD-3001.

See `LISEZMOI.md` (French) for the full list of model assumptions and limitations.
