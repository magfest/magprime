ARG BRANCH=super2025
FROM ghcr.io/magfest/ubersystem:${BRANCH}
ENV uber_plugins=["magprime"]

# install plugins
COPY . plugins/magprime/

RUN uv pip install --system -r plugins/magprime/requirements.txt
