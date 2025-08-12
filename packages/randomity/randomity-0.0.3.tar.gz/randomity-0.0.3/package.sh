set -e

echo "Building the Python package..."

rm -rf dist/*

python -m build

echo "Package built successfully. Uploading to PyPI..."

twine upload dist/*

echo "Package uploaded successfully!"