import pytest


def pytest_addoption(parser):
    parser.addoption("--openai-key")


@pytest.fixture
def openai_key(request):
    return request.config.getoption("--openai-key")
