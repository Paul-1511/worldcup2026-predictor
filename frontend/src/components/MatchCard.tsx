import type { Match } from "../types";

interface Props {
  match: Match;
  compact?: boolean;
}

export function MatchCard({ match, compact = false }: Props) {
  const finished = match.status === "finished";
  const score = finished
    ? `${match.home_score} – ${match.away_score}`
    : "vs";

  return (
    <article className={`match-card ${finished ? "finished" : "upcoming"}`}>
      <header className="match-meta">
        {match.group && <span className="badge group">{match.group}</span>}
        <span className="date">{match.date}</span>
        {match.time && <span className="time">{match.time}</span>}
      </header>
      <div className="match-teams">
        <div className="team home">
          <span className="flag">{flagEmoji(match.home_team)}</span>
          <span className="name">{match.home_team}</span>
        </div>
        <div className={`score ${finished ? "final" : "pending"}`}>{score}</div>
        <div className="team away">
          <span className="name">{match.away_team}</span>
          <span className="flag">{flagEmoji(match.away_team)}</span>
        </div>
      </div>
      {!compact && match.ground && (
        <footer className="match-ground">{match.ground}</footer>
      )}
      {!compact && finished && (match.goals_home.length > 0 || match.goals_away.length > 0) && (
        <div className="scorers">
          {match.goals_home.map((g, i) => (
            <span key={`h${i}`} className="scorer home">
              {g.name} {g.minute}&apos;
            </span>
          ))}
          {match.goals_away.map((g, i) => (
            <span key={`a${i}`} className="scorer away">
              {g.minute}&apos; {g.name}
            </span>
          ))}
        </div>
      )}
    </article>
  );
}

const FLAGS: Record<string, string> = {
  Mexico: "🇲🇽", "South Africa": "🇿🇦", "South Korea": "🇰🇷",
  "Czech Republic": "🇨🇿", Canada: "🇨🇦", "Bosnia & Herzegovina": "🇧🇦",
  Qatar: "🇶🇦", Switzerland: "🇨🇭", Brazil: "🇧🇷", Morocco: "🇲🇦",
  Haiti: "🇭🇹", Scotland: "🏴󠁧󠁢󠁳󠁣󠁴󠁿", Argentina: "🇦🇷", France: "🇫🇷",
  England: "🏴󠁧󠁢󠁥󠁮󠁧󠁿", Spain: "🇪🇸", Germany: "🇩🇪", Portugal: "🇵🇹",
  Netherlands: "🇳🇱", Belgium: "🇧🇪", Italy: "🇮🇹", Croatia: "🇭🇷",
  Japan: "🇯🇵", "United States": "🇺🇸", Uruguay: "🇺🇾", Colombia: "🇨🇴",
  Senegal: "🇸🇳", Ghana: "🇬🇭", Egypt: "🇪🇬", Iran: "🇮🇷",
  "Saudi Arabia": "🇸🇦", Tunisia: "🇹🇳", Sweden: "🇸🇪", Norway: "🇳🇴",
  Ecuador: "🇪🇨", Austria: "🇦🇹", Algeria: "🇩🇿", Jordan: "🇯🇴",
  Panama: "🇵🇦", "DR Congo": "🇨🇩", Uzbekistan: "🇺🇿", Iraq: "🇮🇶",
  "New Zealand": "🇳🇿", "Cape Verde": "🇨🇻",
};

function flagEmoji(team: string): string {
  return FLAGS[team] ?? "⚽";
}
