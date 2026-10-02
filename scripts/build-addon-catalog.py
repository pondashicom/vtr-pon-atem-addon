#!/usr/bin/env python3
"""Generate the static v1 add-on catalog from already built packages."""

import argparse
import hashlib
import json
import pathlib
import re
import sys
import zipfile


BASE = "https://pondashi.com/vtr-pon/addon/download/"
CONTRACTS = {
    "vtr-pon-atem-addon": "switcher-addon-abi-v1",
    "vtr-pon-network-video-addon": "network-video-abi-v2",
    "vtr-pon-vst3-addon": "vst-protocol-v2",
    "vtr-pon-decklink-addon": "decklink-media-abi-v1",
}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("packages", type=pathlib.Path, nargs="+")
    args = parser.parse_args()
    if len(args.packages) > 4:
        parser.error("the v1 catalog allows at most four packages")
    entries = []
    seen = set()
    for path in args.packages:
        try:
            with zipfile.ZipFile(path) as archive:
                manifest = json.loads(archive.read("manifest.json"),
                                      object_pairs_hook=unique_object)
                agreements = manifest.get("agreements")
                if not isinstance(agreements, list) or not agreements or len(agreements) > 16:
                    raise ValueError("the package needs declared agreement documents")
                agreement_paths = set()
                for item in agreements:
                    if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
                        raise ValueError("invalid agreement declaration")
                    name, digest = item["path"], item["sha256"]
                    if (not isinstance(name, str) or not name.startswith("licenses/") or
                            name.casefold() in agreement_paths or
                            not isinstance(digest, str) or
                            not re.fullmatch(r"[0-9a-f]{64}", digest) or
                            hashlib.sha256(archive.read(name)).hexdigest() != digest):
                        raise ValueError("missing or changed agreement document")
                    agreement_paths.add(name.casefold())
        except (OSError, KeyError, ValueError, zipfile.BadZipFile) as exc:
            parser.error(f"could not read {path}: {exc}")
        addon_id = manifest.get("id")
        version = manifest.get("version")
        if (addon_id not in CONTRACTS or addon_id in seen or
                manifest.get("formatVersion") != 2 or
                manifest.get("contract") != CONTRACTS[addon_id] or
                not isinstance(version, str) or
                not re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", version) or
                path.name != f"{addon_id}-{version}-windows-x64.vtrponaddon"):
            parser.error(f"invalid or duplicate add-on package: {path}")
        seen.add(addon_id)
        entries.append({"id": addon_id, "version": version,
                        "url": BASE + path.name,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"formatVersion": 1,
                                       "packages": sorted(entries, key=lambda item: item["id"])},
                                      ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
