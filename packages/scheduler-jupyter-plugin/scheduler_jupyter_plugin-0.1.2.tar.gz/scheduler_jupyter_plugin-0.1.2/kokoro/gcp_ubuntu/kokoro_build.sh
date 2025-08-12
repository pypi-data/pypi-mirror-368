#!/bin/bash

# Fail on any error.
set -e

# Display commands being run.
# WARNING: please only enable 'set -x' if necessary for debugging, and be very
#  careful if you handle credentials (e.g. from Keystore) with 'set -x':
#  statements like "export VAR=$(cat /tmp/keystore/credentials)" will result in
#  the credentials being printed in build logs.
#  Additionally, recursive invocation with credentials as command-line
#  parameters, will print the full command, with credentials, in the build logs.
# set -x

# Code under repo is checked out to ${KOKORO_ARTIFACTS_DIR}/github.
# The final directory name in this path is determined by the scm name specified
# in the job configuration.

export PATH="$HOME/.local/bin:$PATH"

# configure gcloud
gcloud config set project deeplearning-platform
gcloud config set compute/region us-central1

# Install dependencies.
sudo apt-get update
sudo apt-get install -y --no-install-recommends git curl
curl -sL https://deb.nodesource.com/setup_18.x | sudo bash -
sudo apt-get --assume-yes install python3 python3-pip nodejs python3-venv

# Install latest jupyter lab and build.
python3 -m venv latest
source latest/bin/activate
pip install jupyterlab build

# Navigate to repo.
cd "${KOKORO_ARTIFACTS_DIR}/github/scheduler-jupyter-plugin"

# Aslo build python packages to dist/
python3 -m build
echo "Package built into dist/."

# install the build
pip install dist/*.whl
echo "Package installed from wheel."

# Run Playwright Tests
cd ./ui-tests
jlpm install
jlpm playwright install
# Installs low-level dependencies required for playwright to launch browsers.
jlpm playwright install-deps
PLAYWRIGHT_JUNIT_OUTPUT_NAME=test-results-latest/sponge_log.xml jlpm playwright test --reporter=junit --output="test-results-latest"
echo "Playwright tests completed."

deactivate
