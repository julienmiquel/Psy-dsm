import os
import json
import pytest
from click.testing import CliRunner
from app.batch import batch_process

@pytest.fixture
def runner():
    return CliRunner()

def test_batch_process(runner, tmp_path):
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.json"

    with open(input_file, "w") as f:
        f.write("Test character 1\n")
        f.write("Test character 2\n")

    result = runner.invoke(batch_process, [str(input_file), str(output_file)])

    assert result.exit_code == 0
    assert os.path.exists(output_file)

    with open(output_file, "r") as f:
        profiles = json.load(f)
        assert len(profiles) == 2
