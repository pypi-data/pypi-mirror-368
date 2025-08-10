import os
import importlib
import django
from django.conf import settings


def detect_possible_settings_modules(project_name):
    """
    Detect possible settings modules for projects that split settings into multiple files.
    """
    possible_modules = []
    base_path = os.path.join(project_name, "settings")

    if os.path.isdir(base_path):
        for file in os.listdir(base_path):
            if file.endswith(".py") and not file.startswith("__"):
                module_name = file[:-3]
                possible_modules.append(f"{project_name}.settings.{module_name}")
    else:
        possible_modules.append(f"{project_name}.settings")

    return possible_modules


def load_django_settings(settings_module: str = None):
    """
    Load Django settings from a given settings module.
    If none provided, try to auto-detect or prompt user.
    """
    if not settings_module:
        settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")

    if not settings_module:
        # Try auto-detection
        cwd = os.getcwd()
        project_dirs = [
            d
            for d in os.listdir(cwd)
            if os.path.isdir(d) and os.path.exists(os.path.join(d, "settings"))
        ]

        if project_dirs:
            if len(project_dirs) == 1:
                modules = detect_possible_settings_modules(project_dirs[0])
                if len(modules) == 1:
                    settings_module = modules[0]
                else:
                    print("Multiple settings modules found:")
                    for idx, mod in enumerate(modules, start=1):
                        print(f"{idx}. {mod}")
                    choice = input("Select settings module number: ").strip()
                    settings_module = modules[int(choice) - 1]
            else:
                print("Multiple Django projects found in this directory.")
                for idx, proj in enumerate(project_dirs, start=1):
                    print(f"{idx}. {proj}")
                proj_choice = input("Select project number: ").strip()
                chosen_project = project_dirs[int(proj_choice) - 1]
                modules = detect_possible_settings_modules(chosen_project)
                for idx, mod in enumerate(modules, start=1):
                    print(f"{idx}. {mod}")
                choice = input("Select settings module number: ").strip()
                settings_module = modules[int(choice) - 1]
        else:
            settings_module = input(
                "Enter settings module (e.g. myproject.settings.dev): "
            ).strip()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

    try:
        django.setup()
    except Exception as e:
        raise RuntimeError(
            f"Error setting up Django with settings '{settings_module}': {e}"
        )

    return settings


def get_allowed_hosts():
    return getattr(settings, "ALLOWED_HOSTS", [])


def get_installed_apps():
    return getattr(settings, "INSTALLED_APPS", [])


def get_root_urlconf_module():
    root_urlconf = getattr(settings, "ROOT_URLCONF", None)
    if not root_urlconf:
        raise RuntimeError("ROOT_URLCONF is not defined in settings.py")
    return importlib.import_module(root_urlconf)
