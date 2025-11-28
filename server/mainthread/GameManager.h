#pragma once
#include "Common.h"
#include "Timer.h"

////////////////////////////////////////////////////////////////////////////////////////////
// For Send
#pragma pack(1)
struct chars_info {
	float my_char_hp;								// hp : 4바이트
	float time_remaining;							// 남은 시간 : 4바이트
	std::array<char_info, PLAYER_COUNT - 1> others; // 13*2 : 26바이트
	void hton() {
		my_char_hp = network::htonf(my_char_hp);
		time_remaining = network::htonf(time_remaining);
		for (char_info& other : others) {
			other.hton();
		}
	}
};

struct chars_skills_info {
	chars_info characters{};							// chars_info : 34바이트
	std::array<skill_info, 4> skills{};					// 스킬 : 17*4 = 68바이트

	void hton() {
		characters.hton();
		for (skill_info& info : skills) {
			info.hton();
		}
	}
};
#pragma pack()

////////////////////////////////////////////////////////////////////////////////////////////
// For Update (실제 서버에서 다루는 오브젝트들)
struct player {
	int id					{ -1 };
	SOCKET sock				{};
	location loc			{};
	char state[5]			{"NULL"};
	float hp				{};

	void print() const {
		// [update] ID : 1 === Char : (x, y) = (1557.1557, 888.4844), State = Idle
		std::print("\r[update] ID : {} === Char : (x, y) = ({}, {}), State = {}\t\t\t\n", id, loc.x, loc.y, state);
	}
};

struct skill_object {
	int frame				{};
	location loc			{};
	char type				{};
	float attack_power		{};

	skill_object() {};
	skill_object(float x, float y, char type, float attack_power)
		: frame{}, loc{ x, y }, type{ type }, attack_power{ attack_power }		{};
	void update();
	RECT get_bb() const;
};
////////////////////////////////////////////////////////////////////////////////////////////

class game_manager
{
public:
	std::array<player, PLAYER_COUNT> players					{};
	std::array<skill_object, PLAYER_COUNT * 2> skills			{};


	std::array<chars_skills_info, PLAYER_COUNT> send_info{}; // update에서 스킬 생성자 전달 / players, skills 에서 정보 획득

	timer game_timer											{};

	void add_player(const player_info& info);
	void update();
	bool intersects(const RECT& aabb1, const RECT& aabb2) const;
	void handle_collsion();
	void broadcast();
	bool end_game();
};

