#include <winsock2.h> // 윈속2 메인 헤더
#include <ws2tcpip.h> // 윈속2 확장 헤더

#include <iostream>
#include <array>
#include <print>

// 소켓 함수 오류 출력 후 종료
void err_quit(const char* msg)
{
	LPVOID lpMsgBuf;
	FormatMessageA(
		FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
		NULL, WSAGetLastError(),
		MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
		(char*)&lpMsgBuf, 0, NULL);
	MessageBoxA(NULL, (const char*)lpMsgBuf, msg, MB_ICONERROR);
	LocalFree(lpMsgBuf);
	exit(1);
}

// 소켓 함수 오류 출력
void err_display(const char* msg)
{
	LPVOID lpMsgBuf;
	FormatMessageA(
		FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
		NULL, WSAGetLastError(),
		MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
		(char*)&lpMsgBuf, 0, NULL);
	std::print("{} - {}\n", msg, (char*)lpMsgBuf);
	LocalFree(lpMsgBuf);
}

// 소켓 함수 오류 출력
void err_display(int errcode)
{
	LPVOID lpMsgBuf;
	FormatMessageA(
		FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
		NULL, errcode,
		MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
		(char*)&lpMsgBuf, 0, NULL);
	printf("[오류] %s\n", (char*)lpMsgBuf);
	LocalFree(lpMsgBuf);
}

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


//서버에서 클라이언트로 보내는 정보 일단 서버에서 skill 처리 전까지는 skill은 전부 id: -1 로 전송
struct chars_skills_info {
	float player_hp;
	float remained_time;
	char_info others[2];
	skill_info other_skills[4];
};