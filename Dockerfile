FROM debian:stable-slim

MAINTAINER Loïc Paulevé <loic.pauleve@labri.fr>

# adapted from colomoto/colomoto-docker-base

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

ENV PYTHONWARNINGS=ignore
ENTRYPOINT ["/usr/bin/tini", "--", "caspo"]
CMD ["--help"]

RUN apt-get update --fix-missing && \
    mkdir /usr/share/man/man1 && touch /usr/share/man/man1/rmid.1.gz.dpkg-tmp && \
    apt-get install -y --no-install-recommends \
        bzip2 \
        ca-certificates \
        wget \
        libxrender1 libice6 libxext6 libsm6 \
        && \
    apt clean -y && \
    rm -rf /var/lib/apt/lists/*

RUN TINI_VERSION="0.18.0" && \
    wget --quiet https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}-amd64.deb && \
    dpkg -i tini_${TINI_VERSION}-amd64.deb && \
    rm *.deb

RUN CONDA_VERSION="latest" && \
    echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/miniconda/Miniconda3-${CONDA_VERSION}-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    conda update -n base -c defaults conda && \
    conda config --set auto_update_conda False && \
    conda config --set show_channel_urls true \
    conda config --add channels conda-forge && \
    conda config --add channels potassco && \
    conda config --add channels bioasp && \
    conda install -y caspo && \
    conda clean -y --all && rm -rf /opt/conda/pkgs
