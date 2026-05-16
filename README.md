# 🤖 BetAnalyzer AI

> Agente de IA autónomo que analiza partidos de fútbol cruzando estadísticas reales, noticias de último momento y cuotas de 23 casas de apuestas — desplegado en producción sobre GCP.

**[🔴 Demo en vivo](https://bet-analyzer-481449893584.us-central1.run.app/)**

![BetAnalyzer AI Demo](docs/demo.gif)

---

## ¿Qué hace?

Ingresás dos equipos y el agente ejecuta un pipeline de 4 pasos de forma autónoma:

1. **Data Collector** — Busca estadísticas, últimos 5 partidos y head-to-head vía football-data.org
2. **News Scraper** — Rastrea lesionados, suspendidos y noticias de último momento vía Tavily
3. **Odds Analyzer** — Consulta cuotas en 23 casas de apuestas, calcula probabilidades implícitas y detecta value bets automáticamente
4. **LLM Analyst** — Sintetiza toda la información y genera un reporte estructurado con recomendación y nivel de confianza

El resultado: un análisis completo en segundos que tomaría 45 minutos hacer manualmente.

---

## Arquitectura

```
Trigger HTTP (browser / curl)
         ↓
   Flask — servidor web
         ↓
   pipeline del agente
    ├── football-data.org  → estadísticas y H2H
    ├── Tavily API         → noticias y contexto
    ├── The Odds API       → cuotas de 23 casas
    └── Groq API (LLM)    → síntesis y recomendación
         ↓
   Respuesta JSON → UI renderizada en el browser
```

---

## Stack técnico

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.11 |
| Web framework | Flask |
| Estadísticas | football-data.org API |
| Noticias | Tavily API |
| Cuotas | The Odds API |
| LLM | Groq API — Llama 3.3 70B |
| Frontend | HTML + CSS + JS vanilla |
| Containerización | Docker |
| Deploy | GCP Cloud Run |

---

## Features

- **Pipeline multi-fuente** — 3 APIs externas + 1 LLM orquestadas en secuencia
- **Value bet detector** — detecta discrepancias entre casas con cálculo de edge %
- **Forma visual G/E/P** — últimos 5 partidos de cada equipo con píldoras de colores
- **H2H con barra de progreso** — historial directo con porcentajes y visualización
- **Loader tipo n8n** — muestra el flujo del agente paso a paso mientras procesa
- **Manejo de errores** — mensajes claros si el equipo no existe o una API falla
- **Provider-agnóstico** — el LLM se cambia editando una sola función
- **Cloud-native** — Docker + GCP Cloud Run, escala a cero cuando no hay tráfico

---

## Estructura del proyecto

```
bet-analyzer/
├── src/
│   ├── football_data.py   # Estadísticas, últimos partidos, H2H
│   ├── news.py            # Noticias y contexto via Tavily
│   ├── odds.py            # Cuotas + value bet detector
│   └── analyst.py         # LLM: síntesis y recomendación final
├── templates/
│   └── index.html         # Frontend completo (HTML/CSS/JS)
├── main.py                # Flask entrypoint + pipeline principal
├── .env.example
├── requirements.txt
└── Dockerfile
```

---

## Setup local

### 1 — Clonar e instalar

```bash
git clone https://github.com/leandro-corvalan/bet-analyzer.git
cd bet-analyzer
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2 — Configurar variables de entorno

```bash
cp .env.example .env
```

Editá `.env` con tus API keys:

```bash
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
FOOTBALL_DATA_API_KEY=your_football_data_api_key
ODDS_API_KEY=your_odds_api_key
```

### 3 — Correr localmente

```bash
python main.py
```

Abrí `http://localhost:8080` en el browser.

---

## API Keys — todas gratuitas

| Servicio | Free tier | Link |
|---|---|---|
| Groq | 30 req/min, 14.400/día | [console.groq.com](https://console.groq.com) |
| Tavily | 1.000 búsquedas/mes | [tavily.com](https://tavily.com) |
| football-data.org | 10 req/min, ligas europeas | [football-data.org](https://www.football-data.org) |
| The Odds API | 500 req/mes | [the-odds-api.com](https://the-odds-api.com) |

---

## Deploy en GCP Cloud Run

```bash
# Configurar proyecto
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

# Crear repositorio de imágenes
gcloud artifacts repositories create bet-analyzer \
  --repository-format=docker \
  --location=us-central1

# Build y push
gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR_PROJECT_ID/bet-analyzer/bet-analyzer

# Deploy
gcloud run deploy bet-analyzer \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/bet-analyzer/bet-analyzer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --env-vars-file env.yaml
```

---

## Conceptos demostrados

- **Orquestación de agentes** — pipeline multi-step con fuentes de datos heterogéneas
- **Prompt engineering** — structured outputs via JSON prompting para outputs consistentes
- **Arquitectura provider-agnóstica** — swap de LLM sin tocar la lógica de negocio
- **Value bet detection** — lógica propia de detección de ineficiencias de mercado
- **Deploy cloud-native** — Docker + GCP Cloud Run con escala automática
- **Gestión segura de credenciales** — variables de entorno, sin secrets en el código

---

## Ligas soportadas

| Liga | Código |
|---|---|
| Premier League | PL |
| La Liga | PD |
| Bundesliga | BL1 |
| Serie A | SA |
| Champions League | CL |

---

## Autor

**Leandro Corvalán**
Desarrollado como proyecto de AI Engineering — Python · Groq · Tavily · football-data.org · The Odds API · Docker · GCP

---
---

# 🤖 BetAnalyzer AI *(English)*

> Autonomous AI agent that analyzes football matches by combining real statistics, breaking news, and odds from 23 bookmakers — deployed in production on GCP.

**[🔴 Live Demo](https://bet-analyzer-481449893584.us-central1.run.app/)**

## What it does

You enter two teams and the agent runs a 4-step pipeline autonomously:

1. **Data Collector** — Fetches stats, last 5 matches and head-to-head via football-data.org
2. **News Scraper** — Tracks injuries, suspensions and breaking news via Tavily
3. **Odds Analyzer** — Queries odds from 23 bookmakers, calculates implied probabilities and automatically detects value bets
4. **LLM Analyst** — Synthesizes all information and generates a structured report with recommendation and confidence score

The result: a complete analysis in seconds that would take 45 minutes manually.

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Web framework | Flask |
| Statistics | football-data.org API |
| News | Tavily API |
| Odds | The Odds API |
| LLM | Groq API — Llama 3.3 70B |
| Frontend | Vanilla HTML/CSS/JS |
| Containerization | Docker |
| Deployment | GCP Cloud Run |

## Key concepts demonstrated

- **Agent orchestration** — multi-step pipeline with heterogeneous data sources
- **Prompt engineering** — structured JSON outputs for consistent LLM responses
- **Provider-agnostic LLM architecture** — swap models by editing a single function
- **Value bet detection** — custom logic for detecting market inefficiencies
- **Cloud-native deployment** — Docker + GCP Cloud Run with auto-scaling
- **Secure credential management** — environment variables, no secrets in code

## Author

**Leandro Corvalán**
Built as an AI Engineering project — Python · Groq · Tavily · Docker · GCP
