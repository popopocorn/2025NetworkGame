#include <winsock2.h> // 윈속2 메인 헤더
#include <ws2tcpip.h> // 윈속2 확장 헤더

#include <iostream>
#include <print>
#include <mutex>

#define PLAYER_COUNT 3

extern std::mutex buffer_gaurd;

extern void err_quit(const char* msg);
extern void err_display(const char* msg);
extern void err_display(int errcode);

inline float ntohf(const float& network_float) {
	int temp;
	::memcpy(&temp, &network_float, sizeof(float));
	temp = ntohl(temp);
	float result;
	::memcpy(&result, &temp, sizeof(float));
	return result;
}

#pragma pack(1)
// 캐릭터 위치
struct location
{
	float x;
	float y;

	void ntoh() {
		x = ntohf(x);
		y = ntohf(y);
	}
};

// 캐릭터 정보
struct char_info
{
	location loc;
	char state[5];   // "Idle\0"

	void ntoh() {
		loc.ntoh();
	}
};

// 스킬 생성자 정보
struct skill_info
{
	int   skill_id;
	location loc;
	char  skill_direction;
	float skill_ad;

	void ntoh() {
		skill_id = ntohl(skill_id);
		loc.ntoh();
		skill_ad = ntohf(skill_ad);
	}
};

struct char_skill_info {
	char_info character;
	skill_info skill;

	void ntoh() {
		character.ntoh();
		skill.ntoh();
	}

	void print() const {
		// [server] Char : (x, y) = (1557.1557, 888.4844), State = Idle
		std::print("[server] Char : (x, y) = ({}, {}), State = {}\n", character.loc.x, character.loc.y, character.state);

		if (skill.skill_id != -1) {

			// [server] Skill : id = 1, (x, y) = (1557.1557, 888.4844), Direction = l, ad : 99999
			std::print("[server]  Skill : id = {}, (x, y) = ({}, {}), Direction = {}, ad : {}\n",
				skill.skill_id, skill.loc.x, skill.loc.y, skill.skill_direction, skill.skill_ad);

		}
	}
};
#pragma pack()