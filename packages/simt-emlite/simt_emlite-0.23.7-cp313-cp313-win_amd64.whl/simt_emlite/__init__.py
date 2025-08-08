def run_tests() -> None:
    import unittest

    loader = unittest.TestLoader()
    suite = loader.discover(".", pattern="test*.py")
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise Exception("Tests failed")


def run_linter() -> None:
    import subprocess

    subprocess.run(["ruff", "check", "."], check=True)
