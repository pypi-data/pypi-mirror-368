#!/usr/bin/env bash
set -euo pipefail

PKG_DIR="${PKG_DIR:-py_cr}"
BUILD_TYPE="${BUILD_TYPE:-Release}"

mkdir -p build/dev
cmake -S . -B build/dev -G Ninja -DCMAKE_BUILD_TYPE="${BUILD_TYPE}"
cmake --build build/dev -j

so="$(find build/dev -type f \( -name '*.so' -o -name '*.pyd' \) -print -quit || true)"
if [[ -z "${so:-}" ]]; then
  echo "ERROR: no extension module found under build/dev" >&2
  cmake --build build/dev --target help || true
  exit 1
fi

mkdir -p "$PKG_DIR"
rm -f "$PKG_DIR"/*.so "$PKG_DIR"/*.pyd 2>/dev/null || true
cp -v -- "$so" "$PKG_DIR/"
echo "Copied $(basename "$so") -> $PKG_DIR/"