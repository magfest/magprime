FROM ghcr.io/magfest/ubersystem:super2025
ENV uber_plugins=["magprime"]

# install plugins
COPY . plugins/magprime/

RUN uv-installer.sh pip install --system -r requirements.txt;
