def start_event(e):
    return e[0]=='START'

def die(e):
    return e[0]=='DIE'

def time_out(e):
    return e[0] =='TIME_OUT'
def Done(e):
    return e[0]=='DONE'
def can_attack(e):
    if (e[1][0] - 200 < e[1][1]) and (e[1][1] < e[1][0] + 200) and e[1] != (0, 0):

        return True


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
            #        print(f'Exit from{self.cur_state}')
                    self.cur_state.exit(self.obj, e)
                    self.cur_state = next_state
                    self.cur_state.enter(self.obj, e)
            #        print(f'Enter into {self.cur_state}')
                    return
            #print(f'        waring: {e}not hadled at state{self.cur_state}')
    def draw(self):
        self.cur_state.draw(self.obj)
    def add_event(self, e):
        #print(f'    debug: ad event{e}')

        self.event_queue.append(e)
    def set_transitions(self, transitions):
        self.transitions = transitions