BASEDIR=$(dirname $0)
python apply-dependencies.py
pushd $BASEDIR
rm -fr dist/*
python -m build
popd