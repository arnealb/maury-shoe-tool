# Schoen aan de voet — v1

Lokale tool die een productfoto van een schoen omzet naar een foto van die schoen aan een voet, via OpenAI **gpt-image-1**.

## Setup (eenmalig)

```bash
# 1. Python 3.10+ vereist
python --version

# 2. Installeer dependencies
pip install -r requirements.txt

# 3. Zet je OpenAI API key
export OPENAI_API_KEY="sk-..."
# Op Windows PowerShell:  $env:OPENAI_API_KEY = "sk-..."
```

API key: https://platform.openai.com/api-keys
Belangrijk: voor `gpt-image-1` heb je een **geverifieerd organization ID** nodig op je OpenAI account. Zie: https://platform.openai.com/settings/organization/general → "Verify Organization". Dat duurt 5 minuten.

## Draaien

```bash
python server.py
```

Open dan **http://127.0.0.1:8000** op je laptop.

### Vanaf je iPhone openen (zelfde wifi als laptop)

1. Vind je laptop-IP:
   - Mac: System Settings → Wi-Fi → Details → IP-adres (iets als `192.168.1.42`)
   - Windows: `ipconfig` in cmd → "IPv4 Address"
2. Op je iPhone (op dezelfde wifi): open Safari, ga naar `http://192.168.1.42:8000` (vervang met jouw IP)
3. Klaar — de upload kan dan ook met foto's uit je iPhone Camera Roll

Als het niet werkt: firewall van je laptop blokkeert vaak poort 8000. Tijdelijk uitzetten of poort 8000 toelaten.

## Gebruik

1. Sleep of kies een schoenfoto
2. Kies een stijl (studio / lifestyle / frontaal)
3. Klik "Genereer"
4. Na 10-30 sec krijg je het resultaat — download rechtsonder

Alle gegenereerde foto's worden ook lokaal bewaard in `outputs/`.

## Wat dit nog NIET doet (komt in v2)

- Folder upload / batch verwerking
- Specifieke "vaste" model/voet aanhouden over alle foto's
- Vergelijking van meerdere stijlen tegelijk
- Webshop integratie

Test eerst met 5–10 schoenen van je ouders. Als de output goed genoeg is, bouwen we v2 uit met batch + folders.

## Kosten

`gpt-image-1` op `quality=high` kost ongeveer $0.17–0.19 per foto van 1024x1024.
- 100 foto's ≈ $17–19
- Wil je goedkoper testen? Zet `quality="medium"` in `server.py` (≈ $0.04) of `"low"` (≈ $0.01). Voor de eerste tests is `medium` meestal voldoende.
# maury-shoe-tool
