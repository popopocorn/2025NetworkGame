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
    int frame{};                
    location loc{};
    int type{ -1 };             // -1=비활성, 0=Aura_blade, 1=Aura, 2=Brandish
    int direction{};
    float attack_power{};

    int owner_id{ -1 };

    skill_object() = default;

    skill_object(float x, float y, int skill_type, float ad, int dir)
        : frame{ 0 }, loc{ x, y }, type{ skill_type }, direction{ dir }, attack_power{ ad } {}

    void update()
    {
        // Aura 화면 벗어나면 사라짐
        if (type == 1) {
            const float speed = 10.0f;
            loc.x += direction * speed;
            if (loc.x > 1500.0f || loc.x < 0.0f) {
                type = -1;
                frame = 0;
                return;
            }
        }

        //// brandish 0.78초 뒤에 사라짐 (구현이 안됨)
        //float elapsed_time = 0;
        //float dt = game_timer.get_delta_time();
        //elapsed_time += dt;

        //if (type == 2) 
        //{
        //    float brandish_time= 0.78f;

        //    if (elapsed_time >= brandish_time) {
        //        type = -1;      // 빈 슬롯 표시
        //        frame = 0;
        //        return;
        //    }
        //}
    }

    // 충돌 박스
    aabb get_bb()
    {
        aabb box{};

        if (type < 0) {
            box.min_x = box.max_x = box.min_y = box.max_y = 0.0f;
            return box;
        }

        switch (type)
        {
        //case 0: // Aura_blade 
        //    box.min_x = loc.x - 20.0f;
        //    box.max_x = loc.x + 20.0f;
        //    box.min_y = loc.y - 20.0f;
        //    box.max_y = loc.y + 20.0f;
        //    break;

        case 1: // Aura 
            if (direction == 1) {
                box.min_x = loc.x + 50.0f;
                box.max_x = loc.x + 150.0f;
            }
            else {
                box.min_x = loc.x - 150.0f;
                box.max_x = loc.x - 50.0f;
            }
            box.min_y = loc.y - 50.0f;
            box.max_y = loc.y + 50.0f;
            break;

        case 2: // Brandish
            if (direction == 1) {
                box.min_x = loc.x;
                box.max_x = loc.x + 120.0f;
            }
            else {
                box.min_x = loc.x - 130.0f;
                box.max_x = loc.x;
            }
            box.min_y = loc.y - 70.0f;
            box.max_y = loc.y + 100.0f;  
            break;

        default:
            box.min_x = box.max_x = box.min_y = box.max_y = 0.0f;
            break;
        }

        return box;
    }
};
    


////////////////////////////////////////////////////////////////////////////////////////////

class game_manager
{
public:
	std::array<player, PLAYER_COUNT> players					{};
	std::array<skill_object, PLAYER_COUNT * SKILL_COUNT> skills	{};


	std::array<chars_skills_info, PLAYER_COUNT> send_info{}; // update에서 스킬 생성자 전달 / players, skills 에서 정보 획득

	timer game_timer                                            {};

	void add_player(const player_info& info);
	void update();
	bool intersects(const RECT& aabb1, const RECT& aabb2) const;
	void handle_collision();
	void broadcast();
	bool end_game();
};

