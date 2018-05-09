FROM python:alpine
WORKDIR /src/Blurplefied
COPY . .
RUN apk update && \
    apk upgrade && \
    apk add git \
            zlib-dev \
            jpeg-dev \
            build-base \
            libwebp \
            libwebp-dev \
            libpng \
            libpng-dev && \
    pip install -r requirements.txt
ENTRYPOINT ["python", "blurple.py"]
