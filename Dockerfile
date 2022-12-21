# Create the base stage
FROM python:3.9 AS base

# Update pip and install poetry
RUN pip install -U pip

# Install poetry and add it to the PATH
RUN curl -sSL https://install.python-poetry.org | python
ENV PATH="/root/.local/bin:$PATH"

# Don't create virtual env, instead install globally
RUN poetry config virtualenvs.create false

# Set the working directory
WORKDIR /usr/src/app

# Copy in the poetry manifest files
COPY pyproject.toml .
COPY poetry.lock .

# Install the required dependencies
RUN poetry install --no-dev

#########
# Release
#
# Building on a new slim alpine image, create an image with just what we are releasing
FROM python:3.9-slim AS release

# Copy in the dependencies installed in base
COPY --from=base /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Set the working directory
WORKDIR /usr/src/app

# Copy in just the webapp
COPY . .

ENTRYPOINT [ "python" ]

CMD [ "tempo_flask.py" ]
