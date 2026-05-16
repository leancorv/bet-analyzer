from flask import Flask, request, jsonify, render_template
from src.analyst import analyze, format_report
from src.football_data import search_team, get_recent_matches, get_head_to_head, format_for_llm
from src.news import get_match_context
from src.odds import get_odds, format_for_llm as format_odds

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST", "GET"])
def run_analysis():
    home = request.args.get("home", "Arsenal")
    away = request.args.get("away", "Burnley")
    competition = request.args.get("competition", "PL")

    home_team = search_team(home, competition=competition)
    away_team = search_team(away, competition=competition)

    if not home_team or not away_team:
        return jsonify({"error": "Equipo no encontrado"}), 404

    # Data cruda
    home_matches = get_recent_matches(home_team["id"])
    away_matches = get_recent_matches(away_team["id"])
    h2h = get_head_to_head(home_team["id"], away_team["id"])
    stats = format_for_llm(home_team["name"], away_team["name"],
                           home_matches, away_matches, h2h)

    news = get_match_context(home, away)

    odds_data = get_odds(home, away, sport="soccer_epl")
    odds_text = format_odds(odds_data) if odds_data else "Sin cuotas disponibles"

    # LLM analysis
    analysis = analyze(home_team["name"], away_team["name"],
                      stats, news, odds_text)

    # Calcular forma como G/E/P
    def calc_form(matches, team_name):
        form = []
        team_lower = team_name.lower()
        for m in matches[-5:]:
            home_match = m["home"].lower()
            away_match = m["away"].lower()
            is_home = team_lower in home_match or home_match in team_lower
            is_away = team_lower in away_match or away_match in team_lower
            if m["winner"] == "DRAW":
                form.append("E")
            elif (m["winner"] == "HOME_TEAM" and is_home) or \
                (m["winner"] == "AWAY_TEAM" and is_away):
                form.append("G")
            else:
                form.append("P")
        return form

    # Calcular H2H stats
    def calc_h2h_stats(h2h_matches, home_name, away_name):
        home_wins = sum(1 for m in h2h_matches
                       if (m["winner"] == "HOME_TEAM" and m["home"] == home_name) or
                          (m["winner"] == "AWAY_TEAM" and m["away"] == home_name))
        away_wins = sum(1 for m in h2h_matches
                       if (m["winner"] == "HOME_TEAM" and m["home"] == away_name) or
                          (m["winner"] == "AWAY_TEAM" and m["away"] == away_name))
        draws = sum(1 for m in h2h_matches if m["winner"] == "DRAW")
        total = len(h2h_matches)
        return {
            "home_wins": home_wins,
            "away_wins": away_wins,
            "draws": draws,
            "total": total,
            "home_pct": round(home_wins/total*100) if total else 0,
            "away_pct": round(away_wins/total*100) if total else 0,
            "draw_pct": round(draws/total*100) if total else 0,
        }

    # Respuesta enriquecida
    return jsonify({
        **analysis,
        "home_name": home_team["name"],
        "away_name": away_team["name"],
        "home_form": calc_form(home_matches, home_team["name"]),
        "away_form": calc_form(away_matches, away_team["name"]),
        "h2h_stats": calc_h2h_stats(h2h, home_team["name"], away_team["name"]),
        "h2h_matches": h2h,
        "odds": {
            "best": odds_data["best_odds"] if odds_data else None,
            "implied": odds_data["implied_probabilities"] if odds_data else None,
            "value_bets": odds_data["value_bets"] if odds_data else [],
            "bookmakers_count": len(odds_data["bookmakers"]) if odds_data else 0,
        } if odds_data else None
    }), 200

@app.route("/", methods=["GET"])
def health():
    return "Bet Analyzer running 🤖", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)