ARG BRANCH=main
FROM ghcr.io/magfest/ubersystem:${BRANCH}
ENV uber_plugins=["magprime"]

# install plugins
COPY . plugins/magprime/

RUN /root/.local/bin/uv pip install --system -r requirements.txt;
