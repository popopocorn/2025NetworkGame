import socket
import threading
from network_data import *

# 네트워크 설정을 위한 dictionary        # 신태양 11/06
network_config = dict()

# 서버와 통신을 위해 사용되는 소켓        # 신태양 11/06
# IPv4, TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 서버에 데이터 전송을 위해 존재하는 버퍼(컨테이너).     # 신태양 11/06
send_buffer = Send_buffer()

# 동기화를 위한 전역 변수     # 신태양 11/06
# with buffer_lock:
#   print(1557)
#   pass
# 와 같이 사용하면 관리 용이함.
buffer_lock = threading.Lock()

# 네트워크 config 파일을 불러오는 함수       # 신태양 11/06
# 보통은 server.txt를 불러온다.
# 형식은
# [KEY]=[VALUE]
# 공백 없음 주의
def load_network_config(filename):
    global client_socket, network_config
    with open(filename, 'r', encoding='utf-8') as file:
        # 파일 정보를 라인 별로 가져옴
        for line in file:
            if '=' in line:
                # [KEY] = [VALUE]를
                # [KEY]
                # [VALUE]
                # 로 나누고 network_config에 저장
                key, value = line.split('=')
                key = key.strip()
                value = value.strip()
                network_config[key] = value

    # txt 파일을 읽어와서 저장하였으므로 현재 PORT의 값은 문자열
    # 고로 int 등의 정수형으로 변환
    if 'PORT' in network_config:
        network_config['PORT'] = int(network_config['PORT'])

# network_config에 들어있는 값으로 서버와 연결을 시도한다.        # 신태양 11/06
# 성공시 0, 실패시 -1 리턴
def connect():
    global client_socket, network_config
    try:
        client_socket.connect((network_config['IP'], network_config['PORT']))
        return 0
    except:
        print("Failed to connect")
        return -1

# send_buffer에 들어 있는 값을 보낸다.        # 신태양 11/06
# 성공시 0, 실패시 -1 리턴
def send_info():
    global client_socket, send_buffer
    data = send_buffer.packing()
    try:
        # 송신 버퍼에 data(아마 31바이트)가 완전히 복사될때 까지 send()를 반복하는 함수
        # 31바이트씩 보내는걸 보장해준다.
        client_socket.sendall(data)
        # 스킬 생성자 정보는 한번만 보낸다.
        send_buffer.skill_info.disable()
        return 0
    except:
        return -1
