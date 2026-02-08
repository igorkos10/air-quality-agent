# Air Quality Agent (Airly -> MariaDB) — JSON-driven pipeline


Autor: Igor Kosecki  
Nr albumu: 79472

Projekt: **Agent do pozyskiwania danych jakości powietrza z zapisem do bazy MariaDB, z logiką sterowaną plikiem JSON i wykonaniem w Pythonie w kontenerze Docker Compose**.
=======
Projekt: **Agent do pozyskiwania danych jakości powietrza z zapisem do bazy MariaDB, z logiką sterowaną plikiem JSON i wykonaniem w Pythonie w kontenerze Docker Compose.**

---

## Co robi agent?

1. Pobiera bieżące pomiary z **Airly API** (dla `installationId`)
2. Waliduje payload wg reguł z JSON
3. Transformuje dane do postaci wierszy (parametr + wartość + timestamp)
4. Zapisuje do **MariaDB** (insert lub upsert)

Logika działania (kolejność kroków i reguły) jest opisana w:

```
config/pipeline.json
```

---

# Wymagania

- Docker Desktop (z włączonym WSL2)
- Docker Compose

---

# Instrukcja uruchomienia (krok po kroku)

## 1 Wejdź do katalogu projektu

Najpierw przejdź do folderu projektu (tam gdzie jest `docker-compose.yml`).

### Windows PowerShell:

```powershell
cd "C:\ścieżka\do\air-quality-agent"
```

### WSL / Linux:

```bash
cd air-quality-agent
```

Wszystkie dalsze komendy należy wykonywać w tym katalogu.

---

## 2 Skopiuj plik środowiskowy

Linux / WSL:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
copy .env.example .env
```

---

## 3 Ustaw klucz Airly

Otwórz plik `.env` i ustaw:

```
AIRLY_API_KEY=twoj_klucz_api
```

---

## 4 (Opcjonalnie) Ustaw installation_id

W pliku:

```
config/pipeline.json
```

zmień wartość:

```json
"installation_id": 122004
```

---

## 5 Uruchom kontenery

```bash
docker compose up -d --build
```

---

## 6 Sprawdź logi agenta

```bash
docker compose logs -f agent
```

---

# Testy 

Testy należy uruchamiać z poziomu Dockera.

Nie należy używać samego `pytest -q` w WSL, ponieważ pytest nie musi być zainstalowany globalnie.

## Poprawne uruchomienie testów:

```bash
docker compose exec agent python -m pytest -q
```

Oczekiwany wynik:

```
6 passed
```

---

# Dostęp do bazy

MariaDB jest dostępna na hoście na porcie:

```
3307
```

Wewnątrz kontenera działa na porcie:

```
3306
```

---

# Konfiguracja JSON

Plik:

```
config/pipeline.json
```

definiuje:

- `agent.loop` – tryb pracy (pętla)
- `agent.interval_seconds` – odstęp między pobraniami
- `source` – źródło danych (Airly) i `installation_id`
- `processing` – reguły walidacji i transformacji
- `storage` – tabela i tryb zapisu (`insert` / `upsert`)
- `steps` – sekwencję kroków wykonywanych przez agenta

Walidacja konfiguracji odbywa się na podstawie:

```
config/schema.pipeline.json
```

---

# Schemat bazy danych

Plik:

```
src/storage/schema.sql
```

Tabela docelowa:

```
measurements
```

Unikalność:

```
(installation_id, measured_at, param)
```

umożliwia bezpieczny UPSERT.

---

# Uruchomienie bez Dockera (opcjonalne)

Jeśli chcesz uruchomić projekt lokalnie:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m src.cpp --config config/pipeline.json --once
```

---

# Uwagi

- Agent startuje dopiero po gotowości bazy (`depends_on` + `healthcheck`)
- Jeśli nie pojawiają się dane w tabeli:
  - sprawdź poprawność `AIRLY_API_KEY`
  - upewnij się, że `installation_id` istnieje w Airly
