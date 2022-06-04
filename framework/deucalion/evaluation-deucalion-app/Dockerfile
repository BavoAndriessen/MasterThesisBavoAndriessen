# syntax=docker/dockerfile:1
# this Dockerfile is for production (building a duecalion sidecar AD application)

FROM python:3.9-slim as runtime

RUN python3 -m pip install -i https://test.pypi.org/simple/ --no-deps deucalion # fout bij het installeren van dependencies, dus voorlopig omzeilen met --no-deps en install upgrade
RUN python3 -m pip install --upgrade deucalion

# log output immediately
#PYTHONUNBUFFERED=1

WORKDIR /deucalion_app
COPY . .
ENTRYPOINT ["python3"]
CMD ["main.py"]
