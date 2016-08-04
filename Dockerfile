FROM svidela/clingo

MAINTAINER Santiago Videla <santiago.videla@gmail.com>

RUN conda install -y pip && pip install -U pip
RUN conda install -y pandas scipy scikit-learn networkx seaborn graphviz joblib
RUN pip install caspo

ENV PYTHONWARNINGS=ignore
ENTRYPOINT ["caspo"]
CMD ["--help"]
