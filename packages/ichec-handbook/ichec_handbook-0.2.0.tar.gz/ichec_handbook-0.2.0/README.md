# ichec_handbook

`ichec_handbook` is a tool for generating e-books and technical documents. It is used at the Irish Centre for High End Computing (ICHEC) to build the [ICHEC handbook](https://ichec-handbook.readthedocs.io/en/latest/src/frontmatter.html) and others.

# Features #

The project is a [Jupyter Book](https://jupyterbook.org/en/stable/intro.html) wrapper that can build multiple configurations of a book based on tags in document frontmatter, allowing the concept of 'public', 'private' or 'draft' versions.

In particular, it allows:

* Rendering of different book versions (e.g. `public`, `private`, `draft`) based on document frontmatter tags
* Automatic conversion of image formats (including TIKZ and mermaid) to best suit the output format (web, PDF etc).
* Named build configurations specified in YAML, allowing rendering of multiple versions in the same build job.
* Book version numbering

# Usage #

Assuming a repository has been set up for a standard Jupyter Book build, to use `ichec_handbook` you can add some additional build configurations to the existing `_config.yml` under an `ichec_handbook` key, for example:

``` yaml
title: Mock Book
author: Mock Book Author
exclude_patterns: [/src/media, infra/, infra/README.md, _build, .venv]
only_build_toc_files: true
sphinx:
  config:
    myst_heading_anchors: 3
latex:
  latex_documents:
     targetname: book.tex
ichec_handbook:
  project_name: mock_book
  version: 0.0.0
  builds:
    - name: "internal"
      outputs:
        - "pdf"
        - "html"
        - "src"
    - name: "public"
      outputs:
        - "pdf"
        - "html"
        - "src"
      include_tags:
        - "public"
```

here the book is given a version and two builds 'internal' and 'public' are specified. The public build will only include documents that have the tag 'public' in their frontmatter, through the use of the 'include_tags' attribute. All supported output formats 'pdf', 'html' and 'src' (just copy all sources) are requested in this case. This will lead to four invocations of Jupyter Book (and two custom copy operations for 'src').

To do the builds run: 

``` shell
ichec_handbook book --source_dir $SOURCE_DIR 
```

where `SOURCE_DIR` is the location of the book sources.


# Installation #

If you are only using this project to build books, the container approach is strongly recommended due to complex runtime dependencies. You can follow the container guide in [infra](./infra/README.md).

If you want a full native version, you first need to install the project dependencies. First, `imagemagick` and `cairo` for image format conversion:

``` shell
brew install imagemagick cairo
```

Next, a full Latex environment, on Mac you can use  [MacTeX](https://www.tug.org/mactex/mactex-download.html)

Finally you need a working version of the [Mermaid CLI](https://github.com/mermaid-js/mermaid-cli).


After installing dependencies you can install the project with:

``` shell
pip install ichec_handbook
```

# Contact #

For further information you can contact `james.grogan@ichec.ie`. 

# Copyright #

Copyright 2025 Irish Centre for High End Computing

The software in this repository can be used under the conditions of the GPLv3+ license, which is available for reading in the accompanying `LICENSE` file.

If you are an ICHEC collaborator or National Service user and hope to use this library under different terms please get in touch.
