#include "Common.h"

std::mutex buffer_gaurd;

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

DWORD WINAPI recv_thread(LPVOID arg)
{
	SOCKET client_sock = (SOCKET)arg;

	char_skill_info info{};

	while (true)
	{
		// recv_info 부분
		int ret = recv(client_sock, (char*)&info, sizeof(info), 0);

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
		info.print();  // 받은 내용 출력 (여기서 \r 써서 한 줄 덮어쓰기도 가능)
	}

	closesocket(client_sock);
	return 0;
}