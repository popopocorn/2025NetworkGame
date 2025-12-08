import struct


class char_info:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.state = 'Idle\0'
        self.direction = 'r'.encode('ascii')
        self.jump = False
        self.heart = False

    # 전송 전 데이터를 구조체로 묶기 위한 함수       # 신태양 11/06
    def packing(self):
        # 전송을 위해 문자열을 ASCII로 인코딩
        state_bytes = self.state.encode('ascii')

        # 좌표-x : float 4바이트
        # 좌표-y : float 4바이트
        # 상태 : char 5바이트
        # 방향 : char 1바이트
        # 점프 : bool 1바이트                    # 신태양 12/05
        # heart : bool 1바이트                  # 신태양 12/05
        return struct.pack('!ff5s1s??', self.x, self.y, state_bytes, self.direction, self.jump, self.heart)

    # 현재 player의 정보로 내용 업데이트        # 신태양 11/06
    def update(self,player):
        self.x = player.player_x
        self.y = player.player_y
        self.state = player.state_machine.get_current_state_name()
        self.direction = player.direction.encode('ascii')
        self.jump = player.player_jump
        self.heart = player.player_heart

    def __repr__(self):
        return f"Char(location=({self.x},{self.y}), state={self.state}), direction={self.direction}, jump={self.jump}, heart={self.heart}"

class skill_info:
    def __init__(self):
        self.skill_id = -1
        self.x = 0.0
        self.y = 0.0
        self.skill_direction = 'r'.encode('ascii')
        self.skill_ad = 0.0

    # 전송 전 데이터를 구조체로 묶기 위한 함수       # 신태양 11/06
    def packing(self):
        # 스킬 id : int 4바이트
        # 좌표-x : float 4바이트
        # 좌표-y : float 4바이트
        # 상태 : char 1바이트
        # 공격력 : float 4바이트
        return struct.pack('!iff1sf', self.skill_id, self.x, self.y, self.skill_direction, self.skill_ad)

    # 현재 player의 정보로 내용 업데이트        # 신태양 11/06
    def update(self,skill_id,player):
        self.skill_id = skill_id
        self.x = player.player_x
        self.y = player.player_y
        self.skill_direction = player.direction.encode('ascii')
        self.skill_ad = player.ad
    # 스킬 생성 정보는 딱 한번만 보내기 위해 선언된 함수     # 신태양 11/06
    def disable(self):
        self.skill_id = -1

    def __repr__(self):
        if self.skill_id == -1:
            return f"SKILL()"
        return f"SKILL(id = {self.skill_id}, location=({self.x},{self.y}), direction={self.skill_direction}, ad={self.skill_ad})"

#서버에서 받은 chars_skills_info 구조체를 unpack하기 위한 클래스 강민서11/12
class chars_skills_info:
    def __init__(self):
        self.my_char_hp=0.0
        self.other_chars=[char_info(), char_info()]
        self.time_remaining=0.0
        self.skills = [skill_info() for _ in range(4)]

    def display(self):
        print(f"HP: {self.my_char_hp}, Time: {self.time_remaining}, Other Chars: {self.other_chars}, Skills: {self.skills}")


class Send_buffer:
    def __init__(self):
        self.char_info = char_info()
        self.skill_info = skill_info()

    # 전송 전 데이터를 구조체로 묶기 위한 함수       # 신태양 11/06
    # char_info(12바이트)와 skill_info(19바이트)를 묶는다.
    # 총 31바이트
    def packing(self):
        return self.char_info.packing() + self.skill_info.packing()
