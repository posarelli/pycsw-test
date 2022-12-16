FROM geopython/pycsw:2.6.1

USER root

# install curl for healthcheck
RUN apt-get update && \
    apt-get install --yes curl && \
    rm -rf /var/lib/apt/lists/*

# update tools
RUN python3 -m pip install --upgrade pip setuptools

# config log dir
RUN mkdir -p /var/log/pycsw && \
    chown pycsw: -R /var/log/pycsw

# install pycsw-dynamic

WORKDIR /home/pycsw/pycsw-dynamic

RUN chown --recursive pycsw:pycsw .

# initially copy only the requirements files
COPY --chown=pycsw requirements.txt .
RUN python3 -m pip install -r requirements.txt

COPY --chown=pycsw . .
COPY --chown=pycsw pycsw-config-docker.cfg ${PYCSW_CONFIG}

RUN python3 -m pip install -e .


WORKDIR /home/pycsw
EXPOSE 8000
USER pycsw
