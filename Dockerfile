FROM python:3.8

RUN apt -y update && \
    apt install -y postgresql

ENV WORKDIR /

WORKDIR $WORKDIR

COPY ./.env ./Pipfile ./Pipfile.lock $WORKDIR

RUN pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install --system --ignore-pipfile --deploy

COPY . $WORKDIR

CMD ["./wait.sh", "python", "discordbot.py"]