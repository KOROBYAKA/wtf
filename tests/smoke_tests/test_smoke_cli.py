import wtf
import shutil
import subprocess

def test_import_ap():
    from wtf.ap import Ap

    assert Ap is not None

def test_import_package():
    assert wtf is not None

def test_wtf_entrypoint_exists():
    assert shutil.which("wtf") is not None

def test_wtf_help_does_not_crash():
    result = subprocess.run(
        ["wtf", "--help"],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0

