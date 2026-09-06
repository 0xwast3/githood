# Contributing

The rule that keeps this repo small: **templates are data, code is plumbing.**

- a new generated file → add it to `plan()` and to the `files` table in
  `scaffold.py`, and put its body in `templates.py`. The test suite asserts the
  two lists agree, so they cannot drift apart.
- a new broker → add the name to `BROKERS` in `spec.py`. `templates.BROKER_IMPL`
  is rendered per broker, so nothing else needs touching.
- a new spec key → parse it in `spec.parse`, give it a default on `Spec`, and
  expose it through `scaffold._values` so templates can use `{{your_key}}`.

Before opening a PR:

```bash
make test    # unit tests + the generated repo's own tests
make demo    # scaffold into .demo and run it
```

Keep dependencies at zero. If something needs a library, it probably belongs in
the generated repo's `requirements.txt`, not in githood.
