#pragma once
#include <winsock2.h> // 윈속2 메인 헤더
#include <ws2tcpip.h> // 윈속2 확장 헤더

#include <iostream>
#include <array>
#include <queue>
#include <print>
#include <mutex>

#define PLAYER_COUNT 3
#define SKILL_COUNT 2

#define SKILL_AURA_SPEED 10.0f
#define SKILL_BRANDISH_LIFE_TIME 0.78f

#define PLAYER_MAX_NON_HIT_TIME 1.0f

struct char_skill_info;

extern std::queue<std::pair<int, char_skill_info>> global_recv_queue;
extern std::mutex buffer_gaurd;

extern void err_quit(const char* msg);
extern void err_display(const char* msg);
extern void err_display(int errcode);

extern DWORD WINAPI recv_thread(LPVOID arg);


namespace network {
	inline float ntohf(const float& network_float) {
		int temp;
		::memcpy(&temp, &network_float, sizeof(float));
		temp = ntohl(temp);
		float result;
		::memcpy(&result, &temp, sizeof(float));
		return result;
	}

	inline float htonf(const float& host_float) {
		int temp;
		::memcpy(&temp, &host_float, sizeof(float));
		temp = htonl(temp);
		float result;
		::memcpy(&result, &temp, sizeof(float));
		return result;
	}
}

#pragma pack(1)
// 캐릭터 위치
struct location
{
	float x					{};
	float y					{};

	void ntoh() {
		x = network::ntohf(x);
		y = network::ntohf(y);
	}

	void hton() {
		x = network::htonf(x);
		y = network::htonf(y);
	}
};

// 캐릭터 정보
struct char_info
{
	location loc			{};
	char state[5]			{"NULL"};   // "Idle\0"
	char direction			{};
	char jump				{};
	char heart				{};

	void ntoh() {
		loc.ntoh();
	}

	void hton() {
		loc.hton();
	}
};

// 스킬 생성자 정보
struct skill_info
{
	int   skill_id			{-1};
	location loc			{};
	char  skill_direction	{};
	float skill_ad			{};

	void ntoh() {
		skill_id = ntohl(skill_id);
		loc.ntoh();
		skill_ad = network::ntohf(skill_ad);
	}

	void hton() {
		skill_id = htonl(skill_id);
		loc.hton();
		skill_ad = network::htonf(skill_ad);
	}

	void disable() { skill_id = -1; }
};

struct char_skill_info {
	char_info character;
	skill_info skill;

	void ntoh() {
		character.ntoh();
		skill.ntoh();
	}

	void print(const int& id = -1) const {
		// [server] Char : (x, y) = (1557.1557, 888.4844), State = Idle
		std::print("\r[server] Char : id = {}, (x, y) = ({}, {}), State = {}\t\t\t\n",id, character.loc.x, character.loc.y, character.state);

		if (skill.skill_id != -1) {

			// [server] Skill : id = 1, (x, y) = (1557.1557, 888.4844), Direction = l, ad : 99999
			std::print("\r[server]  Skill : id = {}, (x, y) = ({}, {}), Direction = {}, ad : {}\t\t\t\n",
				skill.skill_id, skill.loc.x, skill.loc.y, skill.skill_direction, skill.skill_ad);

		}
		
	}
};

struct player_info {
	SOCKET sock;
	int id;
};

#pragma pack()