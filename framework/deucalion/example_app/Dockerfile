# syntax=docker/dockerfile:1
# this Dockerfile is for production (building a duecalion sidecar AD application)

FROM python:3.9-slim as runtime

RUN python3 -m pip install -i https://test.pypi.org/simple/ --no-deps deucalion # fout bij het installeren van dependencies, dus voorlopig omzeilen met --no-deps en install upgrade
RUN python3 -m pip install --upgrade deucalion

WORKDIR /deucalion_app
COPY . .
RUN python3 -m pip install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["main.py"]
