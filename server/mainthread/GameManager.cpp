#include "GameManager.h"

void game_manager::start_game()
{
	char start_message{ '1' };
	for (auto p : players) {
		send(p.sock, &start_message, 1, 0);
	}
	game_timer.restore();
	time_remaining = 15.0f; // 테스트용
	//time_remaining = INIT_GAME_TIME;
	
	SetEvent(start_event);

	std::print("[SERVER] Game Start\n");
}

void game_manager::add_player(const player_info& info)
{
	std::lock_guard<std::mutex> lock(buffer_gaurd);
	if (info.id < 0 or info.id > PLAYER_COUNT) { return; }
	players[info.id].id = info.id;
	players[info.id].sock = info.sock;
	players[info.id].hp = INIT_HP;
	players[info.id].heart = false;
}

void game_manager::handle_collision()
{
	for (skill_object& s : skills)
	{
		if (s.type < 0)  
			continue;
		//std::print("[DEBUG] Skill{:03} is enabled\n", static_cast<int>(s.type));
		// 스킬의 AABB
		RECT skill_bb = s.get_bb();

		for (player& p : players)
		{
			if (p.id < 0) { continue; }
			if (p.heart) { continue; }
			if (p.id == s.owner_id) { continue; }   // 자기 스킬은 판정 제외
			
			

			RECT player_bb = p.get_bb();

			if (intersects(skill_bb, player_bb))
			{
				std::print("[GAME] Player{:03} collieds with Skill{:03}(owned by Player{:03})\n", p.id, static_cast<int>(s.type), s.owner_id);
				std::print("\tcollision info : Player{:03} - LT : ({}, {}), RB : ({}, {}) / Skill{:03} - LT : ({}, {}), RB : ({}, {})\n",
					p.id, player_bb.left, player_bb.top, player_bb.right, player_bb.bottom,
					static_cast<int>(s.type), skill_bb.left, skill_bb.top, skill_bb.right, skill_bb.bottom);

				p.hp -= s.attack_power;
				p.heart = true;

				if (p.hp <= 0.0f) {
					p.hp = 0.0f;
					int& score{ players[s.owner_id].score };
					std::print("[GAME] Player{:03} is dead\n[GAME] Player{:03}'s Score : {} + 1 = {}\n",p.id, s.owner_id, score, score + 1);
					++players[s.owner_id].score;
					p.non_hit_time = PLAYER_MAX_DEAD_TIME;
				}
				else {
					p.non_hit_time = PLAYER_MAX_NON_HIT_TIME;
				}
				break;
			}
		}
	}
}

void game_manager::dispatch()
{
	{
		std::lock_guard<std::mutex> lock(buffer_gaurd);

		local_recv_queue.swap(global_recv_queue);
	}

	while (not local_recv_queue.empty()) {
		// 받은 플레이어 정보 -> player_container
		// loc (x,y) : 8바이트
		// state : 5바이트
		int& id{ local_recv_queue.front().first };

		char_skill_info& info{ local_recv_queue.front().second };
		players[id].loc = info.character.loc;
		::memcpy(&players[id].state, &info.character.state,	sizeof(char_info::state));
		players[id].direction = info.character.direction;
		players[id].jump = info.character.jump;

		// 받은 스킬 생성자 -> send_info
		if (info.skill.skill_id > 0) {

			int skill_insert_offset = id * SKILL_COUNT + info.skill.skill_id - 1;

			skill_object& obj = skills[skill_insert_offset];

			obj.loc = info.skill.loc;
			if ('r' == info.skill.skill_direction) {
				obj.direction = 1;     // 오른쪽
			}
			else {
				obj.direction = -1;    // 왼쪽
			}

			obj.frame = 0.f;
			obj.type = info.skill.skill_id;
			obj.attack_power = info.skill.skill_ad;
			obj.owner_id = id;


			for (int i = 0; i < PLAYER_COUNT - 1; ++i) {

				int player_offset{ (id + i + 1) % PLAYER_COUNT };
				chars_skills_info& current_info{ send_info[player_offset] };
				// 0번 플레이어 : 1번-1, 1번-2, 2번-1, 2번-2
				// 1번 플레이어 : 2번-1, 2번-2, 0번-1, 0번-2
				// 2번 플레이어 : 0번-1, 0번-2, 1번-1, 1번-2

				int skill_offset{ (PLAYER_COUNT + id - 1 - player_offset) % PLAYER_COUNT };
				skill_offset *= 2;
				skill_offset += info.skill.skill_id - 1;

				::memcpy(&current_info.skills[+skill_offset], &info.skill, sizeof(skill_info));
			}
		}

		local_recv_queue.pop();
	}


}

void game_manager::update()
{
	game_timer.tick(1000.0f);
	time_remaining -= game_timer.get_delta_time();

	
	
	// 스킬 업데이트
	for (skill_object& skill : skills) {
		skill.update(game_timer.get_delta_time());
	}

	// 플레이어 업데이트
	for (player& p : players) {
		p.update(game_timer.get_delta_time());
	}

}

bool game_manager::intersects(const RECT& a, const RECT& b) const
{
	if (a.right < b.left)   return false;
	if (a.left > b.right)   return false; 
	if (a.bottom < b.top)   return false;
	if (a.top > b.bottom)   return false; 
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
			send_info[id].characters.time_remaining = time_remaining;

			// 피격
			send_info[id].characters.my_char_heart = players[id].heart;

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
			// skill 객체의 생성자는 dispatch()에서 받아옴을 기대함

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

void player::update(float fDeltaTime)
{
	if (heart) {
		non_hit_time -= fDeltaTime;

		if (non_hit_time <= 0.f) {
			heart = false;

			if (hp <= 0.0f) {
				hp = INIT_HP;
			}
		}
	}
}

RECT player::get_bb() const
{
	RECT rc;
	rc.left = static_cast<LONG>(loc.x - 20);
	rc.top = static_cast<LONG>(loc.y - 35);
	rc.right = static_cast<LONG>(loc.x + 10);
	rc.bottom = static_cast<LONG>(loc.y + 30);
	return rc;
}

bool game_manager::end_game()
{
	if (time_remaining >= 0.0f) { return false; } //남은 시간 0초 이상이면 false반환

	std::print("[SERVER] GAME END\n");

	for (auto i = 0; i < PLAYER_COUNT; ++i) {

		std::print("[GAME] Player{:03}'s score : {}\n", i, players[i].score);

		std::array<int, PLAYER_COUNT> score_for_send{};
		for (auto j = 0; j < PLAYER_COUNT; ++j) {
			score_for_send[j] = ::htonl(players[(i + j) % PLAYER_COUNT].score);
		}

		send(players[i].sock, (char*)score_for_send.data(), sizeof(int)*PLAYER_COUNT, 0);

	}


	return true;
}


void skill_object::update(float fDeltaTime)
{
	frame += fDeltaTime;

	switch (type) {
	case 1:	// Aura 화면 벗어나면 사라짐
		{
			loc.x += direction * SKILL_AURA_SPEED * 100 * fDeltaTime;

			if (loc.x > 1500.0f || loc.x < 0.0f) {
				type = -1;
				frame = 0.f;
				return;
			}
		}

		break;

	case 2:
		{
			if (frame >= SKILL_BRANDISH_LIFE_TIME)
			{
				type = -1;
				frame = 0.f;
				return;
			}
		}
		break;
	}
}

RECT skill_object::get_bb()
{
	RECT box{};

	if (type < 0) {
		box.left = box.right = box.top = box.bottom = 0;
		return box;
	}

	switch (type)
	{
	case 0: // Aura_blade 
		box.left = static_cast<LONG>(loc.x - 20.0f);
		box.right = static_cast<LONG>(loc.x + 20.0f);
		box.top = static_cast<LONG>(loc.y - 20.0f);
		box.bottom = static_cast<LONG>(loc.y + 20.0f);
		break;

	case 1: // Aura 
		if (direction == 1) {  // 오른쪽 공격
			box.left = static_cast<LONG>(loc.x - 40.f);
			box.right = static_cast<LONG>(loc.x + 40.f);
		}
		else {                 // 왼쪽 공격
			box.left = static_cast<LONG>(loc.x - 40.f);
			box.right = static_cast<LONG>(loc.x + 40.f);
		}
		box.top = static_cast<LONG>(loc.y - 50.0f);
		box.bottom = static_cast<LONG>(loc.y + 50.0f);
		break;

	case 2: // Brandish
		if (direction == 1) {
			box.left = static_cast<LONG>(loc.x);
			box.right = static_cast<LONG>(loc.x + 120.0f);
		}
		else {
			box.left = static_cast<LONG>(loc.x - 130.0f);
			box.right = static_cast<LONG>(loc.x);
		}
		box.top = static_cast<LONG>(loc.y - 70.0f);
		box.bottom = static_cast<LONG>(loc.y + 100.0f);
		break;

	default:
		box.left = box.right = box.top = box.bottom = 0;
		break;
	}
	return box;
}

