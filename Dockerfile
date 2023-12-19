FROM python:3.10.9-bullseye

RUN apt-get update && apt-get install --no-install-recommends -y  \
    zlib1g-dev \
    exiftool \
    libjpeg-dev \
    python3-pythonmagick \
    inkscape \
    xvfb \
    poppler-utils \
    libfile-mimeinfo-perl \
    qpdf \
    libimage-exiftool-perl \
    ffmpeg \
    libreoffice \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir flask==2.0.3 gunicorn==20.1.0 boto3==1.21.17 rsa==4.8 cryptography==36.0.1 Werkzeug==2.2.2

WORKDIR /home

COPY s3_file_browser.py .

COPY templates/ templates/

COPY Dockerfile .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "s3_file_browser:app", "--timeout", "60", "--workers", "2", "--threads", "4"]
