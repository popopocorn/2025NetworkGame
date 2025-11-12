#pragma once
#include "Common.h"
#include <array>

#pragma pack(1)
struct chars_info {
	float my_char_hp;
	location other_char_location[PLAYER_COUNT];
	char other_char_state[PLAYER_COUNT][5];
	float time_remaining;
};

struct chars_skills_info {
	chars_info characters;
	skill_info skill[PLAYER_COUNT];
};
#pragma pack()





struct player {
	SOCKET sock{};
	float x{};
	float y{};
	char state[5]{};
	float hp{};

	player() {};
};

struct skill {
	int frame{};
	float x;
	float y;
	char type;
	float attack_power;

	skill(float x, float y, char type, float attack_power) : x{ x }, y{ y }, type{ type }, attack_power{ attack_power } {};
	void update();
	RECT get_bb() const;
};

class game_manager
{
	std::array<player, PLAYER_COUNT> players;
	std::array<skill, PLAYER_COUNT> skills;

	void add_player(int id, const SOCKET& sock);
	void update();
	bool intersects(RECT aabb1, RECT aabb2) const;
	void handle_collsion();
	void broadcast() const;
	bool end_game();
};

