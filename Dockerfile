FROM svidela/clingo

MAINTAINER Santiago Videla <santiago.videla@gmail.com>

RUN conda install -y pip && pip install -U pip
RUN conda install -y ipython ipywidgets pandas scipy scikit-learn networkx seaborn graphviz joblib
RUN pip install git+git://github.com/bioasp/caspo.git@gringo-python

ENV PYTHONWARNINGS=ignore
ENTRYPOINT ["caspo"]
CMD ["--help"]
