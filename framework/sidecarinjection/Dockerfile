# syntax=docker/dockerfile:1

FROM golang:1.17.8-alpine as build

WORKDIR /build

COPY go.mod ./
COPY go.sum ./

RUN go mod download

COPY deucalion-sidecar-injector.go ./
COPY webhook/* ./webhook/
COPY manual/* ./manual/

RUN go build deucalion-sidecar-injector.go

FROM alpine:latest
WORKDIR /app

# not needed in production, only for debugging
# COPY configuration/tls/webhook-tls.pem ./tls/
# COPY configuration/tls/webhook-tls-key.pem ./tls/
COPY --from=build /build/deucalion-sidecar-injector .


ENTRYPOINT ["./deucalion-sidecar-injector"]
