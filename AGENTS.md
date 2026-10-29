# Project Guidelines

This is a standalone, offline firmware-reading tool. Keep it independent from camera applications and private research checkouts.

- Use only the Python standard library at runtime unless a dependency is explicitly reviewed and locked.
- Preserve strict output bounds and malformed-input checks in the FFLZ decoder.
- Do not commit firmware images, camera dumps, device identifiers, credentials, generated decode output or third-party vendor trees.
- Do not add flashing, USB, RAM-writing or signature-bypass behavior under the guise of offline unpacking.
- Run `PYTHONPATH=src python3 -m unittest discover -s tests -v` after changes.
- Update `docs/FORMAT.md` when format behavior changes and `docs/VALIDATION.md` when repeating cross-model validation.
