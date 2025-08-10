from datetime import datetime
import re


class Player:
    def __init__(self, player_id, name, number, position, dob, performance_score):
        self.player_id = player_id
        self._name = name
        self.number = number
        self._position = position
        self.dob = dob
        self.performance_score = performance_score

    @property
    def player_id(self):
        return self._player_id if hasattr(self,"_player_id") else None
    @player_id.setter
    def player_id(self,p_id):
        try:
            p_id = int(p_id)
        except ValueError:
            raise ValueError("ID cầu thủ không hợp lệ.")
        self._player_id = p_id

    @property
    def name(self):
        return self._name

    @property
    def number(self):
        return self._number if hasattr(self,"_number") else None
    @number.setter
    def number(self,num):
        try:
            num = int(num)
        except ValueError:
            raise ValueError("Số áo cầu thủ không hợp lệ.")
        self._number = num

    @property
    def position(self):
        return self._position

    @property
    def dob(self):
        return self._dob if hasattr(self,"_dob") else None
    @dob.setter
    def dob(self,d):
        pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(pattern,d):
            raise ValueError("Ngày tháng không hợp lệ.")
        self._dob = d

    @property
    def performance_score(self):
        return self._performance_score if hasattr(self,"_performance_score") else None
    @performance_score.setter
    def performance_score(self,value):
        try:
            value = float(value)
        except ValueError:
            raise ValueError("Điểm phong độ không hợp lệ.")
        self._performance_score = value

#------------------------------------------------------------------------------------
    def update_performance(self, score):
        self._performance_score = score

    def get_age(self):
        birth_date = datetime.strptime(self.dob, "%Y-%m-%d")
        today = datetime.today()
        return today.year - birth_date.year


