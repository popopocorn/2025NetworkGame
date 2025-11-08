#define _WINSOCK_DEPRECATED_NO_WARNINGS
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <iostream>
#include "Common.h"

struct location
{
    float x;
    float y;
};

struct char_info      //캐릭터 정보
{
    location loc;
    char state[5];   // "Idle", "Run"
};

struct skill_info     //스킬 정보
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
    int client_size;
    int name_len;

    //윈속 초기화
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0)
    {
        perror("WSAStartup 실패");
        return 1;
    }

    //바인드
    server_sock = socket(AF_INET, SOCK_STREAM, 0);
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(40000);

    if (bind(server_sock, (sockaddr*)&server_addr, sizeof(server_addr)) == SOCKET_ERROR)
    {
        perror("바인드 실패");
        closesocket(server_sock);
        WSACleanup();
        return 1;
    }

    //리슨
    if (listen(server_sock, SOMAXCONN) == SOCKET_ERROR)
    {
        perror("리슨 실패");
        closesocket(server_sock);
        WSACleanup();
        return 1;
    }

    std::cout << "Server listen...\n";

    while (true)
    {
        sockaddr_in client_addr{};
        int client_size = sizeof(client_addr);

        SOCKET client_sock = accept(server_sock, (sockaddr*)&client_addr, &client_size);
        if (client_sock == INVALID_SOCKET)
        {
            std::cout << "accept 실패 또는 서버 종료\n";
            break;
        }

        std::cout << "클라이언트 연결됨: "
            << inet_ntoa(client_addr.sin_addr) << std::endl;

        //루프 돌면서 클라에서 char_info받기
        while (true)
        {
            char_info info{};
            int ret = recv(client_sock, (char*)&info, sizeof(info), 0);
            if (ret <= 0)
            {
                std::cout << "클라이언트 연결 끊김\n";
                break;
            }

            std::cout << "[server] CharInfo x =" << info.loc.x
                << " y =" << info.loc.y
                << " state =" << info.state << std::endl;
        }

        closesocket(client_sock);
    }

    closesocket(server_sock);
    WSACleanup();
    return 0;
}
