import pytest

from conftest import iter_imported_aliases, SOURCE_PATH, iter_python_files, is_class_import


def test_no_protected_imports_except_for_classes():
    lines = []
    for file in iter_python_files(SOURCE_PATH):
        for alias_, statement in iter_imported_aliases(file):
            if alias_.name.startswith("_") and not is_class_import(alias_, statement):
                lines.append(f"{file}:{statement.lineno}: imports protected name '{alias_.name}'")
    if len(lines) > 0:
        pytest.fail(f"Found {len(lines)} protected imports\n" + "\n".join(lines))
