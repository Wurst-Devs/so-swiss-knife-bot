FROM python:3.9-alpine as base

FROM base as builder

WORKDIR /install

RUN apk update && apk add git gcc musl-dev

COPY requirements.txt /requirements.txt

RUN pip install --prefix=/install -r /requirements.txt

FROM base

WORKDIR /app

COPY --from=builder /install /usr/local

COPY . .

CMD [ "sh", "-c", "python src/main.py" ]
