# Pierścień

"Jeden by wszystkimi rządzić".

Jeśli to czytasz to znaczy, że musisz wprowadzić zmiany w Pierścieniu lub dodać do niego nowe funkcjonalności, co oznacza, że teraz Ty zajmujesz się tym projektem. Wyrazy współczucia.

Poniżej znajdują się kroki, które mogą pomóc w uruchomieniu go w środowisku developerskim i produkcyjnym.

**Ważne!** Pamiętaj, że do poprawnego działania aplikacji i skutecznego połączenia z Mocarzem niezbędne jest połączenie z VPNem!

## Dane do plików .env i dane dostępu do serwera

Dane znajdują się w [Google Secret Manager](https://console.cloud.google.com/security/secret-manager?authuser=2&project=pierscien-vcc). Jeśli nie posiadasz dostępu, poproś osobę uprawnioną o nadanie ci niezbędnych uprawnień.

## Przygotowanie projektu w środowisku developerskim

### Przygotowanie bazy danych

```sh
docker compose up pierscien_db -d
```

### Uruchomienie serwera

```sh
W sklonowanym repozytorium:
1. cd backend
2. sanic server:app --dev --port=7777
```

### Uruchomienie frontendu

```sh
W sklonowanym repozytorium:
1. cd frontend
2. upewnić się że w pliku frontend\src\config.js zmienna baseUrl ma wartość "http://localhost:7777"
3. npm run dev
```

```sh
Aplikacja będzie dostępna pod adresem localhost:8081/
```
