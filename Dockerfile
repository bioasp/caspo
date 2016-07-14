FROM svidela/clingo

MAINTAINER Santiago Videla <santiago.videla@gmail.com>

RUN conda install -y pip && pip install -U pip
RUN conda install -y ipython pandas scipy scikit-learn networkx
RUN pip install git+git://github.com/bioasp/caspo.git@gringo-python

ENTRYPOINT ["caspo"]
CMD ["--help"]
