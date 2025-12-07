#pragma once
#include "Common.h"
#include "Timer.h"

////////////////////////////////////////////////////////////////////////////////////////////
// For Send
#pragma pack(1)
struct chars_info {
	float my_char_hp;								// hp : 4바이트
	float time_remaining;							// 남은 시간 : 4바이트
	std::array<char_info, PLAYER_COUNT - 1> others; // 15*2 : 30바이트
	void hton() {
		my_char_hp = network::htonf(my_char_hp);
		time_remaining = network::htonf(time_remaining);
		for (char_info& other : others) {
			other.hton();
		}
	}
};

struct chars_skills_info {
	chars_info characters{};							// chars_info : 38바이트
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
	char direction			{};
	bool jump				{};
	bool heart				{};
	float hp				{};

	void print() const {
		// [update] ID : 1 === Char : (x, y) = (1557.1557, 888.4844), State = Idle
		std::print("\r[update] ID : {} === Char : (x, y) = ({}, {}), State = {}\t\t\t\n", id, loc.x, loc.y, state);
	}
	RECT get_bb() const;
};

struct skill_object {
	int frame				{};
	location loc			{};
	char type				{};
	float attack_power		{};
    int direction           {};

    int owner_id        { -1 };

	skill_object() {};
	skill_object(float x, float y, char type, float attack_power, int dir)
        : frame{}, loc{ x, y }, type{ type }, attack_power{ attack_power }, direction{ dir } {};

    void update()
    {
        // Aura 화면 벗어나면 사라짐
        if (type == 1) 
        {
            frame++;
            attack_power = 80; // 공격력 80
            float speed = 10.0f;
            if (direction == 1)
            {
                loc.x += direction * speed;
            }
            if (direction != 1)
            {
                loc.x += direction * speed;
            }
            if (loc.x > 1500.0f || loc.x < 0.0f) {
                type = -1;
                frame = 0;
                return;
            }
        }
    
        // 0.78초 뒤에 사라짐 1프레임당 0.16초
        if (type == 2)
        {            
            int BRANDISH_FRAMES = 11;
            attack_power = 120; // 공격력 120
            frame++;

            if (frame >= BRANDISH_FRAMES)
            {
                type = -1;         
                frame = 0;
                return;
            }       
        }
    }

    // 충돌 박스
    RECT get_bb()
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
                box.left = static_cast<LONG>(loc.x);
                box.right = static_cast<LONG>(loc.x + 150.0f);
            }
            else {                 // 왼쪽 공격
                box.left = static_cast<LONG>(loc.x - 150.0f);
                box.right = static_cast<LONG>(loc.x);
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
};
    
////////////////////////////////////////////////////////////////////////////////////////////
class game_manager
{
public:
	std::array<player, PLAYER_COUNT> players					{};
    std::array<skill_object, PLAYER_COUNT* SKILL_COUNT> skills  {};
	std::array<chars_skills_info, PLAYER_COUNT> send_info{}; // update에서 스킬 생성자 전달 / players, skills 에서 정보 획득

	timer game_timer                                            {};

	void start_game();
	void add_player(const player_info& info);
	void update();
	bool intersects(const RECT& aabb1, const RECT& aabb2) const;
	void handle_collision();
	void broadcast();
	bool end_game();
};
