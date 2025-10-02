# 📊 Helpscout Mailbox Analyzer

## Descriere

Platformă full-stack de analiză a conversațiilor din HelpScout, dezvoltată pentru a automatiza procesul de alocare a costurilor și analiză a workload-ului echipei de suport din cadrul Themeisle. Sistemul procesează mii de conversații din multiple mailbox-uri, imparte pe categorii pe baza unor tag-uri și generează un raport pentru fiecare produs si persoana în format CSV.
---

## ✨ Caracteristici Principale

### 🔄 Procesare Concurentă Avansată
- **ThreadPoolExecutor** cu 30 de worker threads pentru procesare paralelă
- **Asyncio pipelines** pentru orchestrarea multi-stage workflow
- **Thread-safe rate limiting** pentru coordonarea request-urilor API

### 🔌 Integrare API Robustă
- **OAuth2 authentication**
- **Custom rate limiter** care trackuiește request-uri pe minut
- **Retry logic** cu exponential backoff
- **Error handling** pentru coduri 429, 500, 502, 503, 504

### 📈 Pipeline de Procesare Date
- **Extracție automată** din 3 mailbox-uri HelpScout
- **Filtrare pe intervale de timp** cu validare date
- **Categorizare bazată pe tag-uri** cu mapare în baza de date
- **Agregare cross-mailbox** pentru rapoarte consolidate

### 🌐 Aplicație Web Full-Stack
- **Flask web server** cu routing și form handling
- **Interfață responsivă** cu CSS simplu si user-friendly
- **Export automat CSV** cu denumire bazată pe lună
- **Auto-browser launch** pentru UX îmbunătățit

### 🗄️ Bază de Date Structurată
- **SQLite database** cu schema normalizată
- **Relații foreign key** între produse și tag-uri
- **20+ produse** predefinite cu 40+ tag-uri asociate
- **Query optimization** cu JOIN-uri eficiente

---

## 🏗️ Arhitectură

### Structura Proiectului

```
Helpscout-Mailbox-Analyzer/
├── APIConnection/              # Logica de conectare la API
│   ├── core_system.py         # Wrapper API cu rate limiting
│   └── get_access_token.py    # OAuth2 token management
│
├── BaseClasses/               # Clase abstracte de bază (OOP)
│   ├── base_wporg_conversations.py
│   ├── conversation_tag_base.py
│   └── mailbox_base.py
│
├── CredentialsAndJsonManager/ # Configureaza datele in json
│   └── config_loader.py
│
├── Database/                  # Schema și populare bază de date
│   ├── database_schema.py
│   ├── database_predefined_values.py
│   └── database_maker.py
│
├── FilterMailboxes/          # Filtrare conversații
│   ├── filter_wporg_conversations.py
│   └── filter_optimole_conversations.py
│
├── HelpscoutMailboxes/       # Implementări mailbox-uri specifice
│   ├── helpscout_free_mailbox.py
│   ├── helpscout_free_mailbox_tags.py
│   ├── helpscout_pro_mailbox.py
│   └── helpscout_optimole_mailbox.py
│
├── ProcessMailboxes/         # Procesare și analiză conversații
│   ├── process_wporg_conversations.py
│   ├── process_pro_conversations.py
│   └── process_optimole_conversations.py
│
├── HelperFiles/              # Utilitare și helper functions
│   ├── get_last_month_dates.py
│   ├── helper_file_to_export_csvs_to_list.py
│   ├── helper_file_to_make_csv_from_list.py
│   └── helper_file_to_change_keys_from_wporg_username_to_team_member_names.py
│
├── Main/                     # Entry points aplicație
│   ├── main.py              # Pipeline async principal
│   └── server.py            # Flask web server
│
├── templates/               # Template-uri HTML
│   ├── form.html
│   └── dashboard.html
│
├── static/                  # Assets frontend
│   ├── styles.css
│   └── script.js
│
├── CSVs/                    # Output folder pentru raport
├── app.db                   # Bază de date SQLite
├── config.json              # Fișier de configurare
└── requirements.txt         # Dependențe Python
```

### Design Patterns Utilizate

- **Abstract Base Classes (ABC)** - Pentru extensibilitate și reutilizare cod prin clase abstracte (`MailboxBase`, `BaseConversations`, `ConversationTagBase`)
- **Template Method Pattern** - Pipeline-uri de procesare cu structură definită și implementări specifice în subclase
- **Multiple Inheritance (Mixin)** - Combinarea funcționalităților din multiple clase de bază (ex: `ProcessOptimoleConversations`)
- **Singleton-like Pattern** - Session sharing și lock-uri globale pentru coordonarea thread-urilor (`CoreSystem._session`, `_request_lock`)

---

## 🚀 Instalare și Configurare

### Prerequisite

- Python 3.13+
- Git

### Pași de Instalare

1. **Clonează repository-ul:**
```bash
git clone https://github.com/deniz2104/Helpscout-Mailbox-Analyzer.git
cd Helpscout-Mailbox-Analyzer
```

2. **Activeaza virtual environment si instaleaza dependentele:**
```bash
python HelperFiles/helper_file_to_automate_making_of_venv.py && source venv/bin/activate
```

3. **Inițializează baza de date:**
```bash
python Database/database_maker.py
```

4. **Configurează credentials (prima rulare):**
- Rulează serverul Flask ```bash python Main/server.py```
- Se va accesa automat http://localhost:5001
- Introdu HelpScout Client ID și Client Secret

---

## 🎮 Utilizare

1. **Ruleaza programul:**
```bash
python Main/main.py
```

2. **Exportă rapoartele:**
- Apasă butonul "Export Data into a CSV" din dashboard
- Raportul va fi descărcat automat

## ⚙️ Configurare

### config.json

Fișierul `config.json` este generat automat la prima rulare.

### Parametri Configurabili

- **TEAM_MEMBERS**: Mapare între prenume și nume complete ale membrilor echipei
- **WP_ORG_USERNAMES**: Mapare între username-uri WordPress.org și membrii echipei
- **MAILBOX_*_ID**: ID-urile mailbox-urilor HelpScout

---

## 🔧 Implementare

### 1. Core API System

**Fișier:** `APIConnection/core_system.py`

Funcționalități:
- Rate limiting per-minute cu tracking automat
- Session persistence pentru connection pooling
- Retry mechanism cu exponential backoff
- Thread-safe request coordination
- Response header parsing pentru limite API

```python
core_system = CoreSystem(client_id, client_secret)
response = core_system.make_request("conversations", params={"status": "active"})
```

**Fișier:** `APIConnection/get_access_token.py`

Funcționalități:
- Determinare token de autentificare

### 2. Concurrent Processing and Base Classes

**Fișier:** `BaseClasses/base_wporg_conversations.py`

Caracteristici:
- ThreadPoolExecutor cu 30 workers
- Procesare paralelă a conversațiilor intr-un mod functional
- Validare ca mail-ul este scris de unul dintre membrii echipei

```python
with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
    results = executor.map(process_single_conversation, conversation_ids)
```

**Fișier:** `BaseClasses/mailbox_base.py`

Caracteristici:
- Clasă abstractă pentru operații comune pe mailboxuri
- Implementare functionala pentru logica de procesare a paginilor,tag-urilor si id-urilor
- Filtrare automată pe intervale de date (ultimul lună)
- Export date în CSV cu headers configurabile

**Fișier:** `BaseClasses/conversation_tag_base.py`

Caracteristici:
- Procesare conversații cu categorizare pe tag-uri
- Validare tag-uri relativ la  baza de date
- Identificare răspunsuri de la membrii echipei în interval de timp specificat
- Agregare rezultate per produs și persoană

### 3. Mailbox Extractors

**Fișiere:** `HelpscoutMailboxes\helpscout_free_mailbox.py`,`HelpscoutMailboxes\helpscout_free_mailbox_tags.py`,`HelpscoutMailboxes\helpscout_optimole_mailbox.py`,`HelpscoutMailboxes\helpscout_pro_mailbox.py`

Caracteristici:
- Extrage ID-uri din conversații din ultimele lună pentru fiecare mailbox
- Extrage tag-urile asociate fiecărei conversații
- Implementează clase specifice pentru Free, Pro și Optimole mailboxes
- Moștenește `MailboxBase` pentru reutilizarea codului

### 4. Conversation Filters

**Fișiere:** `FilterMailboxes\filter_wporg_conversations.py`,`FilterMailboxes\filter_optimole_conversations.py`

Caracteristici:
- **WPORG Filter**: Filtrează conversații pe bază de tag "team reply" pentru forumul WordPress.org
- **Optimole Filter**: Identifică conversații cu răspunsuri de la membrii echipei folosind ThreadPoolExecutor
- Compară ID-uri cu tag-uri pentru a găsi conversații relevante
- Generează CSV-uri cu conversații filtrate pentru procesare ulterioară

### 5. Conversation Processors

**Fișiere:** `ProcessMailboxes\process_wporg_conversations.py`,`ProcessMailboxes\process_pro_conversations.py`,`ProcessMailboxes\process_optimole_conversations.py`

Caracteristici:
- Extrage username-uri din conversații WordPress.org folosind regex parsing pentru a gasi userul unui membru
- Categorizează conversații pe produs bazat pe tag-uri din baza de date
- Numără răspunsurile fiecărui membru al echipei per produs
- Generează JSON files cu rezultate agregate pentru raport

### 6. Helper Files - Utilitare

**Fișier:** `HelperFiles/get_last_month_dates.py`
- Calculează prima și ultima zi a lunii anterioare
- Returnează intervale de timp formatate pentru filtrare conversații

**Fișier:** `HelperFiles/helper_file_to_get_last_month.py`
- Returnează numărul lunii anterioare (1-12)
- Utilizat pentru denumirea automată a rapoartelor CSV

**Fișier:** `HelperFiles/helper_file_to_export_csvs_to_list.py`
- Citește CSV-uri și convertește în liste

**Fișier:** `HelperFiles/helper_file_to_make_csv_from_list.py`
- Generează CSV-uri din liste de intregi
- Adaugă header configurabil automat
- Export rapid de date

**Fișier:** `HelperFiles/helper_file_to_change_keys_from_wporg_username_to_team_member_names.py`
- Mapează username-uri WordPress.org la numele membrilor echipei
- Citește mapping-ul din `config.json`
- Transformă rezultate pentru raportare consistentă

**Fișier:** `HelperFiles/helper_file_to_see_no_replies_emails_in_optimole.py`
- Identifică conversații Optimole fără răspuns de la echipă
- Compară set-uri de ID-uri (toate vs cu răspuns)
- Generează CSV cu conversații care necesită follow-up

**Fișier:** `HelperFiles/helper_file_to_automate_making_of_venv.py`
- Automatizează crearea virtual environment
- Instalează dependențe din `requirements.txt`
- Upgrade automat pip la ultima versiune

### 7. Database Layer

**Fișiere:** `Database/database_schema.py`, `database_predefined_values.py`

Schema:
- Tabela `products`: 20+ produse
- Tabela `tags`: 40+ tag-uri cu foreign keys
- Relații ONE-TO-MANY între produse și tag-uri

**Fișiere:** `Database/database_maker.py`

Caracteristici:
- Initializeaza baza de date si o populeaza.

### 8. Async Pipeline and Server

**Fișier:** `Main/server.py`

Caracteristici:
- Flask web server cu auto-browser launch
- Route pentru form submission și dashboard
- Endpoint `/check_json_files` pentru verificare status procesare
- Endpoint `/export` pentru download CSV-uri consolidate
- Agregare automată date din multiple JSON files

**Fișier:** `Main/main.py`

Pipeline în 5 stage-uri:
1. **Stage 1**: Procesare Free Mailbox (paralel)
2. **Stage 2**: Procesare Pro & Optimole (paralel)
3. **Stage 3**: Filtrare conversații (paralel)
4. **Stage 4**: Procesare no-replies
5. **Stage 5**: Generare rapoarte finale (secvențial)

---

## 📊 Output și Rapoarte

### Fișiere Generate

**CSVs/**
- `filtered_free_conversations_ids.csv` - ID-uri conversații free
- `filtered_free_conversations_tags.csv` - Tag-uri conversații free
- `filtered_wporg_conversations.csv` - Conversații WordPress.org filtrate
- `filtered_optimole_conversations.csv` - Conversații Optimole filtrate
- `filtered_optimole_conversations_no_replies.csv` - Conversații fără răspunsuri
- `process_optimole_results.json` - Rezultate procesare Optimole
- `process_pro_results.json` - Rezultate procesare Pro
- `process_wporg_results.json` - Rezultate procesare WordPress.org
- `cost_allocation_for_[month].csv` - **Raport final consolidat**

## 🎯 Cazuri de Utilizare

### 1. Alocare Costuri Lunară
Generează automat raportul de workload pentru fiecare membru al echipei pe produs, utilizat pentru alocarea costurilor interne.

### 2. Analiză Performanță Echipă
Identifică distribuția workload-ului între membri și produse pentru optimizarea resurselor.

### 3. Tracking Conversații WordPress.org
Extrage și mapează automat conversațiile din forumul WordPress.org către membrii echipei.
---

## 🔒 Securitate

- ✅ OAuth2 token management cu refresh automat
- ✅ Rate limiting pentru protecție împotriva API abuse
- ✅ SQL injection prevention prin parametrizare queries
- ✅ Error handling pentru toate operațiunile I/O

---

## 🚀 Performance

### Optimizări

- Connection pooling pentru API requests
- Thread pooling pentru procesare paralelă
- Batch processing pentru database operations
- CSV streaming pentru memory efficiency

---

## 🛠️ Tech Stack

### Backend
- **Python 3.13** - Limbaj principal
- **Flask 3.1.2** - Web framework
- **Requests 2.32.5** - HTTP client
- **SQLite3** - Database
- **Threading** - Concurrent processing
- **Asyncio** - Async pipeline orchestration

### Frontend
- **HTML5**
- **CSS3**
- **JavaScript** - Client-side logic

### Architecture
- **OOP** - Abstract base classes
- **Multiple Inheritance** - Mixin patterns
- **Type Hints** - Python type annotations
- **Design Patterns** - Template Method, Singleton

---

## 📝 Dependențe

```txt
requests==2.32.5
pandas==2.3.2
Flask==3.1.2
```

---

## 🐛 Troubleshooting

### Eroare: "Failed to get token"
**Soluție:** Verifică că `HELPSCOUT_CLIENT_ID` și `HELPSCOUT_CLIENT_SECRET` sunt corecte în `config.json`.

### Eroare: "Rate limit reached"
**Soluție:** Sistemul va aștepta automat. Dacă problema persistă, reduce `max_workers` din 30 la 20.

### Eroare: "No JSON files found"
**Soluție:** Rulează mai întâi `python Main/server.py` pentru a genera fișierele JSON necesare.

### Eroare: "Database locked"
**Soluție:** Asigură-te că nicio altă instanță nu accesează baza de date. Închide toate procesele și reîncearcă.

---

## 📄 Licență

Toate drepturile rezervate.

---
