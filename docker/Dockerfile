FROM python:3.10-slim as base
# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
FROM base AS python-deps
# Install pipenv and compilation dependencies
RUN pip install pipenv==2023.2.18
RUN apt-get update && apt-get install -y --no-install-recommends gcc=12.2.1 && rm -rf /var/lib/apt/lists/*
# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy
FROM base AS runtime
# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"
# Create and switch to a new user
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser
# Install application into container
COPY . .
# Run the application
CMD ["python", "./run.py"]
