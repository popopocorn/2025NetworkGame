#include "GameManager.h"

// 모든 플레이어한테 정보를 보내는 함수										// 신태양 11/13
void game_manager::broadcast()
{
	{
		// players에서 정보 읽어오기 위함.
		std::lock_guard<std::mutex> lock(buffer_gaurd);

		for (int id = 0; id < PLAYER_COUNT; ++id) {
			
			// hp
			send_info.characters.my_char_hp = players[id].hp;				
			send_info.characters.time_remaining = 15.57f;

			for (int i = 0; i < PLAYER_COUNT - 1; ++i) {
				// 0번 플레이어 : 1번, 2번
				// 1번 플레이어 : 2번, 0번
				// 2번 플레이어 : 0번, 1번
				int offset{ (id + 1 + i) % PLAYER_COUNT };

				//
				send_info.characters.others[i].loc.x = players[offset].x;
				send_info.characters.others[i].loc.y = players[offset].y;
				::memcpy(send_info.characters.others[i].state, players[offset].state, 5);
			}
			// skill 객체의 생성자는 update()에서 받아옴을 기대함

			// 남은 시간. 추후 Timer 작성 후, 수정 필요
				
			send_info.hton();
			send(players[id].sock, (char*)&send_info, sizeof(chars_skills_info), 0);
		}

		// 스킬 생성자 정보는 한번만 보낸다.
		for (skill_info& skill : send_info.skill) {
			skill.disable();
		}

	}
}
