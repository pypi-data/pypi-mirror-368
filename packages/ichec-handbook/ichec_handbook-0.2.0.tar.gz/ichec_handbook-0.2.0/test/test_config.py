from iccore.serialization import read_yaml
from iccore.test_utils import get_test_data_dir, get_test_output_dir

from ichec_handbook.document import config


def test_config():

    config_file = get_test_data_dir() / "mock_document/_config.yml"

    original_config = read_yaml(config_file)
    doc_config = config.read(config_file)

    config_out = get_test_output_dir() / "config_out.yml"
    config.write(config_out, original_config, doc_config)

    config1 = config.read(config_out)

    assert doc_config.project_name == config1.project_name

    config_out.unlink()
