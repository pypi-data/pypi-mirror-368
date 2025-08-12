
# mkdocs-jupyterlite

A MkDocs plugin that enables embedding interactive jupyterlite notebooks in your docs.

Say you have a notebook `example.ipynb` in your awesome project, and you want
users to be able to play around with it.
In the past, you could use a tool like [Binder](https://mybinder.org/) to achieve this.
But, that requires a full docker environment and a remote server.
By using [JupyterLite](https://jupyterlite.readthedocs.io/),
you can run Jupyter notebooks directly in the browser without any server-side dependencies.

However, to use jupyterlite, you have to manually install jupyterlite and
then run a build step to package your notebooks, other files, and python
dependencies into a single static site.

This plugin automates that process for you.

## Installation

### Step 1: Install the plugin from [PyPI](https://pypi.org/project/mkdocs-jupyterlite/):

```bash
python -m pip install mkdocs-jupyterlite
```

### Step 2: Configure your `mkdocs.yml` file

See the [mkdocs.yml](https://github.com/NickCrews/mkdocs-jupyterlite/blob/main/mkdocs.yml)
that configures [this project's site](https://nickcrews.github.io/mkdocs-jupyterlite).

```yaml
site_name: mkdocs-jupyterlite
site_url: https://nickcrews.github.io/mkdocs-jupyterlite/
repo_url: https://github.com/nickcrews/mkdocs-jupyterlite/

nav:
  - Home: index.md
  - Notebook 1: notebook.ipynb

plugins:
  - jupyterlite:
      enabled: true
      notebook_patterns:
        # include all
        - "**/*.ipynb",
        # exclude drafts
        - "!**/draft_*.ipynb",  
        # re-include a specific draft
        - "project/drafts/draft_keep.ipynb",
        # exclude an anchored notebook
        - "!/top_secret.ipynb",
```

Here are the details on the configuration options:

### `enabled`

bool, whether or not the plugin is enabled. Defaults to `true`.

### `notebook_patterns`

A list of patterns that uses [gitignore](https://git-scm.com/docs/gitignore)
semantics to include and exclude files.
The last matching pattern will be used to determine if a file is a notebook.

For all files that match, the content of the page will be an
iframe that embeds the JupyterLite Notebook html.

## Contributing

I want this to be usable for other people, so file an issue if you want
to use this in your site, but run into any problems.

Possible improvements:

- Include custom python wheels into the JupyterLite environment.
- Passing an entire jupyter-lite.json config file.
- Instead of using an iframe, actually inline the contents of the generated HTML?
- Fix the TOC so clicking headers actually scrolls in the iframe.