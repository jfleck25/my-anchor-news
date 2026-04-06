🎯 **What:** Removed the unused local `pool` import in `main.py` by changing `from psycopg2 import pool` to `import psycopg2.pool`.

💡 **Why:** `from psycopg2 import pool` defines `pool` as a local variable which is never used directly, as the code uses the fully-qualified `psycopg2.pool.ThreadedConnectionPool`. Simply removing the import statement isn't viable because `import psycopg2` does not automatically load the `pool` submodule. Changing to `import psycopg2.pool` correctly resolves the linter warning about an unused local while ensuring the submodule is loaded properly.

✅ **Verification:** Verified via `flake8 main.py --select=F401` that the unused import warning is resolved. Verified via `pytest` that tests pass without throwing `AttributeError: module 'psycopg2' has no attribute 'pool'`. Tested loading module successfully using local venv.

✨ **Result:** A cleaner codebase with fewer linter warnings while maintaining robust database pooling functionality.
