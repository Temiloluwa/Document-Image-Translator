import pytest


# You can add shared fixtures here if needed
@pytest.fixture(autouse=True)
def always_pass():
    # Dummy fixture for demonstration
    yield
