# Public Artifact Export

This repository is the private working repository for the benchmark and paper.
Do not make this repository public directly, because its Git history contains
manuscript drafts and paper-specific files. Instead, generate a fresh public
artifact repository from a sanitized export.

The export script is:

```bash
python3 python/export_public_artifact.py
```

It creates a clean data/code folder under:

```text
_public_release/iot-benchmark-pack-public
```

The `_public_release/` directory is ignored by Git in this working repository.

## Recommended Workflow

Run a dry run first:

```bash
python3 python/export_public_artifact.py --dry-run
```

Generate or replace the public export:

```bash
python3 python/export_public_artifact.py --force
```

The script refuses to delete an output directory that contains a `.git`
directory. This protects the local public-repository clone from being removed by
accident. Use a separate staging export when updating an already initialized
public repository.

Inspect the generated folder before publishing:

```bash
find _public_release/iot-benchmark-pack-public -maxdepth 2 -type f | sort
```

Check that local-only files are absent:

```bash
find _public_release/iot-benchmark-pack-public -name ".env*" -print
find _public_release/iot-benchmark-pack-public/firmware -name secrets.h -print
```

Check for private local identifiers:

```bash
rg -n "\b(10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|192\.168\.[0-9]{1,3}\.[0-9]{1,3}|172\.(1[6-9]|2[0-9]|3[01])\.[0-9]{1,3}\.[0-9]{1,3})\b|/Users[/]|isam[@]|Isams[-]MacBook[-]Pro[-]2|iot[-]tb2|light[.]ts0001" _public_release/iot-benchmark-pack-public
```

Check that manuscript files are not included:

```bash
rg -n "paper_[d]raft|paper_[s]upplement|ad[h]oc_networks|w1_[p]aper_notes|latency_[d]iagram|figure-1[.]tikz" _public_release/iot-benchmark-pack-public
```

No output from the checks above is the desired result.

## What The Script Does

The script copies tracked repository files into a new export folder, then
sanitizes text files while copying them.

It excludes local-only or manuscript-related material, including:

- `.env` files
- `_public_release/`
- Python cache files
- generated chat snapshots
- `firmware/secrets.h`
- paper drafts, supplements, paper figures, archive notes, and presentation
  source files under `docs/`

It sanitizes text content by replacing:

- private LAN IP addresses with `<private-ip>`
- absolute local user paths with `<local-path>`
- serial device names with `/dev/serial-port`
- MAC addresses with `<mac-address>`
- local host and device labels with generic names
- the local Home Assistant entity id with `light.benchmark_device`

The export also writes:

- `PUBLIC_RELEASE_NOTES.md`
- `PUBLIC_EXPORT_MANIFEST.json`

The public artifact should also contain:

- `LICENSE` for source code
- `DATA_LICENSE.md` for datasets, tables, figures, and documentation
- `CITATION.cff` for GitHub citation metadata
- `.zenodo.json` for Zenodo release metadata

By default, the manifest records copied files and summary counts. It does not
list excluded file names.

## Script Options

Use a custom output directory:

```bash
python3 python/export_public_artifact.py --out /path/to/export
```

Replace an existing export:

```bash
python3 python/export_public_artifact.py --force
```

Preview counts without copying files:

```bash
python3 python/export_public_artifact.py --dry-run
```

Include excluded file names in the manifest for a private audit:

```bash
python3 python/export_public_artifact.py --include-excluded-file-list --force
```

Do not publish an export generated with `--include-excluded-file-list` unless
you have reviewed the manifest.

## Publishing The Export

Publish from the generated export folder as a new repository with fresh history:

```bash
cd _public_release/iot-benchmark-pack-public
git init
git add .
git commit -m "Initial public artifact release"
git branch -M main
git remote add origin https://github.com/isam-aqu/iot-benchmark-pack-public.git
git push -u origin main
```

Do not run these commands from the private working repository root.

After this first push, treat the generated folder as a Git working copy. Do not
run `python3 python/export_public_artifact.py --force` directly over it. For
updates, use a separate staging folder:

```bash
python3 python/export_public_artifact.py --out _public_release/iot-benchmark-pack-public-staging --force
```

Then copy the reviewed staging contents into the local public-repository clone
and commit from that clone.

The public repository is:

```text
https://github.com/isam-aqu/iot-benchmark-pack-public.git
```

The archived artifact DOI is:

```text
https://doi.org/10.5281/zenodo.20137155
```

For later updates, regenerate the export, review it, then commit and push from
the generated export repository.

After the public GitHub repository is updated, create a versioned GitHub release.
If the release changes materially, archive the new release on Zenodo and update
the paper's data and code availability statement with the current release DOI.

Recommended first release metadata:

- Tag: `v1.0.0`
- Title: `IoT Benchmark Pack Public Artifact v1.0.0`
- Description: `Public data, firmware, run metadata, and analysis scripts supporting the measurement-aware heterogeneous IoT evaluation.`

## Updating The Export Rules

If new local-only files are added to the private repository, update
`EXCLUDE_PATTERNS` in `python/export_public_artifact.py`.

If new local identifiers appear in data or metadata, update the sanitization
rules in the same script and rerun the export plus the audit checks above.
