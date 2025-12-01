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
    int frame{};                // 프레임 인덱스 (원하면 유지)
    location loc{};
    int type{ -1 };             // -1=비활성, 0=Aura_blade, 1=Aura, 2=Brandish
    int direction{};
    float attack_power{};

    skill_object() = default;

    skill_object(float x, float y, int skill_type, float ad, int dir)
        : frame{ 0 }, loc{ x, y }, type{ skill_type }, direction{ dir }, attack_power{ ad } {}

    void update()
    {
        if (type < 0)
            return;

        // 서버 틱을 60fps로 가정 (한 틱당 약 0.016초)
        constexpr float FRAME_TIME = 1.0f / 60.0f;
        float brandish_time = 0.0f;

        // ----- Aura (type == 1) : 이동 + 화면 밖이면 삭제 -----
        if (type == 1) {
            const float speed = 10.0f;
            loc.x += direction * speed;

            if (loc.x > 1500.0f || loc.x < 0.0f) {
                type = -1;
                frame = 0;
                brandish_time = 0.0f;
                return;
            }
        }

        // ----- Brandish (type == 2) : 0.78초 후 삭제 -----
		if (type == 2) {
			constexpr float BRANDISH_DURATION = 0.78f;
			brandish_time += FRAME_TIME;   // 이번 틱 경과 시간 누적

			if (brandish_time >= BRANDISH_DURATION) {
				type = -1;   // 비활성
				frame = 0;
				brandish_time = 0.0f;
				return;
			}
		}
    }
    RECT get_bb()
    {
        RECT rc{};
        if (type < 0) return rc;

        switch (type)
        {
        case 0: // Aura_blade : 파이썬 Aura_blade는 히트박스 안 썼지만, 대충 플레이어 주변 박스
            rc.left = static_cast<LONG>(loc.x) - 25;
            rc.right = static_cast<LONG>(loc.x) + 25;
            rc.top = static_cast<LONG>(loc.y) - 25;
            rc.bottom = static_cast<LONG>(loc.y) + 25;
            break;

        case 1: // Aura (발사체) - 파이썬 Aura.get_bb 그대로
            if (direction == 1) {
                rc.left = static_cast<LONG>(loc.x + 50);
                rc.top = static_cast<LONG>(loc.y - 50);
                rc.right = static_cast<LONG>(loc.x + 150);
                rc.bottom = static_cast<LONG>(loc.y + 50);
            }
            else {
                rc.left = static_cast<LONG>(loc.x - 150);
                rc.top = static_cast<LONG>(loc.y - 50);
                rc.right = static_cast<LONG>(loc.x - 50);
                rc.bottom = static_cast<LONG>(loc.y + 50);
            }
            break;

        case 2: // Brandish - 파이썬 Brandish.get_bb 그대로
            if (direction == 1) {
                rc.left = static_cast<LONG>(loc.x);
                rc.top = static_cast<LONG>(loc.y - 70);
                rc.right = static_cast<LONG>(loc.x + 120);
                rc.bottom = static_cast<LONG>(loc.y + 100);
            }
            else {
                rc.left = static_cast<LONG>(loc.x - 130);
                rc.top = static_cast<LONG>(loc.y - 70);
                rc.right = static_cast<LONG>(loc.x);
                rc.bottom = static_cast<LONG>(loc.y + 90);
            }
            break;
        default:
            break;
        }
        return rc;
    }
};
    


////////////////////////////////////////////////////////////////////////////////////////////

class game_manager
{
public:
	std::array<player, PLAYER_COUNT> players					{};
	std::array<skill_object, PLAYER_COUNT * SKILL_COUNT> skills	{};


	std::array<chars_skills_info, PLAYER_COUNT> send_info{}; // update에서 스킬 생성자 전달 / players, skills 에서 정보 획득

	timer game_timer											{};

	void add_player(const player_info& info);
	void update();
	bool intersects(const RECT& aabb1, const RECT& aabb2) const;
	void handle_collision();
	void broadcast();
	bool end_game();
};

