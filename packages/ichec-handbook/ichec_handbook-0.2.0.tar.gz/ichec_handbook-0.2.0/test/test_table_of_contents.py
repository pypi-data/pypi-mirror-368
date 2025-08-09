from iccore.test_utils import get_test_data_dir, get_test_output_dir

from ichec_handbook.document.jupyter_book import toc


def test_table_of_contents():
    toc_file = get_test_data_dir() / "mock_document/_toc.yml"

    contents = toc.read(toc_file)
    contents = toc.from_jupyterbook(contents)
    contents = toc.to_jupyterbook(contents)

    toc_out = get_test_output_dir() / "_toc_test.yml"
    toc.write(toc_out, contents)

    toc_1 = toc.read(toc_out)

    toc_out.unlink()

    assert len(toc_1.parts[0].chapters[2].sections) == 2
