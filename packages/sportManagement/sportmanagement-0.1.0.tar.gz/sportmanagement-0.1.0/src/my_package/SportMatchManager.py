from team import Team
from match import Match

class SportMatchManager:
    def __init__(self):
        self._teams = []
        self._matches = []

    @property
    def teams(self):
        return self._teams

    @property
    def matches(self):
        return self._matches

    def add_team(self, team:Team):
        self.teams.append(team)

    def get_team_by_id(self, f_id: str):          #đổi lại thành tìm bằng ID
        try:
            f_id = int(f_id)
        except ValueError:
            raise ValueError("ID đội không hợp lệ.")
        for team in self.teams:
            if team.team_id == f_id:
                return team
        raise ValueError(f"Không tìm thấy đội có ID {f_id}")

    def schedule_match(self,match:Match):
        self.matches.append(match)

    def list_matches(self):
        show = "\n===== Các trận đã diễn ra ====="
        for i,match in enumerate(self.matches,1):
            show += f"\n{i}. {match.print_match_summary()}\n--------------------------------------------"
        return show

    def get_top_scorer(self):
        total_points = {}
        for match in self.matches:
            for score in match.score_events:
                if score.player in total_points:
                    total_points[score.player] += score.points
                else:
                    total_points[score.player] = score.points
        return max(total_points, key=lambda player: total_points[player])

    def get_highest_scoring_match(self):
        total_points = {}
        for match in self.matches:
            for score in match.score_events:
                if match in total_points:
                    total_points[match] += score.points
                else:
                    total_points[match] = score.points
        return max(total_points, key=lambda match: total_points[match])

