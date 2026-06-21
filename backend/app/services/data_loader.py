from __future__ import annotations

import json
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from app.services.team_names import normalize

DATA_DIR = Path(__file__).resolve().parents[3] / "data"
WORLDCUP_URL = (
    "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"
)
RESULTS_PATH = DATA_DIR / "results.csv"
WORLDCUP_PATH = DATA_DIR / "worldcup2026.json"


class DataLoader:
    def __init__(self) -> None:
        self._worldcup: dict[str, Any] | None = None
        self._results: list[dict[str, Any]] | None = None
        self._last_fetch: datetime | None = None

    def load_results(self) -> list[dict[str, Any]]:
        if self._results is None:
            rows: list[dict[str, Any]] = []
            with RESULTS_PATH.open(encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        home_score = int(row["home_score"])
                        away_score = int(row["away_score"])
                    except (TypeError, ValueError):
                        continue

                    rows.append(
                        {
                            **row,
                            "home_team": normalize(row.get("home_team", "")),
                            "away_team": normalize(row.get("away_team", "")),
                            "home_score": home_score,
                            "away_score": away_score,
                            "neutral": row.get("neutral", "TRUE").upper() == "TRUE",
                        }
                    )
            self._results = rows
        return self._results

    async def fetch_worldcup(self, force: bool = False) -> dict[str, Any]:
        if self._worldcup is not None and not force:
            return self._worldcup

        fetched_text: str | None = None
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(WORLDCUP_URL)
                resp.raise_for_status()
                self._worldcup = resp.json()
                self._last_fetch = datetime.now(timezone.utc)
                fetched_text = resp.text
        except Exception:
            if WORLDCUP_PATH.exists():
                self._worldcup = json.loads(WORLDCUP_PATH.read_text(encoding="utf-8"))
            else:
                raise

        if fetched_text is not None:
            try:
                WORLDCUP_PATH.write_text(fetched_text, encoding="utf-8")
            except OSError:
                pass

        return self._worldcup  # type: ignore[return-value]

    def get_worldcup_local(self) -> dict[str, Any]:
        if self._worldcup is not None:
            return self._worldcup
        if WORLDCUP_PATH.exists():
            self._worldcup = json.loads(WORLDCUP_PATH.read_text(encoding="utf-8"))
            return self._worldcup
        raise FileNotFoundError("World Cup data not available")

    def get_matches(self) -> list[dict[str, Any]]:
        wc = self.get_worldcup_local()
        matches: list[dict[str, Any]] = []
        for idx, m in enumerate(wc.get("matches", [])):
            score = m.get("score")
            ft = score.get("ft") if score else None
            matches.append(
                {
                    "id": idx,
                    "round": m.get("round", ""),
                    "date": m.get("date", ""),
                    "time": m.get("time", ""),
                    "home_team": normalize(m.get("team1", "")),
                    "away_team": normalize(m.get("team2", "")),
                    "home_score": ft[0] if ft else None,
                    "away_score": ft[1] if ft else None,
                    "ht_home": score.get("ht", [None, None])[0] if score else None,
                    "ht_away": score.get("ht", [None, None])[1] if score else None,
                    "group": m.get("group"),
                    "ground": m.get("ground", ""),
                    "status": "finished" if ft else "scheduled",
                    "goals_home": m.get("goals1", []),
                    "goals_away": m.get("goals2", []),
                }
            )
        return matches

    def get_teams(self) -> set[str]:
        teams: set[str] = set()
        for m in self.get_matches():
            teams.add(m["home_team"])
            teams.add(m["away_team"])
        return teams

    def get_training_data(self, since: str = "2018-01-01") -> list[dict[str, Any]]:
        return [row.copy() for row in self.load_results() if row["date"] >= since]

    @property
    def last_fetch(self) -> datetime | None:
        return self._last_fetch


loader = DataLoader()
