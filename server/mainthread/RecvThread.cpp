#include "RecvThread.h"

DWORD WINAPI recv_thread(LPVOID arg)
{
	player_info player_sock_info = *(player_info*)(arg);

	delete (player_info*)arg;

	char_skill_info info{};

	HANDLE hConsole{ GetStdHandle(STD_OUTPUT_HANDLE) };

	while (true)
	{
		// recv_info 부분
		int ret = recv(player_sock_info.sock, (char*)&info, sizeof(info), 0);

		if (ret == 0)
		{
			// 클라가 정상 종료
			std::cout << "Client Connection lost\n";
			break;
		}
		else if (ret == SOCKET_ERROR)
		{
			err_display("recv()");
			break;
		}

		info.ntoh();   // 네트워크 바이트 → 호스트 바이트
		{
			std::lock_guard<std::mutex> lock(buffer_gaurd);
			// 받은 플레이어 정보 -> player_container
			// loc (x,y) : 8바이트
			// state : 5바이트
			::memcpy(&main_game->players[player_sock_info.id].loc,
					&info.character,
					sizeof(char_info));





			// 받은 스킬 생성자 -> send_info
			if(info.skill.skill_id > 0){

				int skill_insert_offset = player_sock_info.id * SKILL_COUNT + info.skill.skill_id - 1;

				skill_object& obj = main_game->skills[skill_insert_offset];

				obj.loc = info.skill.loc;
				if (info.skill.skill_direction == 'r')
					obj.direction = 1;     // 오른쪽
				else
					obj.direction = -1;    // 왼쪽
				obj.type = info.skill.skill_id;
				obj.attack_power = info.skill.skill_ad;
				obj.owner_id = player_sock_info.id;  
				std::cout << "[RECV DIR] direction = " << info.skill.skill_direction << std::endl;


				for(int i = 0;i<PLAYER_COUNT-1;++i){
					int player_offset { (player_sock_info.id + i + 1) % PLAYER_COUNT };
					chars_skills_info& current_info{ main_game->send_info[player_offset] };
					// 0번 플레이어 : 1번, 1번, 2번, 2번
					// 1번 플레이어 : 2번, 2번, 0번, 0번
					// 2번 플레이어 : 0번, 0번, 1번, 1번

					int skill_offset { (player_sock_info.id + PLAYER_COUNT - 1 - player_offset) % PLAYER_COUNT };
					skill_offset *= 2;
					skill_offset += info.skill.skill_id - 1;
					::memcpy(&current_info.skills[+skill_offset], &info.skill, sizeof(skill_info));
				}
			}
		}
		
	}

	closesocket(player_sock_info.sock);
	return 0;
}