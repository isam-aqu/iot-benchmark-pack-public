# Public Artifact Export

This folder was generated from the private working repository by
`python/export_public_artifact.py`.

The export is intended to contain the data, firmware, and analysis scripts needed
to reproduce the reported measurements. It intentionally excludes manuscript
drafts, paper conversion files, private local environment files, and generated
chat snapshots.

Sanitization applied during export:

- private LAN IP addresses are replaced with `<private-ip>`
- absolute local user paths are replaced with `<local-path>`
- serial device names are replaced with `/dev/serial-port`
- local host/device labels are generalized
- the local Home Assistant entity id is replaced with `light.benchmark_device`

Export summary:

- copied files: 3417
- text files sanitized: 3379
- excluded tracked files: 45

Before publishing, inspect this folder, initialize it as a fresh Git repository,
and create the public GitHub release or Zenodo archive from the fresh repository.
