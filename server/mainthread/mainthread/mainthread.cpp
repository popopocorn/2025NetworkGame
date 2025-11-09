#include "Common.h"
#include "ConfigLoader.h"


// --------------------------- main부분 ---------------------------------
int main()
{
    WSADATA wsa;
    SOCKET server_sock;
    struct sockaddr_in server_addr;

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
    config_loader config("server.txt");

    server_sock = socket(AF_INET, SOCK_STREAM, 0);
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(config.get_port_number());

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

        std::cout << "Client Accept : " << inet_ntoa(client_addr.sin_addr) << std::endl;

        // 루프 돌면서 클라에서 char_skill_info 받기
        char_skill_info info{};
        while (true)
        {
            
            int ret = recv(client_sock, (char*)&info, sizeof(info), 0);

            if (0 == ret)
            {
                // 클라 연결 종료
                std::cout << "Client Connection lost\n";
                break;
            }
            else if (SOCKET_ERROR == ret)
            {
                // recv 에러 출력
                err_display("recv()");
                break;
            }
            info.ntoh();        // 네트워크 바이트 정렬 -> 호스트 바이트 정렬
            info.print();       // 받은 내용 그대로 출력
        }

        closesocket(client_sock);
    }

    closesocket(server_sock);
    WSACleanup();
    return 0;
}
