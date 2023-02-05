FROM ghcr.io/magfest/ubersystem:super2022

# install plugins
COPY . plugins/magprime/
# RUN git clone --depth 1 --branch super2022 https://github.com/magfest/covid.git plugins/covid

RUN /app/env/bin/paver install_deps
