from __future__ import annotations

from dataclasses import dataclass
from math import exp, factorial

from app.services.team_names import normalize


@dataclass
class TeamStrength:
    attack: float
    defense: float
    matches: int


class PoissonPredictor:
    """Dixon-Coles inspired Poisson model for international football."""

    HOME_ADVANTAGE = 1.15
    LEAGUE_AVG_GOALS = 1.35
    MAX_GOALS = 6

    def __init__(self) -> None:
        self.strengths: dict[str, TeamStrength] = {}
        self.trained = False

    def fit(self, rows: list[dict]) -> None:
        teams = {row["home_team"] for row in rows} | {row["away_team"] for row in rows}
        team_stats: dict[str, dict[str, float]] = {
            t: {"gf": 0.0, "ga": 0.0, "n": 0} for t in teams
        }

        for row in rows:
            h, a = row["home_team"], row["away_team"]
            hs, aws = float(row["home_score"]), float(row["away_score"])
            for team, gf, ga in [(h, hs, aws), (a, aws, hs)]:
                team_stats[team]["gf"] += gf
                team_stats[team]["ga"] += ga
                team_stats[team]["n"] += 1

        self.strengths = {}
        for team, s in team_stats.items():
            n = max(s["n"], 1)
            avg_gf = s["gf"] / n
            avg_ga = s["ga"] / n
            attack = avg_gf / self.LEAGUE_AVG_GOALS
            defense = avg_ga / self.LEAGUE_AVG_GOALS
            self.strengths[team] = TeamStrength(
                attack=max(attack, 0.3),
                defense=max(defense, 0.3),
                matches=int(n),
            )
        self.trained = True

    def _expected_goals(
        self, home: str, away: str, neutral: bool = True
    ) -> tuple[float, float]:
        home = normalize(home)
        away = normalize(away)
        default = TeamStrength(1.0, 1.0, 0)
        hs = self.strengths.get(home, default)
        aws = self.strengths.get(away, default)

        home_exp = hs.attack * aws.defense * self.LEAGUE_AVG_GOALS
        away_exp = aws.attack * hs.defense * self.LEAGUE_AVG_GOALS

        if not neutral:
            home_exp *= self.HOME_ADVANTAGE

        return max(home_exp, 0.05), max(away_exp, 0.05)

    @staticmethod
    def _pmf(goals: int, expected_goals: float) -> float:
        return (expected_goals ** goals) * exp(-expected_goals) / factorial(goals)

    def predict(
        self, home: str, away: str, neutral: bool = True
    ) -> dict:
        lam_h, lam_a = self._expected_goals(home, away, neutral)

        score_probs: list[dict] = []
        home_win = draw = away_win = 0.0
        most_likely = (0, 0, 0.0)

        for h in range(self.MAX_GOALS + 1):
            for a in range(self.MAX_GOALS + 1):
                p = self._pmf(h, lam_h) * self._pmf(a, lam_a)
                if p > 0.001:
                    score_probs.append(
                        {"home": h, "away": a, "probability": round(float(p), 4)}
                    )
                if h > a:
                    home_win += p
                elif h == a:
                    draw += p
                else:
                    away_win += p
                if p > most_likely[2]:
                    most_likely = (h, a, p)

        score_probs.sort(key=lambda x: x["probability"], reverse=True)

        return {
            "model": "poisson",
            "home_team": normalize(home),
            "away_team": normalize(away),
            "expected_goals_home": round(lam_h, 2),
            "expected_goals_away": round(lam_a, 2),
            "predicted_score": f"{most_likely[0]}-{most_likely[1]}",
            "probabilities": {
                "home_win": round(home_win, 4),
                "draw": round(draw, 4),
                "away_win": round(away_win, 4),
            },
            "top_scores": score_probs[:8],
        }
