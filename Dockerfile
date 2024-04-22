ARG BRANCH=main
FROM ghcr.io/magfest/ubersystem:${BRANCH}
ENV uber_plugins=["magprime"]

# install plugins
COPY . plugins/magprime/

RUN /app/env/bin/paver install_deps
