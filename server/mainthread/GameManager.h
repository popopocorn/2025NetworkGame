#pragma once
#include "Common.h"
#include <array>

////////////////////////////////////////////////////////////////////////////////////////////
// For Send
#pragma pack(1)
struct chars_info {
	float my_char_hp;								// hp : 4바이트
	float time_remaining;							// 남은 시간 : 4바이트
	char_info others[PLAYER_COUNT-1];				// 13*2 : 26바이트
	void hton() {
		my_char_hp = network::htonf(my_char_hp);
		time_remaining = network::htonf(time_remaining);
		for (char_info& other : others) {
			other.hton();
		}
	}
};

struct chars_skills_info {
	chars_info characters;							// chars_info : 34바이트
	skill_info skill[4];							// 스킬 생성자 : 17*4 = 68바이트

	void hton() {
		characters.hton();
		for (skill_info& info : skill) {
			info.hton();
		}
	}
};
#pragma pack()

////////////////////////////////////////////////////////////////////////////////////////////
// For Update (실제 서버에서 다루는 오브젝트들)
struct player {
	SOCKET sock{};
	float x;
	float y;
	char state[5];
	float hp;
};

struct skill_object {
	int frame;
	float x;
	float y;
	char type;
	float attack_power;

	skill_object(float x, float y, char type, float attack_power)
		: x{ x }, y{ y }, type{ type }, attack_power{ attack_power } {};
	void update();
	RECT get_bb() const;
};
////////////////////////////////////////////////////////////////////////////////////////////

class game_manager
{
	std::array<player, PLAYER_COUNT> players;
	std::array<skill_object, PLAYER_COUNT> skills;

	chars_skills_info send_info;				// update에서 스킬 생성자 전달 / players, skills 에서 정보 획득

	void add_player(const int& id, const SOCKET& sock);
	void update();
	bool intersects(const RECT& aabb1, const RECT& aabb2) const;
	void handle_collsion();
	void broadcast();
	bool end_game();
};

