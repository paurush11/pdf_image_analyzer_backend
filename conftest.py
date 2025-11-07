"""Pytest configuration for Django project."""
import os
import pytest
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


@pytest.fixture(scope='session')
def django_db_setup():
    """Setup database for tests."""
    pass

