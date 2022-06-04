# syntax=docker/dockerfile:1
# this Dockerfile is for development only

FROM python:3.9-slim-buster as build
WORKDIR /build

RUN python3 -m pip install --upgrade build

COPY deucalionframework/ ./deucalionframework
WORKDIR /build/deucalionframework
RUN python3 -m build
RUN python3 -m pip install --user dist/*.whl


FROM python:3.9-slim as runtime
COPY --from=build /root/.local /root/.local

WORKDIR /example_app
COPY example_app/ .
RUN python3 -m pip install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["main.py"]
