FROM ghcr.io/magfest/ubersystem:super2020_migrated

# install plugins
COPY . plugins/magprime/

RUN /app/env/bin/paver install_deps
