#define _WINSOCK_DEPRECATED_NO_WARNINGS
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <iostream>
#include "Common.h"     // err_quit, err_display 선언/정의

struct location // 캐릭터 위치
{
    float x;
    float y;
};

struct char_info // 캐릭터 정보
{
    location loc;
    char state[5];   // "Idle", "Run"
};

struct skill_info // 스킬 정보
{
    int   skill_id;
    location loc;
    char  skill_direction;
    float skill_ad;
};


// --------------------------- main부분 ---------------------------------
int main()
{
    WSADATA wsa;
    SOCKET server_sock, client_sock;
    struct sockaddr_in server_addr, client_addr;

    // 윈속 초기화
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0)
    {
        err_quit("WSAStartup()");
    }

    // 소켓 생성
    server_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (server_sock == INVALID_SOCKET)
    {
        err_quit("socket()");
    }

    // 바인드
    server_sock = socket(AF_INET, SOCK_STREAM, 0);
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(40000);

    if (bind(server_sock, (sockaddr*)&server_addr, sizeof(server_addr)) == SOCKET_ERROR)
    {
        err_quit("bind()");
    }

    // 리슨
    if (listen(server_sock, SOMAXCONN) == SOCKET_ERROR)
    {
        err_quit("listen()");
    }

    std::cout << "Server listen...\n";

    while (true)
    {
        sockaddr_in client_addr{};
        int client_size = sizeof(client_addr);

        SOCKET client_sock = accept(server_sock, (sockaddr*)&client_addr, &client_size);
        if (client_sock == INVALID_SOCKET)
        {
            err_display("accept()");
            continue;
        }

        std::cout << "클라이언트 연결됨: "
            << inet_ntoa(client_addr.sin_addr) << std::endl;

        // 루프 돌면서 클라에서 char_info 받기
        while (true)
        {
            char_info info{};
            int ret = recv(client_sock, (char*)&info, sizeof(info), 0);

            if (ret == 0)
            {
                // 클라 연결 종료
                std::cout << "클라이언트 연결 끊김\n";
                break;
            }
            else if (ret == SOCKET_ERROR)
            {
                // recv 에러 출력
                err_display("recv()");
                break;
            }

            std::cout << "[server] CharInfo x = " << info.loc.x
                << " y = " << info.loc.y
                << " state = " << info.state << std::endl;
        }

        closesocket(client_sock);
    }

    closesocket(server_sock);
    WSACleanup();
    return 0;
}
