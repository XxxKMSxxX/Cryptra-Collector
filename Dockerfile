FROM python:3.12-slim-bookworm

COPY . .

RUN pip install .

CMD ["sh", "-c", "python -Bum collector ${EXCHANGE} ${CONTRACT} ${SYMBOL} ${AWS_REGION}"]