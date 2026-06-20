import type { StandingRow } from "../types";

interface Props {
  standings: Record<string, StandingRow[]>;
}

export function StandingsTable({ standings }: Props) {
  const groups = Object.keys(standings).sort();

  if (groups.length === 0) {
    return <p className="empty">No group standings yet — matches haven&apos;t started.</p>;
  }

  return (
    <div className="standings-grid">
      {groups.map((group) => (
        <div key={group} className="standings-group">
          <h3>{group}</h3>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Team</th>
                <th>P</th>
                <th>W</th>
                <th>D</th>
                <th>L</th>
                <th>GD</th>
                <th>Pts</th>
              </tr>
            </thead>
            <tbody>
              {standings[group].map((row) => (
                <tr key={row.team} className={row.position <= 2 ? "qualify" : ""}>
                  <td>{row.position}</td>
                  <td className="team-name">{row.team}</td>
                  <td>{row.played}</td>
                  <td>{row.won}</td>
                  <td>{row.drawn}</td>
                  <td>{row.lost}</td>
                  <td className={row.gd > 0 ? "pos" : row.gd < 0 ? "neg" : ""}>
                    {row.gd > 0 ? `+${row.gd}` : row.gd}
                  </td>
                  <td className="pts">{row.points}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}
