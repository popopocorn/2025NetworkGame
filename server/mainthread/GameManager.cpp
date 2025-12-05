#include "GameManager.h"

void game_manager::add_player(const player_info& info)
{
	std::lock_guard<std::mutex> lock(buffer_gaurd);
	if (info.id < 0 or info.id > PLAYER_COUNT) { return; }
	players[info.id].id = info.id;
	players[info.id].sock = info.sock;
	players[info.id].hp = 100.0f;
}

void game_manager::handle_collision()
{
	for (skill_object& s : skills)
	{
		if (s.type < 0)   // 비어 있는 슬롯이면 스킵
			continue;

		// 스킬의 AABB
		aabb skill_bb = s.get_bb();

		for (player& p : players)
		{
			if (p.id < 0)
				continue;

			aabb player_bb;
			player_bb.min_x = p.loc.x - 25.0f;
			player_bb.max_x = p.loc.x + 25.0f;
			player_bb.min_y = p.loc.y - 50.0f;
			player_bb.max_y = p.loc.y + 50.0f;

			if (::intersects(skill_bb, player_bb))
			{
				p.hp -= s.attack_power;
				if (p.hp < 0.0f) p.hp = 0.0f;

				// 한 번 맞으면 스킬 제거
				s.type = -1;
				s.frame = 0;
				break;
			}
			send_info[p.id].characters.my_char_hp = players[p.id].hp;
		}
	}
}

void game_manager::update()
{
	game_timer.tick(60.0f);

	std::array<player, PLAYER_COUNT> temp;
	{
		std::lock_guard<std::mutex> buffer_lock(buffer_gaurd);
		::memcpy(temp.data(), players.data(), temp.size() * sizeof(player));
	}

	// 스킬 업데이트
	for (skill_object& skill : skills) {
		skill.update();
	}

	// 충돌 + HP 계산
	handle_collision();
}



// 모든 플레이어한테 정보를 보내는 함수										// 신태양 11/13
void game_manager::broadcast()
{
	{
		// players에서 정보 읽어오기 위함.
		std::lock_guard<std::mutex> lock(buffer_gaurd);

		for (int id = 0; id < PLAYER_COUNT; ++id) {
			
			// hp
			send_info[id].characters.my_char_hp = players[id].hp;

			// 남은 시간. 추후 Timer 작성 후, 수정 필요
			send_info[id].characters.time_remaining = 15.57f;

			for (int i = 0; i < PLAYER_COUNT - 1; ++i) {
				// 0번 플레이어 : 1번, 2번
				// 1번 플레이어 : 2번, 0번
				// 2번 플레이어 : 0번, 1번
				int offset{ (id + 1 + i) % PLAYER_COUNT };

				//
				send_info[id].characters.others[i].loc = players[offset].loc;
				::memcpy(send_info[id].characters.others[i].state, players[offset].state, 5);
			}
			// skill 객체의 생성자는 update()에서 받아옴을 기대함
			
		}
	}


	for (int id = 0; id < PLAYER_COUNT; ++id) {
		send_info[id].hton();
		send(players[id].sock, (char*)&send_info[id], sizeof(chars_skills_info), 0);

		// 스킬 생성자 정보는 한번만 보낸다.
		for (skill_info& skill : send_info[id].skills) {
			skill.disable();
		}
	}

}

bool game_manager::end_game()
{
	float end_time = game_timer.get_elapsed_time(); // 시간 3분 지나면 종료
	int   winner_id = -1; //이긴 플레이어 아이디

	if (end_time >= 60.0f) {  
		float best_hp = -1.0f; // 가장 좋은 플레이어의 hp

		// 가장 상태가 좋은 플레이어가 누군지 확인
		for (int i = 0; i < PLAYER_COUNT; ++i)
		{
			player& p = players[i];
			if (p.id >= 0 && p.hp > 0.0f) {
				if (p.hp > best_hp) {
					best_hp = p.hp;
					winner_id = i;
				}
			}
		}
	}

	const char* win_msg = "WIN";  
	const char* lose_msg = "LOSE";

	// 이긴 플레이어에게는 승리메시지 진 플레이어는 패배메시지 전송
	// 연결상태 확인하고 전송? 이건 안됨
	for (int i = 0; i < PLAYER_COUNT; ++i)
	{
		player& p = players[i];

		// 접속 안된 슬롯이면 무시
		if (p.id < 0)           continue;
		if (p.sock == INVALID_SOCKET) continue;

		const char* msg = nullptr;

		if (i == winner_id) {
			msg = win_msg;
		}
		else {
			msg = lose_msg;
		}

		int len = static_cast<int>(std::strlen(msg));
		int ret = send(p.sock, msg, len, 0);
		if (ret == SOCKET_ERROR) {
			err_display("send(end_game msg)");
		}
	}
	return true;
}
