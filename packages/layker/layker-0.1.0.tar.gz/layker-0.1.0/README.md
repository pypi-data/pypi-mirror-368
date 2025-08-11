<!-- README.md (Layker) -->

<div align="center" style="margin-bottom: 18px;">
  <span style="font-size: 44px; line-height: 1; vertical-align: middle;">🐟</span>
  <span style="font-size: 44px; font-weight: bold; letter-spacing: 1.5px; color: #2186C4; vertical-align: middle;">Layker</span>
  <span style="font-size: 44px; line-height: 1; vertical-align: middle;">🐟</span>
  <br>
  <span style="font-size: 16px; color: #444; font-family: monospace; letter-spacing: 0.5px;">
    <b>L</b>akehouse‑<b>A</b>ligned <b>Y</b>AML <b>K</b>it for <b>E</b>ngineering <b>R</b>ules
  </span>
</div>

---

Declarative **table metadata control** for Databricks & Spark.  
Layker turns a YAML spec into **safe, validated DDL** with a built‑in **audit log**.  
If nothing needs to change, Layker exits cleanly. If something must change, you’ll see it first.

---

## What is Layker?

Layker is a Python package for managing **table DDL, metadata, and auditing** with a single YAML file as the source of truth.

**Highlights**
- **Declarative** – author schemas, tags, constraints, and properties in YAML.
- **Diff‑first** – Layker computes a diff against the live table; “no diff” = no work.
- **Safe evolution** – add/rename/drop column intents are detected and gated by required Delta properties.
- **Auditable** – every applied change is logged with **before/after** snapshots and a concise **differences** dictionary.
- **Serverless‑friendly** – gracefully skips `REFRESH TABLE` on serverless (prints a warning).

---

## Installation

Stable:
```bash
pip install layker
```

Latest (main):
```bash
pip install "git+https://github.com/Levi-Gagne/layker.git"
```

Python 3.8+ and Spark 3.3+ are recommended.

---

## Quickstart

### 1) Author a YAML spec
Minimal example (save as `src/layker/resources/example.yaml`):
```yaml
catalog: dq_dev
schema: lmg_sandbox
table: layker_test

columns:
  1:
    name: id
    datatype: bigint
    nullable: false
    active: true
  2:
    name: name
    datatype: string
    nullable: true
    active: true

table_comment: Demo table managed by Layker
table_properties:
  delta.columnMapping.mode: "name"
  delta.minReaderVersion: "2"
  delta.minWriterVersion: "5"

primary_key: [id]
tags:
  domain: demo
  owner: team-data
```

### 2) Sync from Python
```python
from pyspark.sql import SparkSession
from layker.main import run_table_load

spark = SparkSession.builder.appName("layker").getOrCreate()

run_table_load(
    yaml_path="src/layker/resources/example.yaml",
    env="prd",
    dry_run=False,
    mode="all",                 # validate | diff | apply | all
    audit_log_table=True        # True=default audit YAML, False=disable, or str path to an audit YAML
)
```

### 3) Or via CLI
```bash
python -m layker src/layker/resources/example.yaml prd false all true
```

> When `audit_log_table=True`, Layker uses the packaged default:
> `layker/resources/layker_audit.yaml`.  
> You can also pass a custom YAML path. Either way, the **YAML defines the audit table’s location**.

---

## How it works (at a glance)

1. **Validate YAML** → fast fail with exact reasons, or proceed.
2. **Snapshot live table** (if it exists).
3. **Compute differences** between YAML snapshot and table snapshot.
   - If **no changes** (i.e., the diff contains only `full_table_name`), **exit** with a success message and **no audit row** is written.
4. **Validate differences** (schema‑evolution preflight):
   - Detects **add/rename/drop** column intents.
   - Requires Delta properties for evolution:
     - `delta.columnMapping.mode = name`
     - `delta.minReaderVersion = 2`
     - `delta.minWriterVersion = 5`
   - On missing requirements, prints details and exits.
5. **Apply changes** (create/alter) using generated SQL.
6. **Audit** (only if changes were applied and auditing is enabled):
   - Writes a row containing:
     - `before_value` (JSON), `differences` (JSON), `after_value` (JSON)
     - `change_category` (`create` or `update`)
     - `change_key` (human‑readable sequence per table, see below)
     - `env`, `yaml_path`, `fqn`, timestamps, actor, etc.

---

## Audit log model

The default audit YAML (`layker/resources/layker_audit.yaml`) defines these columns (in order):

- **change_id** – UUID per row
- **run_id** – optional job/run identifier
- **env** – environment/catalog prefix
- **yaml_path** – the source YAML path that initiated the change
- **fqn** – fully qualified table name
- **change_category** – `create` or `update` (based on whether a “before” snapshot was present)
- **change_key** – readable sequence per table:
  - First ever create: `create-1`
  - Subsequent updates on that lineage: `create-1~update-1`, `create-1~update-2`, …
  - If the table is later dropped & re‑created: the next lineage becomes `create-2`, etc.
- **before_value** – JSON snapshot before change (may be null on first create)
- **differences** – JSON diff dict that was applied
- **after_value** – JSON snapshot after change
- **notes** – optional free text
- **created_at / created_by / updated_at / updated_by**

Uniqueness expectation: `(fqn, change_key)` is effectively unique over time.

---

## Modes & parameters

- **mode**: `validate` | `diff` | `apply` | `all`
  - `validate`: only YAML validation (exits on success)
  - `diff`: prints proposed changes and exits
  - `apply`: applies changes only
  - `all`: validate → diff → apply → audit
- **audit_log_table**:
  - `False` – disable auditing
  - `True` – use default `layker/resources/layker_audit.yaml`
  - `str` – path to a custom audit YAML (the YAML governs the destination table)
- **No‑op safety**: if there are **no changes**, Layker exits early and **skips audit**.

---

## Notes on serverless

Databricks serverless does **not** support `REFRESH TABLE`.  
Layker detects this and prints a warning; the rest of the flow continues.

---

## Repository layout (typical)

```
src/
  layker/
    __init__.py
    __main__.py
    main.py
    differences.py
    loader.py
    logger.py
    snapshot_yaml.py
    snapshot_table.py
    resources/
      layker_audit.yaml
    utils/
      color.py
      printer.py
      spark.py
      timer.py
      paths.py
      table.py
    validators/
      params.py
      differences.py
```

---

## Troubleshooting

- **Spark Connect / serverless**: Layker avoids schema inference issues by using explicit schemas when writing the audit row.
- **Single quotes in comments**: Layker sanitizes YAML comments to avoid SQL quoting errors.
- **No changes but I still see output**: A diff containing only `full_table_name` means **no change**; Layker exits early with a success message and writes no audit row.

---

## Contributing & License

PRs and issues welcome.  
License: see `LICENSE` in the repo.

<div align="center" style="margin-top: 18px;">
  <span style="font-size: 18px; color: #2186C4; font-weight: bold;">Built for engineers, by engineers.</span><br>
  <span style="font-size: 18px;">🐟&nbsp;LAYKER&nbsp;🐟</span>
</div>