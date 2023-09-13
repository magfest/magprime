ARG BRANCH=main
FROM ghcr.io/magfest/ubersystem:${BRANCH}

# install plugins
COPY . plugins/magprime/

RUN /app/env/bin/paver install_deps
