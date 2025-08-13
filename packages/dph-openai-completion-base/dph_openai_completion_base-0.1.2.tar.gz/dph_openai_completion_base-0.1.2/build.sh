python3 -m venv venv
source venv/bin/activate
python3 -m pip install build twine
python3 -m build

# python3 -m twine upload dist/*
