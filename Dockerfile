FROM continuumio/miniconda3:latest

ARG CASPO_VERSION
RUN conda install -y -c conda-forge -c bioasp caspo=${CASPO_VERSION} && \
    conda clean -y --all && rm -rf /opt/conda/pkgs
