BASEDIR=$(dirname $0)
pushd $BASEDIR
python apply-dependencies.py
rm -fr dist/*
python -m build
popd