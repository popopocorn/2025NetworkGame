#include "GameManager.h"

void game_manager::start_game()
{
	for (auto p : players) {
		send(p.sock, (const char*)'1', 1, 0);
	}
}

void game_manager::add_player(const player_info& info)
{
	std::lock_guard<std::mutex> lock(buffer_gaurd);
	if (info.id < 0 or info.id > PLAYER_COUNT) { return; }
	players[info.id].id = info.id;
	players[info.id].sock = info.sock;
}

void game_manager::update()
{
	game_timer.tick(60.0f);

	std::array<player, PLAYER_COUNT> temp;
	{
		std::lock_guard<std::mutex> buffer_lock(buffer_gaurd);
		::memcpy(temp.data(), players.data(), temp.size() * sizeof(player));

	}
}

bool game_manager::intersects(const RECT& aabb1, const RECT& aabb2) const
{
	if (aabb1.right < aabb2.left)   return false;
	if (aabb1.bottom < aabb2.top)    return false;
	if (aabb1.left > aabb2.right)  return false;
	if (aabb1.top > aabb2.bottom) return false;
	return true;
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
				send_info[id].characters.others[i].direction = players[offset].direction;
				send_info[id].characters.others[i].jump = players[offset].jump;
				send_info[id].characters.others[i].heart = players[offset].heart;
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
