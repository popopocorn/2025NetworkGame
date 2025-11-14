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

        std::cout << "Client Accept : "
            << inet_ntoa(client_addr.sin_addr) << std::endl;

        // ---- Server_recv_thread 생성 ----
        HANDLE hThread = CreateThread(NULL, 0, recv_thread, (LPVOID)client_sock, 0, NULL);

        if (hThread == NULL)
        {
            err_display("CreateThread()");
            closesocket(client_sock);
            continue;
        }

        CloseHandle(hThread);
    }

    closesocket(server_sock);
    WSACleanup();
    return 0;
}


