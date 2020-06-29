# highlight.js Web site


## Development

The site is a pretty standard Django application. Some interesting parts:

- `hljs_org/settings.py` — default project settings. Those that are read from `env(...)` can be overwritten by env vars.

- `hljs_org/management/commands/updatehljs.py` — deployment script that can be run both manually and as a reaction on a GitHub webhook posting to `/api/release/`.

- `hljs_org/views.py::release()` — GitHub webhook end point.

- `hljs_org/lib.py` — logic for working with the highlight.js source directory (parsing versions, readme, building a .zip archive for download, etc.)

(There are indeed no tests. Never needed them for this project :-) )


## Deployment

Deployment is done manually by the current owner of highlightjs.org, all the configs are outside of this repo.
