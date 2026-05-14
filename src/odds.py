import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.the-odds-api.com/v4"
API_KEY = os.getenv("ODDS_API_KEY")

def get_odds(home: str, away: str, sport: str = "soccer_epl") -> dict:
    """
    Trae las cuotas de múltiples casas para un partido.
    Devuelve las mejores cuotas y detecta value bets.
    """
    response = requests.get(
        f"{BASE_URL}/sports/{sport}/odds",
        params={
            "apiKey": API_KEY,
            "regions": "eu",
            "markets": "h2h",
            "oddsFormat": "decimal"
        }
    )

    if response.status_code != 200:
        print(f"Error odds API: {response.status_code}")
        return None

    games = response.json()

    # Buscar el partido que matchee
    home_lower = home.lower().replace(" fc", "").strip()
    away_lower = away.lower().replace(" fc", "").strip()

    for game in games:
        game_home = game["home_team"].lower()
        game_away = game["away_team"].lower()

        if home_lower in game_home and away_lower in game_away:
            return parse_odds(game)
        if away_lower in game_home and home_lower in game_away:
            return parse_odds(game)

    return None

def parse_odds(game: dict) -> dict:
    """
    Extrae y compara cuotas de todas las casas disponibles.
    Detecta la mejor cuota por resultado y calcula value bets.
    """
    results = {"home": [], "draw": [], "away": [], "bookmakers": []}

    for bookmaker in game.get("bookmakers", []):
        name = bookmaker["title"]
        for market in bookmaker["markets"]:
            if market["key"] == "h2h":
                odds_map = {o["name"]: o["price"] for o in market["outcomes"]}
                home_odd = odds_map.get(game["home_team"])
                away_odd = odds_map.get(game["away_team"])
                draw_odd = odds_map.get("Draw")

                results["bookmakers"].append({
                    "name": name,
                    "home": home_odd,
                    "draw": draw_odd,
                    "away": away_odd
                })
                if home_odd: results["home"].append(home_odd)
                if draw_odd: results["draw"].append(draw_odd)
                if away_odd: results["away"].append(away_odd)

    # Mejores cuotas disponibles
    best = {
        "home": max(results["home"]) if results["home"] else None,
        "draw": max(results["draw"]) if results["draw"] else None,
        "away": max(results["away"]) if results["away"] else None,
    }

    # Value bet detector
    # Si la mejor cuota implica probabilidad menor al promedio → posible value
    def implied_prob(odd): return round(1 / odd * 100, 1) if odd else None
    def avg(lst): return round(sum(lst) / len(lst), 2) if lst else None

    value_bets = []
    for outcome, odds_list in [("home", results["home"]),
                                ("draw", results["draw"]),
                                ("away", results["away"])]:
        if not odds_list or len(odds_list) < 2:
            continue
        best_odd = max(odds_list)
        avg_odd = avg(odds_list)
        # Si la mejor cuota es >5% mayor al promedio, hay discrepancia
        if best_odd > avg_odd * 1.05:
            value_bets.append({
                "outcome": outcome,
                "best_odd": best_odd,
                "avg_odd": avg_odd,
                "edge": round((best_odd / avg_odd - 1) * 100, 1)
            })

    return {
        "match": f"{game['home_team']} vs {game['away_team']}",
        "commence_time": game["commence_time"][:10],
        "best_odds": best,
        "implied_probabilities": {
            "home": implied_prob(best["home"]),
            "draw": implied_prob(best["draw"]),
            "away": implied_prob(best["away"]),
        },
        "bookmakers": results["bookmakers"],
        "value_bets": value_bets
    }

def format_for_llm(odds_data: dict) -> str:
    """Convierte las cuotas en texto para el LLM."""
    if not odds_data:
        return "No se encontraron cuotas para este partido."

    lines = [
        f"=== Cuotas: {odds_data['match']} ({odds_data['commence_time']}) ===",
        f"Mejores cuotas disponibles:",
        f"  Local:  {odds_data['best_odds']['home']} (prob. implícita: {odds_data['implied_probabilities']['home']}%)",
        f"  Empate: {odds_data['best_odds']['draw']} (prob. implícita: {odds_data['implied_probabilities']['draw']}%)",
        f"  Visitante: {odds_data['best_odds']['away']} (prob. implícita: {odds_data['implied_probabilities']['away']}%)",
    ]

    if odds_data["value_bets"]:
        lines.append("\n⚡ Value bets detectados:")
        for vb in odds_data["value_bets"]:
            lines.append(
                f"  {vb['outcome'].upper()}: mejor cuota {vb['best_odd']} "
                f"vs promedio {vb['avg_odd']} (+{vb['edge']}% edge)"
            )
    else:
        lines.append("\nSin value bets detectados — mercado eficiente.")

    lines.append(f"\nCasas consultadas: {len(odds_data['bookmakers'])}")
    return "\n".join(lines)

if __name__ == "__main__":
    odds = get_odds("Arsenal", "Burnley", sport="soccer_epl")
    if odds:
        print(format_for_llm(odds))
    else:
        print("Partido no encontrado.")