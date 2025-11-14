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

			// 받은 스킬 -> ㅁㄹ
			;

		}
		
	}

	closesocket(player_sock_info.sock);
	return 0;
}