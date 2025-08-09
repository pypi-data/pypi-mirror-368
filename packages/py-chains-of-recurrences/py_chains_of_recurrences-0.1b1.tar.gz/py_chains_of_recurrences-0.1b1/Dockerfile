# ./Dockerfile
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
      bash build-essential cmake ninja-build git pkg-config file python3-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /project