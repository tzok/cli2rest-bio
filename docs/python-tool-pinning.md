# Python Tool Pinning

`rnapolis`, `barnaba`, and `fr3d` now use tool-local `uv` projects and lockfiles.

## Update model

### RNAPOLIS

- Manifest: `rnapolis/pyproject.toml`
- Lockfile: `rnapolis/uv.lock`
- Source: PyPI
- Update mode: automatic via Dependabot `uv` updates

`rnapolis` is intentionally pinned to a released PyPI version instead of a Git SHA.

### Barnaba

- Manifest: `barnaba/pyproject.toml`
- Lockfile: `barnaba/uv.lock`
- Source: `https://github.com/srnas/barnaba`
- Update mode: manual Git SHA pinning

### FR3D

- Latest channel manifest: `fr3d/uv/latest/pyproject.toml`
- Latest channel lockfile: `fr3d/uv/latest/uv.lock`
- Master channel manifest: `fr3d/uv/master/pyproject.toml`
- Master channel lockfile: `fr3d/uv/master/uv.lock`
- Source: `https://github.com/BGSU-RNA/fr3d-python`
- Update mode: manual Git SHA pinning per channel

Both FR3D channels are preserved to match the existing published image behavior.

## Manual SHA pinning

Dependabot is configured to monitor the `uv` projects, but it is not relied on to bump Git SHAs.
Git-based dependency pins for `barnaba` and `fr3d` must be updated manually.

Image rebuild identity includes the tool lockfile checksum, so dependency-only `uv.lock` changes also produce new image tags in CI.

### Barnaba update procedure

1. Choose the target upstream commit in `srnas/barnaba`.
2. Update `tool.uv.sources.barnaba.rev` in `barnaba/pyproject.toml`.
3. Refresh the lockfile:

```bash
uv lock --directory barnaba
```

4. Rebuild and test the image.

### FR3D update procedure

Repeat these steps for each channel independently.

1. Choose the target upstream commit in `BGSU-RNA/fr3d-python`.
2. Update `tool.uv.sources.fr3d.rev` in one of:
   - `fr3d/uv/latest/pyproject.toml`
   - `fr3d/uv/master/pyproject.toml`
3. Refresh the matching lockfile:

```bash
uv lock --directory fr3d/uv/latest
uv lock --directory fr3d/uv/master
```

4. Rebuild and test the image for the updated channel.

## Local validation

Useful commands after changing a pin:

```bash
docker build -t cli2rest-rnapolis ./rnapolis
docker build -t cli2rest-barnaba ./barnaba
docker build -t cli2rest-fr3d ./fr3d
docker build --build-arg FR3D_CHANNEL=master -t cli2rest-fr3d-master ./fr3d
```

Then run the existing integration workflows or local CLI checks against the built image.
