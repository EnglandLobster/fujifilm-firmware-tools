# Contributing

## Scope

Keep the project focused on offline, read-only DAT and FFLZ analysis. Flashing, USB transport, RAM writes, signature bypasses, and private camera research data are outside this repository.

## Requirements

- Python 3.10 or newer.
- No runtime dependencies outside the Python standard library without prior discussion.
- Preserve bounded decoding, exact output-length checks, and useful malformed-input errors.
- Add or update synthetic tests for every behavior change.

Run the full test suite before submitting a change:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Also exercise the installed command when changing the CLI or packaging:

```sh
python -m pip install -e .
fujitools --help
```

## Data and confidentiality

Do not commit DAT firmware, NAND/RAM dumps, generated decode output, device serial numbers, access tokens, or personal research material. Test fixtures must be synthetic. When reporting cross-model validation, record the official source URL, firmware version, input SHA-256, decoder results, and any unsupported regions without attaching the firmware itself.

## Documentation

Update `docs/FORMAT.md` for format changes, `docs/VALIDATION.md` for new validation evidence, and both README language variants when user-facing commands or limitations change.
