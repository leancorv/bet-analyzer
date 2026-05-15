import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze(home: str, away: str,
            stats: str, news: str, odds: str) -> dict:
    """
    Recibe toda la data recopilada y genera un análisis estructurado.
    Devuelve un dict con secciones claras.
    """
    prompt = f"""
    Sos un analista deportivo experto en apuestas de fútbol.
    Analizá el siguiente partido y generá un reporte estructurado.

    PARTIDO: {home} vs {away}

    ESTADÍSTICAS Y HEAD TO HEAD:
    {stats}

    NOTICIAS Y CONTEXTO (lesionados, suspendidos):
    {news}

    CUOTAS Y VALUE BETS:
    {odds}

    Respondé ÚNICAMENTE con este JSON, sin texto adicional ni backticks:
    {{
        "forma_local": "<análisis de los últimos partidos del local en 2 oraciones>",
        "forma_visitante": "<análisis de los últimos partidos del visitante en 2 oraciones>",
        "head_to_head": "<qué dice el historial directo en 1 oración>",
        "contexto": "<lesionados y factores externos relevantes en 2 oraciones>",
        "analisis_cuotas": "<qué dicen las cuotas y si los value bets tienen sentido en 2 oraciones>",
        "recomendacion": "<apuesta recomendada con justificación en 2 oraciones>",
        "confianza": <número del 1 al 10>,
        "resultado_probable": "<1 / X / 2>"
    }}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    raw = response.choices[0].message.content.strip()
    return json.loads(raw)

def format_report(home: str, away: str, analysis: dict) -> str:
    """Formatea el análisis en un reporte legible."""
    conf = analysis.get("confianza", "?")
    conf_bar = "█" * conf + "░" * (10 - conf)

    return f"""
╔══════════════════════════════════════════════╗
  {home} vs {away}
╚══════════════════════════════════════════════╝

📊 FORMA LOCAL
{analysis.get("forma_local")}

📊 FORMA VISITANTE
{analysis.get("forma_visitante")}

⚔️  HEAD TO HEAD
{analysis.get("head_to_head")}

🏥 CONTEXTO
{analysis.get("contexto")}

💰 ANÁLISIS DE CUOTAS
{analysis.get("analisis_cuotas")}

🎯 RECOMENDACIÓN
{analysis.get("recomendacion")}

Resultado probable: {analysis.get("resultado_probable")}
Confianza: {conf}/10  [{conf_bar}]
"""

if __name__ == "__main__":
    from football_data import search_team, get_recent_matches, get_head_to_head, format_for_llm
    from news import get_match_context
    from odds import get_odds, format_for_llm as format_odds

    home_name = "Arsenal"
    away_name = "Burnley"

    print("🔍 Recopilando datos...")
    home_team = search_team(home_name, competition="PL")
    away_team = search_team(away_name, competition="PL")

    home_matches = get_recent_matches(home_team["id"])
    away_matches = get_recent_matches(away_team["id"])
    h2h = get_head_to_head(home_team["id"], away_team["id"])
    stats = format_for_llm(home_team["name"], away_team["name"],
                           home_matches, away_matches, h2h)

    print("📰 Buscando noticias...")
    news = get_match_context(home_name, away_name)

    print("💰 Consultando cuotas...")
    odds_data = get_odds(home_name, away_name, sport="soccer_epl")
    odds = format_odds(odds_data) if odds_data else "Sin cuotas disponibles"

    print("🤖 Analizando con LLM...\n")
    analysis = analyze(home_team["name"], away_team["name"], stats, news, odds)
    print(format_report(home_team["name"], away_team["name"], analysis))