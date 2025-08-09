"""
Module to support rendering documents to disk for a given
build context
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Callable
from functools import partial

from iccore import filesystem as fs

import ictasks
from ictasks import Task

from ..document import toc, config
from ..rendering import media
from ..tags import TagFilter

from .context import RenderContext, replace_dirs

logger = logging.getLogger(__name__)


def _copy_media_files(contents: toc.TableOfContents, ctx: RenderContext, path: Path):
    media_filenames = [Path(f).name for f in contents.images]

    for f in ctx.media_dir.iterdir():
        if f.is_file() and f.name in media_filenames:
            fs.copy_file(f, path / ctx.config.media_dir)

    if ctx.media_build_dir.exists():
        for f in ctx.media_build_dir.iterdir():
            if f.is_file() and f.name in media_filenames:
                fs.copy_file(f, path / ctx.config.media_dir)


def _make_src_archive(path: Path, build_ctx: RenderContext, ctx: RenderContext):
    src_archive = path / "src_archive"
    os.makedirs(src_archive, exist_ok=True)
    shutil.copytree(path / "src", src_archive / "src")
    shutil.copy(path / "_config.yml", src_archive)
    shutil.copy(path / "_toc.yml", src_archive)

    fs.make_archive(
        build_ctx.build_dir / f"{ctx.config.project_name}_src",
        "zip",
        src_archive,
    )

    shutil.rmtree(src_archive)


def _render_build(
    contents: toc.TableOfContents,
    ctx: RenderContext,
    build: config.Build,
    copy_sources_func: Callable,
    build_funcs: dict[str, Callable],
):
    logger.info("Start rendering build: %s", build.name)

    build_dir = ctx.build_dir / build.name
    fs.clear_dir(build_dir)

    pred = TagFilter(includes=build.include_tags, excludes=build.exclude_tags)
    filtered_contents = toc.filter_children(contents, lambda x: pred(x))

    logger.info("Copying source files")
    copy_sources_func(filtered_contents, ctx, build)

    logger.info("Copying media files")
    _copy_media_files(filtered_contents, ctx, build_dir)

    build_ctx = replace_dirs(ctx, build_dir)
    os.makedirs(build_ctx.build_dir, exist_ok=True)
    logger.info("Rendering with %s", build_ctx)

    if "src" in build.outputs:
        logger.info("Making src archive")
        _make_src_archive(build_dir, build_ctx, ctx)

    for fmt, func in build_funcs.items():
        if fmt in build.outputs:
            logger.info("Rendering format: %s", fmt)
            func(ctx.config.project_name, build_ctx)

    logger.info("Finished rendering build: %s", build.name)


def _task_func(render_func: Callable, _: Task):
    render_func()


def render(
    contents: toc.TableOfContents,
    ctx: RenderContext,
    copy_sources_func: Callable,
    build_funcs: dict[str, Callable],
):
    """
    Render a document to disk for a given render context. User provided callbacks are
    to copy book sources to the output archive and build functions for supported
    formats.

    Particular document types, such as Book, provide suitable callbacks for each.

    :param TableOfContents contents: The content to render
    :param RenderContext ctx: The settings for the render
    :param Callable copy_sources_func: Function to copy document source files to output
    :param dict[str, Callable] build_funcs: Function to build the document per format
    """

    logger.info("Rendering document with: %s", ctx)

    media.convert(
        ctx.media_dir, ctx.media_build_dir, ctx.conversion_dir, ctx.config.tools
    )

    logger.info("Launching %d render tasks:", len(ctx.config.builds))
    tasks = []
    for build in ctx.config.builds:
        render_func = partial(
            _render_build, contents, ctx, build, copy_sources_func, build_funcs
        )
        tasks.append(Task(launch_func=partial(_task_func, render_func)))
    ictasks.run_funcs(tasks)

    logger.info("Finished render tasks")
