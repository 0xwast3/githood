# GITHOOD

**One spec in, one repo out.**

`githood` reads a one-page spec and writes a complete trading-bot repository:
source, tests, `Dockerfile`, GitHub Actions CI, `.env.example`, a git repo with
the first commit already made, and a receipt of everything it wrote.

No frameworks, no services, no database. Standard library only.

```
$ githood new examples/momentum.spec.md
Momentum Paper Trader -> momentum-paper-trader/
  17 files · 6.9kb · 25ms · git: initialised · 1 commit
  receipt: runs/2026-09-06/receipt-090840.json

next:
  cd momentum-paper-trader && cp .env.example .env && make test
```

---

## Why

Most "AI writes your app" output is a folder you cannot rebuild. githood takes
the opposite position: **the spec is the source of truth, the repo is an
artifact.** Change the spec, run it again, get the same tree. Every number in
`risk.py` came from a line you wrote; nothing was invented on the way.

Three rules the generator holds itself to:

1. every generated file is regenerable — your edits live in `.env` and your own
   modules, never inside what githood rewrites;
2. CI exists on the first commit, not after the first outage;
3. nothing ships in live mode by default. The broker adapters refuse to
   construct with `live=True` until a human implements and reviews the order
   path.

## Install

```bash
git clone https://github.com/your-handle/githood
cd githood
pip install -e .          # gives you the `githood` command
```

Python 3.9+. There are no runtime dependencies.

## Use

```bash
githood plan examples/momentum.spec.md   # print the tree, write nothing
githood new  examples/momentum.spec.md   # write it
githood new spec.md -o ./bots/alpha --no-git --force
```

| flag | what it does |
| --- | --- |
| `-o, --out` | output directory (default: the slugified project name) |
| `--force` | overwrite a non-empty directory |
| `--no-git` | skip `git init` and the first commit |
| `--dry-run` | say what would happen, touch nothing |

## The spec format

A title, some `key: value` lines, and a list of rules. That is the whole
language.

```markdown
# Momentum Paper Trader

broker: robinhood
symbols: AAPL, MSFT, NVDA
timeframe: 5m
max_position: 10%
stop_loss: 2%
cash: 10000

rules:
- buy when the 20 period average crosses above the 50
- sell when the 20 period average crosses back below the 50
- flatten everything fifteen minutes before the close
```

| key | default | notes |
| --- | --- | --- |
| `broker` | `paper` | one of `robinhood`, `alpaca`, `paper` |
| `symbols` | `AAPL` | comma separated |
| `timeframe` | `5m` | free text, copied into the strategy |
| `max_position` | `0.10` | share of equity per position, `%` accepted |
| `stop_loss` | `0.02` | per position, `%` accepted |
| `cash` | `10000` | starting paper equity |

Unknown keys are not an error — they are kept and copied into the generated
README, so nothing a human wrote gets dropped. A spec with no rules is refused:
a bot with no rules is a random number generator.

## What it writes

```
momentum-paper-trader/
├── README.md              the spec, restated for whoever opens the repo
├── .env.example           keys go here; .env is gitignored
├── .gitignore
├── requirements.txt
├── Makefile               make run · make test · make image · make ship
├── Dockerfile             multi-stage, python:3.12-slim
├── compose.yml            bot + mounted runs/
├── .github/workflows/
│   └── ci.yml             unittest + docker build on every push
├── src/
│   ├── main.py            one pass: quote, decide, size, submit
│   ├── strategy.py        signals in, orders out (your rules as comments)
│   ├── risk.py            the only file allowed to say no
│   └── broker/
│       ├── base.py        the interface every venue answers
│       └── robinhood.py   paper-mode adapter, live path left to you
├── tests/test_risk.py     the caps from your spec, asserted
└── runs/                  receipts, never edited by hand
```

`make test` passes in the generated repo immediately — that is covered by
githood's own test suite, which scaffolds a project into a temp directory and
runs the child project's tests.

## Receipts

Every pass appends to `runs/trace.log` and drops a JSON receipt:

```json
{
  "at": "2026-09-06T09:08:40+00:00",
  "spec": "examples/momentum.spec.md",
  "project": "Momentum Paper Trader",
  "broker": "robinhood",
  "risk": { "max_position": 0.1, "stop_loss": 0.02 },
  "files": ["README.md", "..."],
  "bytes": 7061,
  "ms": 25,
  "git": "initialised · 1 commit"
}
```

If you cannot say which pass wrote a file and why, you do not have a generator,
you have a folder.

## Layout of this repo

```
githood/
├── cli.py          argparse front door
├── spec.py         the spec language and its errors
├── scaffold.py     writes the tree, runs git init
├── templates.py    every generated file, as one flat table
└── receipts.py     runs/ receipts and the trace log
tests/              spec parsing, scaffolding, and the child repo's own tests
examples/           two specs to start from
```

## Development

```bash
python -m unittest discover -s tests -q
```

Adding a broker: drop a `{{broker}}` block in `templates.py`, add the name to
`BROKERS` in `spec.py`, done. Adding a file to the generated repo: add it to
`plan()` and to the `files` table in `scaffold.py` — those two lists are
asserted against each other by the test suite, so they cannot drift.

## Safety

Generated adapters are paper-mode stubs. They return placeholder prices and
fake fills so the loop can be tested end to end. Implementing a live order path
is deliberately left to you, and reviewed by you. Nothing in this repository is
financial advice.

## License

MIT — see [LICENSE](LICENSE).
