from __future__ import annotations

from collections import defaultdict
from typing import Any


def compute_standings(matches: list[dict[str, Any]]) -> dict[str, list[dict]]:
    """Compute group standings from finished group-stage matches."""
    groups: dict[str, dict[str, dict]] = defaultdict(
        lambda: defaultdict(
            lambda: {
                "team": "",
                "played": 0,
                "won": 0,
                "drawn": 0,
                "lost": 0,
                "gf": 0,
                "ga": 0,
                "gd": 0,
                "points": 0,
            }
        )
    )

    for m in matches:
        group = m.get("group")
        if not group or not group.startswith("Group"):
            continue
        if m["status"] != "finished":
            continue

        h, a = m["home_team"], m["away_team"]
        hs, aws = m["home_score"], m["away_score"]

        for team in (h, a):
            groups[group][team]["team"] = team

        groups[group][h]["played"] += 1
        groups[group][a]["played"] += 1
        groups[group][h]["gf"] += hs
        groups[group][h]["ga"] += aws
        groups[group][a]["gf"] += aws
        groups[group][a]["ga"] += hs

        if hs > aws:
            groups[group][h]["won"] += 1
            groups[group][h]["points"] += 3
            groups[group][a]["lost"] += 1
        elif hs < aws:
            groups[group][a]["won"] += 1
            groups[group][a]["points"] += 3
            groups[group][h]["lost"] += 1
        else:
            groups[group][h]["drawn"] += 1
            groups[group][a]["drawn"] += 1
            groups[group][h]["points"] += 1
            groups[group][a]["points"] += 1

    result: dict[str, list[dict]] = {}
    for group_name, teams in sorted(groups.items()):
        rows = list(teams.values())
        for r in rows:
            r["gd"] = r["gf"] - r["ga"]
        rows.sort(key=lambda x: (-x["points"], -x["gd"], -x["gf"]))
        for i, r in enumerate(rows, 1):
            r["position"] = i
        result[group_name] = rows

    return result
