## 
# Build:
# docker build --build-arg http_proxy=$HTTP_PROXY --build-arg https_proxy=$HTTPS_PROXY -t svidela/caspo .
# 
# Run:
# docker run -t -i svidela/caspo
##
FROM svidela/clingo

MAINTAINER Santiago Videla <santiago.videla@gmail.com>

RUN conda install -y pip ipython numpy pandas scipy scikit-learn networkx && pip install -U pip && pip install caspo

