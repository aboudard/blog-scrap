# Website scraper

Downloads articles from a blog URL you provide and saves them as Markdown files
in `website-archives`.

## Setup

From the project folder, install the dependencies into the virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run

```powershell
.\.venv\Scripts\python.exe scrap_website.py
```

When prompted, type the blog URL, for example `https://example.com/blog/`.

If HTTPS fails with `CERTIFICATE_VERIFY_FAILED` on a network that inspects TLS,
ask your IT team for its trusted inspection CA certificate in PEM format, then
set Requests' CA bundle for the current PowerShell session:

```powershell
$env:REQUESTS_CA_BUNDLE = "C:\path\to\trusted-ca.pem"
.\.venv\Scripts\python.exe scrap_website.py
```

Do not disable certificate verification with `verify=False`.
