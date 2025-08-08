import inspect

from settings_models import common


def create_pages():
    schema_dict = {
        "openapi": "3.0.0",
        "info": {"title": "Settings Definitions", "version": "1.0.0"}
    }

    for name, obj in inspect.getmembers(common):
        if inspect.isclass(obj) and issubclass(obj, common.SettingsModel) and obj != common.SettingsModel:
            print(obj.schema_json())


if __name__ == "__main__":
    create_pages()
