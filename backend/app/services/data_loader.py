from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import pandas as pd

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
        self._results: pd.DataFrame | None = None
        self._last_fetch: datetime | None = None

    def load_results(self) -> pd.DataFrame:
        if self._results is None:
            df = pd.read_csv(RESULTS_PATH)
            df["date"] = pd.to_datetime(df["date"])
            df["home_team"] = df["home_team"].map(normalize)
            df["away_team"] = df["away_team"].map(normalize)
            df["home_score"] = pd.to_numeric(df["home_score"], errors="coerce")
            df["away_score"] = pd.to_numeric(df["away_score"], errors="coerce")
            df = df.dropna(subset=["home_score", "away_score"])
            self._results = df
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

    def get_training_data(self, since: str = "2018-01-01") -> pd.DataFrame:
        df = self.load_results()
        cutoff = pd.to_datetime(since)
        return df[df["date"] >= cutoff].copy()

    @property
    def last_fetch(self) -> datetime | None:
        return self._last_fetch


loader = DataLoader()
