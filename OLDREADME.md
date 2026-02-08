# Air Quality Agent (Airly -> MariaDB) — JSON-driven pipeline

Projekt: **Agent do pozyskiwania danych jakości powietrza z zapisem do bazy MariaDB, z logiką sterowaną plikiem JSON i wykonaniem w Pythonie w kontenerze Docker Compose**.

## Co robi agent?
1. Pobiera bieżące pomiary z **Airly API** (dla `installationId`)
2. Waliduje payload wg reguł z JSON
3. Transformuje dane do postaci wierszy (parametr + wartość + timestamp)
4. Zapisuje do **MariaDB** (insert lub upsert)

Logika działania (kolejność kroków i reguły) jest opisana w `config/pipeline.json`.

---

## Wymagania
- Docker + Docker Compose

## Szybki start

1. Skopiuj plik środowiskowy:
```bash
cp .env.example .env
```

2. Wstaw swój klucz Airly:
- edytuj `.env` i ustaw `AIRLY_API_KEY=...`

3. (Opcjonalnie) ustaw właściwy `installation_id` w `config/pipeline.json`

4. Uruchom całość:
```bash
docker compose up -d --build
```

5. Podgląd logów:
```bash
docker compose logs -f agent
```

Baza MariaDB jest wystawiona na hosta na porcie `3307` (wewnątrz kontenera 3306).

## Konfiguracja JSON

Plik `config/pipeline.json` definiuje:
- `agent.loop` i `agent.interval_seconds` – tryb pętli i odstęp między pobraniami
- `source` – źródło danych (Airly) i `installation_id`
- `processing` – reguły: wymagane pola, dozwolone parametry, zaokrąglanie
- `storage` – tabela oraz tryb zapisu (`insert` / `upsert`)
- `steps` – sekwencja kroków wykonywana przez agenta

Walidacja JSON odbywa się na podstawie `config/schema.pipeline.json`.

## Schemat bazy danych

Plik: `src/storage/schema.sql`

Tabela docelowa: `measurements`  
Unikalność: `(installation_id, measured_at, param)` umożliwia bezpieczny `UPSERT`.

## Uruchomienie jednorazowe (poza Docker)
Jeśli chcesz odpalić jednorazowo lokalnie:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m src.cpp --config config/pipeline.json --once
```

## Testy
```bash
pytest -q
```

## Uwagi
- W Dockerze agent startuje dopiero po gotowości bazy (`depends_on` + `healthcheck`).
- Jeśli nie masz danych w tabeli:
  - sprawdź poprawność `AIRLY_API_KEY`
  - upewnij się, że `installation_id` istnieje i jest dostępny w Airly
