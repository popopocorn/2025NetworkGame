#include "RecvThread.h"

DWORD WINAPI recv_thread(LPVOID arg)
{
	player_info player_sock_info = *(player_info*)(arg);

	delete (player_info*)arg;

	std::pair<int, char_skill_info> info;
	info.first = player_sock_info.id;

	HANDLE hConsole{ GetStdHandle(STD_OUTPUT_HANDLE) };

	while (true)
	{
		// recv_info 부분
		int ret = recv(player_sock_info.sock, (char*)&info.second, sizeof(char_skill_info), 0);
		
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

		info.second.ntoh();   // 네트워크 바이트 → 호스트 바이트

		{
			std::lock_guard<std::mutex> lock(buffer_gaurd);
			global_recv_queue.push(info);
		}
		
	}

	closesocket(player_sock_info.sock);
	return 0;
}