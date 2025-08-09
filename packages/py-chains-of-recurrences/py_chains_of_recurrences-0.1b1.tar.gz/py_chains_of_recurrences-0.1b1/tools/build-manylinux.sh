#!/usr/bin/env bash
set -euo pipefail

ABIS="${ABIS:-cp310-cp310 cp311-cp311 cp312-cp312}"

rm -rf dist wheelhouse && mkdir -p dist wheelhouse

/opt/python/cp312-cp312/bin/python -m pip -q install -U pip build
/opt/python/cp312-cp312/bin/python -m build --sdist

for ABI in $ABIS; do
  /opt/python/$ABI/bin/python -m pip -q install -U pip build
  /opt/python/$ABI/bin/python -m build --wheel
done

# install auditwheel using cp312's pip
/opt/python/cp312-cp312/bin/python -m pip -q install -U pip auditwheel

# repair wheels *with the same interpreter*
for whl in dist/*.whl; do
  /opt/python/cp312-cp312/bin/python -m auditwheel repair "$whl" -w wheelhouse/
done

mv -v wheelhouse/*.whl dist/