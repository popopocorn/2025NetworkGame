import struct


class char_info:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.state = 'Idle\0'

    # 전송 전 데이터를 구조체로 묶기 위한 함수       # 신태양 11/06
    def packing(self):
        # 전송을 위해 문자열을 ASCII로 인코딩
        state_bytes = self.state.encode('ascii')

        # 좌표-x : float 4바이트
        # 좌표-y : float 4바이트
        # 상태 : char 5바이트
        return struct.pack('!ff5s', self.x, self.y, state_bytes)

    # 현재 player의 정보로 내용 업데이트        # 신태양 11/06
    def update(self,player):
        self.x = player.player_x
        self.y = player.player_y
        self.state = player.state_machine.get_current_state_name()

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
        print(player.player_x, player.player_y, player.ad)
    # 스킬 생성 정보는 딱 한번만 보내기 위해 선언된 함수     # 신태양 11/06
    def disable(self):
        self.skill_id = -1

#서버에서 받은 chars_skills_info 구조체를 unpack하기 위한 클래스 강민서11/12
class chars_skills_info:
    def __init(self):
        self.my_char_hp=0.0
        self.other_chars=[]
        self.time_remaining=0.0
        self.skills = []


class Send_buffer:
    def __init__(self):
        self.char_info = char_info()
        self.skill_info = skill_info()

    # 전송 전 데이터를 구조체로 묶기 위한 함수       # 신태양 11/06
    # char_info(12바이트)와 skill_info(19바이트)를 묶는다.
    # 총 31바이트
    def packing(self):
        return self.char_info.packing() + self.skill_info.packing()
    
class recv_buffer:
    def __init__(self):
        self.recved_info = []