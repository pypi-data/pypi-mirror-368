ARG IMAGE=python:3.13-alpine

FROM $IMAGE AS builder

RUN python3 -m pip install build

WORKDIR /app

COPY requirements.txt .

COPY . .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt && \
    python3 -m build && \
    mv /app/dist/vibepython-*.whl /wheels

FROM $IMAGE

WORKDIR /app
COPY --from=builder /wheels /wheels

RUN apk add --no-cache musl-locales musl-locales-lang
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONIOENCODING=utf-8

RUN pip install --no-cache /wheels/*

COPY . .

ENTRYPOINT [ "vibepython" ]

# CMD ["/app/main.py"]
