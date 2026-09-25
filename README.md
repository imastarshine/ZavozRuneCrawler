# ZavozRune Crawler
---
ZavozRune Crawler, it's a basic python project, that scans and visits all domain-only links from certain webpages. On new link or content on page it sends a message to telegram channel/direct message.
This project specially developed for crawling [DELTARUNE](https://www.deltarune.com/) webpage. But it can be easily set up for any other websites

## Let's set up this on your system

1. Clone repository
```bash
git clone https://github.com/imastarshine/ZavozRuneCrwaler.git
```

2. Install all dependencies (requires: Python >= 3.12 and Poetry)
```bash
cd ZavozRuneCrawler
poetry install
```

3. Let's configure it
```bash
cp .env-example .env
nano .env
```

- Set up your telegram bot token from @BotFather
- Set up your ID from channel or user id for telegram
- Set up basic URL for scanning and filtering

4. Now we need to plant the sprout
```bash
poetry run python3 scripts/add_link.py
Input new link
> "ANY LINK HERE" (for example: "https://deltarune.com/")
```

5. Now we can start it
```bash
poetry run python3 main.py
```

6. Or you can set up it like Unit
```ini
[Unit]
Description=Zavoz Rune Crawler
After=network.target
[Service]
User=<ANY>
UMask=0002
WorkingDirectory=<YOUR DIR>
ExecStart=<YOUR DIR>/.venv/bin/python <YOUR DIR>/main.py
Restart=always
RestartSec=1800
Environment=PYTHONUNBUFFERED=1
[Install]
WantedBy=multi-user.target
```

## Live example
[TELEGRAM](https://t.me/zavozrune)
