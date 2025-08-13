FROM python:3.12-slim
MAINTAINER Grigory Markin "gmn@eacg.de"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    maven \
    npm \
    nuget \
    gradle \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir -p /tmp/ts-scan
WORKDIR /tmp/ts-scan

COPY ./src ./src
COPY ./pyproject.toml ./LICENSE ./

RUN pip install ./

ENTRYPOINT ["ts-scan"]
CMD []