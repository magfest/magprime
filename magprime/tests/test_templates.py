import pytest

from uber.tests import collect_template_paths, is_valid_jinja_template


@pytest.mark.parametrize("template_path", collect_template_paths(__file__))
def test_is_valid_jinja_template(template_path):
    is_valid_jinja_template(template_path)
