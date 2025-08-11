"""Test the imports in the sweepexp/__init__.py file."""
import pytest

import sweepexp as test_module

all_imports = []
for mod in test_module.all_modules_by_origin.values():
    all_imports.extend(mod)
for mod in test_module.all_imports_by_origin.values():
    all_imports.extend(mod)

# Remove SweepExpMPI from the imports as it requires mpi4py
all_imports.remove("SweepExpMPI")

@pytest.mark.parametrize("import_name", all_imports)
def test_module_import(import_name):
    attr = getattr(test_module, import_name)
    assert attr is not None
