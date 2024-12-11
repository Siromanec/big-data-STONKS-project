FROM python:3.11-slim

WORKDIR /app

# RUN apt-get update \
#     && apt-get install --yes --no-install-recommends \
#     build-essential
# RUN apk --no-cache add musl-dev linux-headers g++ gcc make
#
# RUN apk add --update --no-cache py3-numpy

RUN pip install --no-cache-dir matplotlib pandas

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./

CMD ["python", "main.py"]