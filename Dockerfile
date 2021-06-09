FROM python:3.9-alpine as bas

FROM base as builder

WORKDIR /install

RUN mkdir /install

COPY requirements.txt /requirements.txt

RUN pip install --install-option="--prefix=/install" -r /requirements.txt

FROM base

WORKDIR /app

COPY --from=builder /install /usr/local

COPY . .

CMD [ "sh", "-c", "python src/main.py" ]