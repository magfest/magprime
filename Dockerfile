FROM ghcr.io/magfest/ubersystem:main

# Install plugins
RUN git clone https://github.com/magfest/covid.git plugins/covid

RUN /app/env/bin/paver install_deps
