import shutil
from pathlib import Path

from iccore.test_utils import get_test_data_dir, get_test_output_dir

from ichec_handbook.document.jupyter_book import toc as jb_toc
from ichec_handbook.document import config, toc
from ichec_handbook.rendering.context import RenderContext
from ichec_handbook.rendering.book import render


def test_book_publish():
    content_root = get_test_data_dir() / "mock_document"

    content = toc.load_content(
        content_root, jb_toc.from_jupyterbook(jb_toc.read(content_root / "_toc.yml"))
    )

    browser_config = Path(__file__).parent.parent / "infra/local/puppeteer-config.json"

    base_config = config.read(content_root / "_config.yml")
    base_config = base_config.model_copy(update={"tools": {"mermaid": browser_config}})

    build_dir = get_test_output_dir()
    ctx = RenderContext(
        source_dir=content_root,
        build_dir=build_dir,
        config=base_config,
    )

    render(content, ctx)

    shutil.rmtree(build_dir)
