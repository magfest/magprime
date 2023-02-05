FROM ghcr.io/magfest/ubersystem:main

# install plugins
COPY . plugins/magprime/
RUN git clone --depth 1 --branch main https://github.com/magfest/covid.git plugins/covid

RUN /app/env/bin/paver install_deps
