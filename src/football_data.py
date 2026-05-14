import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": os.getenv("FOOTBALL_DATA_API_KEY")}

def search_team(team_name: str, competition: str = "PL") -> dict:
    """
    Busca un equipo dentro de una competición.
    PL = Premier League, PD = La Liga, BL1 = Bundesliga
    SA = Serie A, CL = Champions League
    """
    response = requests.get(
        f"{BASE_URL}/competitions/{competition}/teams",
        headers=HEADERS
    )
    teams = response.json().get("teams", [])
    
    # Busca por nombre parcial, case insensitive
    team_name_lower = team_name.lower()
    for t in teams:
        if team_name_lower in t["name"].lower() or \
           team_name_lower in t["shortName"].lower():
            return {"id": t["id"], "name": t["name"]}
    return None

def get_recent_matches(team_id: int, limit: int = 5) -> list:
    """Últimos N partidos finalizados de un equipo."""
    response = requests.get(
        f"{BASE_URL}/teams/{team_id}/matches",
        headers=HEADERS,
        params={"status": "FINISHED", "limit": limit}
    )
    matches = []
    for m in response.json().get("matches", []):
        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]
        score_home = m["score"]["fullTime"]["home"]
        score_away = m["score"]["fullTime"]["away"]
        matches.append({
            "date": m["utcDate"][:10],
            "home": home,
            "away": away,
            "score": f"{score_home}-{score_away}",
            "winner": m["score"]["winner"]
        })
    return matches

def get_head_to_head(team_id_home: int, team_id_away: int) -> list:
    """Últimos enfrentamientos directos entre dos equipos."""
    response = requests.get(
        f"{BASE_URL}/teams/{team_id_home}/matches",
        headers=HEADERS,
        params={"status": "FINISHED", "limit": 20}
    )
    h2h = []
    for m in response.json().get("matches", []):
        ids = [m["homeTeam"]["id"], m["awayTeam"]["id"]]
        if team_id_away in ids:
            score_home = m["score"]["fullTime"]["home"]
            score_away = m["score"]["fullTime"]["away"]
            h2h.append({
                "date": m["utcDate"][:10],
                "home": m["homeTeam"]["name"],
                "away": m["awayTeam"]["name"],
                "score": f"{score_home}-{score_away}",
                "winner": m["score"]["winner"]
            })
    return h2h[:5]

def format_for_llm(home_name: str, away_name: str,
                   home_matches: list, away_matches: list,
                   h2h: list) -> str:
    """Convierte toda la data en texto limpio para el LLM."""
    def match_str(m):
        return f"  {m['date']} | {m['home']} {m['score']} {m['away']} → {m['winner']}"

    lines = []
    lines.append(f"=== Últimos partidos de {home_name} ===")
    lines.extend(match_str(m) for m in home_matches)

    lines.append(f"\n=== Últimos partidos de {away_name} ===")
    lines.extend(match_str(m) for m in away_matches)

    lines.append(f"\n=== Head to head ===")
    if h2h:
        lines.extend(match_str(m) for m in h2h)
    else:
        lines.append("  Sin enfrentamientos recientes")

    return "\n".join(lines)

if __name__ == "__main__":
    arsenal = search_team("Arsenal FC")
    city = search_team("Manchester City FC")
    print("Arsenal:", arsenal)
    print("City:", city)

    if arsenal and city:
        home_matches = get_recent_matches(arsenal["id"])
        away_matches = get_recent_matches(city["id"])
        h2h = get_head_to_head(arsenal["id"], city["id"])
        print(format_for_llm(
            arsenal["name"], city["name"],
            home_matches, away_matches, h2h
        ))