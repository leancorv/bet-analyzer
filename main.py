from flask import Flask, request, jsonify
from src.analyst import analyze, format_report
from src.football_data import search_team, get_recent_matches, get_head_to_head, format_for_llm
from src.news import get_match_context
from src.odds import get_odds, format_for_llm as format_odds

app = Flask(__name__)

@app.route("/analyze", methods=["POST", "GET"])
def run_analysis():
    home = request.args.get("home", "Arsenal")
    away = request.args.get("away", "Burnley")

    print(f"\n🤖 Analizando: {home} vs {away}")

    home_team = search_team(home, competition="PL")
    away_team = search_team(away, competition="PL")

    if not home_team or not away_team:
        return jsonify({"error": "Equipo no encontrado"}), 404

    home_matches = get_recent_matches(home_team["id"])
    away_matches = get_recent_matches(away_team["id"])
    h2h = get_head_to_head(home_team["id"], away_team["id"])
    stats = format_for_llm(home_team["name"], away_team["name"],
                           home_matches, away_matches, h2h)

    news = get_match_context(home, away)
    odds_data = get_odds(home, away, sport="soccer_epl")
    odds = format_odds(odds_data) if odds_data else "Sin cuotas disponibles"

    analysis = analyze(home_team["name"], away_team["name"], stats, news, odds)
    report = format_report(home_team["name"], away_team["name"], analysis)

    print(report)
    return jsonify(analysis), 200

@app.route("/", methods=["GET"])
def health():
    return "Bet Analyzer running 🤖", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)