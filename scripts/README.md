# Building release packages

Build the Release binaries from a clean checkout of `v0.3.0`, following BUILDING.md. Then run the following command with Python 3:

```powershell
py -3 scripts/package-release.py --build-dir build-release --output-dir packages
```

For VST3, collect the Qt 6.8.3 plug-ins `imageformats/qgif.dll`, `qico.dll`, `qjpeg.dll`, and `qsvg.dll` into `audio-addons/imageformats/`, in addition to the files copied by the deployment tool. Copy the DXC/DXIL DLLs from the Windows SDK's `Redist/D3D/x64` directory and the DLLs from Visual Studio's `VC/Redist/MSVC/.../x64/Microsoft.VC143.CRT/` directory into the same folder, using the explicit file lists in release-config.json. Do not copy SDKs, redistributable installers, unnecessary Qt plug-ins, or users' VST3 plug-ins.

The packaging script checks the source checkout's Git status and tag, the Release build configuration, the explicitly listed payload files, Windows x64 PE binaries, UTF-8 documents, and SHA-256 checksums of the agreement documents. It does not overwrite existing output. These checks do not replace runtime or hardware testing.

Once all four add-on packages are ready, generate a candidate catalog:

```powershell
py -3 scripts/build-addon-catalog.py --output packages/catalog.json packages/*.vtrponaddon
```

When running the catalog command in PowerShell, pass the four package filenames explicitly rather than passing a wildcard to Python. The catalog uses URLs under the official `/vtr-pon/addon/download/` path and SHA-256 checksums calculated from the actual package files. Publish the files and catalog as part of the release process.
