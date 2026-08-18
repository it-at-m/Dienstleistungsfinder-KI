# Migration audit record

The public import was prepared from working-tree snapshots, without transferring either internal Git history.

- Backend source commit: `fb7fb5367032a88924c65bfe2e35335a8036a114`
  - Modified: `src/backend/data_models.py`
  - Untracked and imported: `src/backend/rerank_v2.py`
- Indexer source commit: `23726e20dca9526118e8db2d9d0ff7cf6f6b7786`
  - Modified and imported: `app.py`, `src/site_visits.py`, `src/utils.py`

Excluded from the import: `.env` files, notebooks, caches, virtual environments, `node_modules`, generated frontend `dist`, indexer `artifacts`, operational `input/web_stats.csv`, example/request payload dumps, and legacy `.gitlab-ci.yml` files. `input/api_ids.txt` was also excluded because its public-data review was not available.

Publication changes remove embedded API-ID credentials and internal endpoints. API authentication now uses `API_AUTH_USER` and `API_AUTH_PASS`; Etracker is optional; mandatory Qdrant configuration fails the process. The previously embedded credential must still be rotated in the owning internal system before a release is published.

Before merging, maintainers must complete the legal review of imported code/assets and confirm that retaining the repository MIT license is appropriate. This record is not a legal clearance.
