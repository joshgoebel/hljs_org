# highlight.js Web site


## Development

The site is a pretty standard Django application. Some interesting parts:

- `hljs_org/settings.py` — default project settings. Those that are read from `env(...)` can be overwritten by env vars.

- `hljs_org/management/commands/updatehljs.py` — deployment script that can be run both manually and as a reaction on a GitHub webhook posting to `/api/release/`.

- `hljs_org/views.py::release()` — GitHub webhook end point.

- `hljs_org/lib.py` — logic for working with the highlight.js source directory (parsing versions, readme, building a .zip archive for download, etc.)

(There are indeed no tests. Never needed them for this project :-) )


## Local installation


### System requirements

- Python 3.6+

- dev package for libmemcached

    On a Mac:

    ```sh
    brew install libmemcached
    ```

    On a Debian family Linux:

    ```sh
    sudo apt install libmemcached-dev
    ```

    **Alternatively**, comment out `pylibmc` in requirements.txt, it should work without a cache.

- Local PostgreSQL. Installation is left as an exercise for the reader. Also feel free to change `hljs_org/settings.py` to use something simpler, the code only uses very basic SQL.

    Create the database with `createdb hlsj_org`.


### App

Installation:

```sh
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
./manage.py migrate
```

Running:

```
./manage.py runserver
```

Note, the site needs access to a checkout of highlight.js itself, which it expects to be at `../highlight.js` by default. You can override the location via an env var `HLJS_SOURCE`. Also, refer to `hljs_org/settings.py` for other tweakable settings.


## Production deployment

Deployment is done manually by the current owner of highlightjs.org, all the configs are outside of this repo.
