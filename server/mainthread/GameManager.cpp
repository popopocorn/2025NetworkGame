#include "GameManager.h"

void game_manager::broadcast() const
{
	{
		std::lock_guard<std::mutex> lock(buffer_gaurd);
		for (int id = 0; id < PLAYER_COUNT; ++id) {
			chars_skills_info info;

			info.characters.my_char_hp = players[id].hp;
			info.characters.time_remaining = 15.57f;				// 수정 필요

			for (int i = 0; i < PLAYER_COUNT - 1; ++i) {
				::memcpy(&info.characters.other_char_location[i].x,	&players[(id + 1 + i) % PLAYER_COUNT].x, sizeof(float) * 2);

				::memcpy(&info.characters.other_char_state[i],	&players[(id + 1 + i) % PLAYER_COUNT].state, 5);
				
				::memcpy(&info.skill[i], &skills[(id + 1 + i) % PLAYER_COUNT], sizeof(skill));
			}

			send(players[id].sock, (char*)&info, sizeof(chars_skills_info), 0);
		}

	}
}
