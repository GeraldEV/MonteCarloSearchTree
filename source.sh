DIR=$(dirname $(readlink -f $0))
echo "Adding $DIR/lib/ to PYTHONPATH"
export PYTHONPATH=$PYTHONPATH:$DIR/lib/
