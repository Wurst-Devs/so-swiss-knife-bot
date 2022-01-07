FROM python:3.9-alpine as base

FROM base as builder

WORKDIR /install

RUN apk update && apk add git gcc musl-dev

COPY requirements.txt /requirements.txt

RUN pip install --prefix=/install -r /requirements.txt

FROM base

WORKDIR /app

ENV TZ=Europe/Paris
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

VOLUME ["/app/data"]

COPY --from=builder /install /usr/local

RUN mkdir -p data

COPY . .

CMD [ "sh", "-c", "python src/main.py" ]
