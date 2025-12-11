#include "RecvThread.h"

DWORD WINAPI recv_thread(LPVOID arg)
{

	player_info player_sock_info = *(player_info*)(arg);

	delete (player_info*)arg;

	std::print("[System] Create Thread : Recv Thread for Player{:03}\n", player_sock_info.id);

	std::pair<int, char_skill_info> info;
	info.first = player_sock_info.id;

	WaitForSingleObject(start_event, INFINITE);

	while (true)
	{
		// recv_info 부분
		int ret = recv(player_sock_info.sock, (char*)&info.second, sizeof(char_skill_info), 0);
		
		if (ret == 0)
		{
			std::print("[Network] Player{:03}'s Client Connection lost\n", player_sock_info.id);
			break;
		}
		else if (ret == SOCKET_ERROR)
		{
			err_display(std::format("Player{:03}'s Socket recv(:03)", player_sock_info.id).c_str());
			break;
		}

		info.second.ntoh();   // 네트워크 바이트 → 호스트 바이트

		{
			std::lock_guard<std::mutex> lock(buffer_gaurd);
			global_recv_queue.push(info);
		}
		
	}

	std::print("[System] Exit Thread : Recv Thread for Player{}\n", player_sock_info.id);
	closesocket(player_sock_info.sock);
	return 0;
}