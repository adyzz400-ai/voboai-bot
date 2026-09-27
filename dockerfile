FROM golang:1.24-bookworm

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --break-system-packages -r requirements.txt

COPY package.json .
RUN npm install

RUN npx playwright install chromium

COPY . .

RUN go build -o sparx-server ./sparx

CMD ["sh", "-c", "./sparx-server & python3 bot.py"]