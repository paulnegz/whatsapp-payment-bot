FROM python:3.11

# Install Chrome
RUN apt-get update && apt-get install tesseract-ocr curl unzip -yf && \
    apt-get install -y dbus-x11 && \
    curl https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o /chrome.deb && \
    dpkg -i /chrome.deb || apt-get install -yf && \
    rm /chrome.deb

RUN apt install -yf wget build-essential libncursesw5-dev libssl-dev libsqlite3-dev && \
    apt install -yf libc6-dev libbz2-dev libffi-dev zlib1g-dev libgdbm-dev && \
    DEBIAN_FRONTEND=noninteractive apt install -y python3-xlib python3-tk python3-dev tk-dev && \
    apt install -y xvfb xserver-xephyr && \
    Xvfb :99 -ac &
ENV DISPLAY=:99

WORKDIR /app

ADD . .

RUN pip install --upgrade pip && \
    pip install virtualenv && \
    virtualenv .venv && \
    /bin/bash -c "source .venv/bin/activate" && \
    pip install --no-cache-dir -r requirements.txt

CMD ["python", "."]
