# shade-agent-py

This is a lightweight python wrapper around the shade-agent-api.

## Usage

For example usage see the [test](./test/src/app.py) 

## Testing locally

Fill out the environment variables and open Docker

Set up virtual environment and install dependencies 
```bash
python -m venv venv
source venv/bin/activate 
pip install -e .
```

Set the contract prefix to `ac-proxy.`

Run the CLI 
```bash
cd test
shade-agent-cli
```

In another terminal run the tests
```bash
python test/src/app.py
```

## Testing on Phala 

Set the contract prefix to `ac-sandbox.`

Build the test image (change your docker ID for your own)
```bash
docker build --no-cache --platform linux/amd64 -t pivortex/my-app:latest -f test/Dockerfile . && docker push pivortex/my-app:latest
```

Edit the app codehash in your `.env.development.local` and `docker-compose.yaml` files

Run the CLI without building 
```bash
cd test
shade-agent-cli --no-build
```

## Publishing 

Build the project 
```bash 
python -m build
```

Test on TestPyPI
```bash
python -m twine check dist/*
```

Publish to TestPyPI
```bash
python -m twine upload --repository testpypi dist/*
```

Publish to PyPI
```bash
python -m twine upload dist/*
```