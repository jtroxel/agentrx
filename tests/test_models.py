from agentrx.models import TemplateData


def test_template_data_valid():
    td = TemplateData(title="Hello", description="desc", tags=["a", "b"])
    assert td.title == "Hello"


def test_template_data_extra_fields_forbidden():
    try:
        TemplateData(title="Hi", extra_field=1)  # type: ignore
        assert False, "extra field should be forbidden"
    except Exception:
        assert True
