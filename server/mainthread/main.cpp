#include "main.h"

int main()
{
    WSADATA wsa;

    // 윈속 초기화
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0)
    {
        err_quit("WSAStartup()");
    }

    while (1) {
        game_roop();
    }
    
    WSACleanup();
    return 0;
}

void game_roop()
{
    std::print("[SERVER] CREATE NEW GAME\n");

    SOCKET server_sock;
    struct sockaddr_in server_addr;

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

    std::cout << "[NETWORK] Server listen...\n";


    main_game = std::make_unique<game_manager>();
    start_event = CreateEvent(NULL, TRUE, FALSE, NULL);

    // 인원 모으기
    //while (current_player_count < 1) // 테스트용
    while (current_player_count < PLAYER_COUNT)
    {

        sockaddr_in client_addr{};
        int client_size = sizeof(client_addr);

        SOCKET client_sock = accept(server_sock, (sockaddr*)&client_addr, &client_size);
        if (INVALID_SOCKET == client_sock)
        {
            err_display("accept()");
            continue;
        }

        std::cout << "[NETWORK] Client Accept : " << inet_ntoa(client_addr.sin_addr) << std::endl;

        // 스레드 생성 후 스레드 내에서 복사 후 해제 or 스레드 생성 실패 시 바로 해제
        player_info* info = new player_info{ .sock = client_sock , .id = current_player_count };

        if (main_game) { main_game->add_player(*info); }

        // ---- Server_recv_thread 생성 ----
        HANDLE hThread = CreateThread(NULL, 0, recv_thread, (LPVOID)(info), 0, NULL);

        if (NULL == hThread)
        {
            delete info;                    // 스레드 생성 실패 시 바로 해제
            err_display("CreateThread()");
            closesocket(client_sock);
            continue;
        }
        else {
            current_player_count++;
        }

        CloseHandle(hThread);
    }
    closesocket(server_sock);

    main_game->start_game();

    // 게임루프
    while (1)
    {
        main_game->dispatch();
        main_game->update();
        main_game->handle_collision();
        main_game->broadcast();
        

        // 게임 종료 조건 체크 
        if (main_game->end_game())
        {
            // 루프 종료
            current_player_count = 0;
            break;
        }
    }
}
