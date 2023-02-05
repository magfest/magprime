FROM ghcr.io/magfest/ubersystem:super2023

# install plugins
COPY . plugins/magprime/
RUN git clone --depth 1 --branch super2023 https://github.com/magfest/covid.git plugins/covid

RUN /app/env/bin/paver install_deps
