#이벤트 체크 함수 e =(종류, 값)
from sdl2 import *

def start_event(e):
    return e[0]=='START'

def space_down(e): #e가 space down인지 판단
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

def time_out(e):
    return e[0] =='TIME_OUT'

def right_down(e):
    return e[0] =='INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT
def right_up(e):
    return e[0] =='INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT
def left_down(e):
    return e[0] =='INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT
def left_up(e):
    return e[0] =='INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT
def skill_down(e):
    if not isinstance(e[1], int):
        if e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and \
                (e[1].key == SDLK_q or e[1].key == SDLK_w or e[1].key == SDLK_e or e[1].key == SDLK_r):
            return True
    return False






class StateMachine():
    def __init__(self, obj):
        self.obj = obj
        self.event_queue = []
    def start(self, state):
        self.cur_state = state # 시작 상태를 받아 그걸로 현재 상태를 정의
        self.cur_state.enter(self.obj, ('START', 0))
        #print(f'Enter into {state}')
    def update(self):
        self.cur_state.do(self.obj)
        if self.event_queue:
            e = self.event_queue.pop(0)
            #현재 상태와 현재 발생한 이벤트에 따라 다음 상태 결정
            #상태 변환 테이블을 이용
            for check_event, next_state in self.transitions[self.cur_state].items():
                if check_event(e):
                    #print(f'Exit from{self.cur_state}')
                    self.cur_state.exit(self.obj)
                    self.cur_state = next_state
                    self.cur_state.enter(self.obj, e)
                    #print(f'Enter into {self.cur_state}')
                    return
            #print(f'        waring: {e}not hadled at state{self.cur_state}')
    def draw(self):
        self.cur_state.draw(self.obj)
    def add_event(self, e):
        #print(f'    debug: ad event{e}')

        self.event_queue.append(e)
    def set_transitions(self, transitions):
        self.transitions = transitions