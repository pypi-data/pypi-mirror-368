FROM python:3.12-slim

# install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# update pip
RUN python -m pip install --upgrade pip

# install uv
RUN pip install uv

COPY .git .git
COPY pyproject.toml pyproject.toml
COPY src/ src/
COPY scripts/ scripts/

## copy the scripts from the local directory to the container
## note: pymlt package is installed via uv from pypi
#COPY ./ /app/
#
## set the working directory in the container
#WORKDIR /app
#
## set the environment variable
#ENV PYTHONPATH="/app"

# install package
RUN uv sync  # --all-groups

# Default command
ENTRYPOINT ["python", "-u"]
CMD ["scripts/train.py"]