BASEDIR=$(dirname $0)
pushd $BASEDIR
pip install -r dev-requirements.txt -U
pip install -r requirements.txt -U
popd