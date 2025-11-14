#include <winsock2.h> // 윈속2 메인 헤더
#include <ws2tcpip.h> // 윈속2 확장 헤더

#include <iostream>
#include <array>
#include <print>
#include <mutex>

#define PLAYER_COUNT 3

extern std::mutex buffer_gaurd;

extern void err_quit(const char* msg);
extern void err_display(const char* msg);
extern void err_display(int errcode);

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
	float x;
	float y;

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
	location loc;
	char state[5];   // "Idle\0"

	void ntoh() {
		loc.ntoh();
	}
};

// 스킬 생성자 정보
struct skill_info
{
	int   skill_id			{-1};
	location loc;
	char  skill_direction;
	float skill_ad;

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


//서버에서 클라이언트로 보내는 정보 일단 서버에서 skill 처리 전까지는 skill은 전부 id: -1 로 전송
struct chars_skills_info {
	float player_hp;
	float remained_time;
	char_info others[2];
	skill_info other_skills[4];
};