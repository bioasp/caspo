FROM continuumio/miniconda3:latest

ENTRYPOINT ["/usr/bin/tini", "--", "caspo"]

RUN TINI_VERSION="0.19.0" && \
    wget --quiet https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}-amd64.deb && \
    dpkg -i tini_${TINI_VERSION}-amd64.deb && \
    rm *.deb

ARG CASPO_VERSION
RUN conda install -y -c conda-forge -c bioasp caspo=${CASPO_VERSION} && \
    conda clean -y --all && rm -rf /opt/conda/pkgs
