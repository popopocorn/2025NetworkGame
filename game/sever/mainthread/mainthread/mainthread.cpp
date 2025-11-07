#define _WINSOCK_DEPRECATED_NO_WARNINGS
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>

#include <iostream>
#include <mutex>
#include <string>
#include <cstdint> //같은 고정 크기 정수 타입
#include <cstring>

#pragma comment(lib, "ws2_32.lib")

std::mutex g_buffer_guard;         // global mutex buffer_guard
DWORD WINAPI recv_thread(LPVOID arg);   // 서버 recv 스레드

// 최대 플레이어 / 최대 스킬 개수
const int MAX_PLAYER = 3; 
const int MAX_SKILL = 64;

// ---------------- 패킷 정의 ----------------
enum PacketType : uint8_t
{
    PACKET_CHAR_INFO = 1,
    PACKET_SKILL_INFO = 2
};

#pragma pack(push, 1) //패딩없이 1바이트 단위로 정렬함 즉, 사이즈 꼬임 방지 목적, 패킷을 주고 받기위해
struct PacketHeader
{
    uint8_t  type;   // uint8_t : unsigned int 8 type 약자 : 부호없는 8비트 정수 타입 선언
    uint16_t size;
};

struct CharInfo      // 네트워크로 오가는 캐릭터 정보
{
    float x;
    float y;
    char state[4];   // "Idle", "Run"
};

struct SkillInfo     // 네트워크로 오가는 스킬 정보
{
    int   skill_id;
    float x;
    float y;
    char  skill_direction;
    float skill_ad;
};
#pragma pack(pop) //CPU는 보통 4바이트 정렬을 좋아해서 성능을 위해 원래대로 정렬해야 함

// recv는 한 번 호출할 때 요청한 만큼 꼭 다 받는다는 보장을 보완하기 위한 recv_all
int recv_all(SOCKET s, char* buf, int size) 
{
    int received = 0;
    while (received < size)
    {
        int ret = recv(s, buf + received, size - received, 0);
        if (ret <= 0) return ret;      // 에러 or 끊김
        received += ret;
    }
    return received;
}

// ======== 런타임 컨테이너용 struct 정의 ========
//나중에 클라한테 보내고, 클라는 그걸 렌더링 하기 위해
struct PlayerInfoRuntime   
{
    float x{ 0.f }; //C++11에서 처음 생긴 문법, x를 기본값 0.0f로 초기화해 둔다, x = 0.0f랑 같은 의미
    float y{ 0.f };
    float hp{ 0.f };
    std::string state{ "Idle" };   // 내부에서는 string 사용, Idle로 초기화
};

struct SkillInfoRuntime   
{
    int skill_id{ 0 }; // skill_id 그대로 가져옴
    float x{ 0.f };
    float y{ 0.f };
    char  direction{ 0 }; // skill_direction
    float attack_damage{ 0.f }; // skill_ad
};

// ======== GameManager 클래스 ========
class GameManager
{
public:
    GameManager()
        : skill_count(0)
    {
        for (int i = 0; i < MAX_PLAYER; ++i)
            sockets[i] = INVALID_SOCKET;  // 아직 접속 안 한 상태
    }

    void add_player(int pid, SOCKET sock)
    {
        if (pid < 0 || pid >= MAX_PLAYER)
            return;

        sockets[pid] = sock;

        player_infos[pid].x = 0.f;
        player_infos[pid].y = 0.f;
        player_infos[pid].hp = 100.f; 
        player_infos[pid].state = "Idle";
    }

    SOCKET get_player_socket(int pid)
    {
        if (pid < 0 || pid >= MAX_PLAYER)
            return INVALID_SOCKET;
        return sockets[pid];
    }

    // === Player Info Container에 Write ===
    void update_char_info(int pid, const CharInfo& info)
    {
        if (pid < 0 || pid >= MAX_PLAYER)
            return;

        player_infos[pid].x = info.x;
        player_infos[pid].y = info.y;
        player_infos[pid].state = info.state;   // std::string은 char*로부터 복사가 가능해서 그대로 대입 가능
    }

    // === Skill Info Container에 Write ===
    void push_skill_info(int , const SkillInfo& info)
    {
        if (skill_count >= MAX_SKILL)
            return;  // 꽉 찼으면 그냥 버림

        SkillInfoRuntime& s = skill_infos[skill_count++];
        s.skill_id = info.skill_id;
        s.x = info.x;
        s.y = info.y;
        s.direction = info.skill_direction;
        s.attack_damage = info.skill_ad;
    }

    void update() {  }
    void handle_collision() {  }
    void broadcast() {  }

    bool intersects() { return false; }   
    bool end_game() { return false; }   

private:
    PlayerInfoRuntime player_infos[MAX_PLAYER]; // Player Info Container
    SkillInfoRuntime  skill_infos[MAX_SKILL]; // Skill Info Container
    SOCKET sockets[MAX_PLAYER]; // 플레이어 소켓
    int skill_count; // skill_infos에 들어간 개수
};

GameManager g_game_manager;

void start_game() { /* 생략 */ }

// --------------------------- main부분 ---------------------------------
int main()
{
    //윈속 초기화
    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0)
    {
        std::cerr << "WSAStartup failed\n";
        return 1;
    }

    //리슨 소켓 생성
    SOCKET listen_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_sock == INVALID_SOCKET)
    {
        std::cerr << "socket() failed\n";
        WSACleanup();
        return 1;
    }

    //바인드
    sockaddr_in srv_addr{};
    srv_addr.sin_family = AF_INET;
    srv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    srv_addr.sin_port = htons(40000);

    if (bind(listen_sock, (sockaddr*)&srv_addr, sizeof(srv_addr)) == SOCKET_ERROR)
    {
        std::cerr << "bind() failed\n";
        closesocket(listen_sock);
        WSACleanup();
        return 1;
    }

    //리슨
    if (listen(listen_sock, SOMAXCONN) == SOCKET_ERROR)
    {
        std::cerr << "listen() failed\n";
        closesocket(listen_sock);
        WSACleanup();
        return 1;
    }

    std::cout << "Server listening...\n";

    HANDLE hRecvThreads[MAX_PLAYER] = {};
    int playerCount = 1;

    //플레이어 접속 대기 + GameManager에 등록 + recv 스레드 생성
    while (playerCount < MAX_PLAYER)
    {
        sockaddr_in cli_addr{};
        int addrlen = sizeof(cli_addr);

        SOCKET client_sock = accept(listen_sock, (sockaddr*)&cli_addr, &addrlen);
        if (client_sock == INVALID_SOCKET)
        {
            std::cerr << "accept() failed\n";
            continue;
        }

        int playerId = playerCount;
        std::cout << "Client connected, id = " << playerId << "\n";

        {
            std::lock_guard<std::mutex> lg(g_buffer_guard);
            g_game_manager.add_player(playerId, client_sock);
        }

        // recv 스레드에 넘길 인자 (player id)
        int* pId = new int(playerId);
        hRecvThreads[playerCount] =
            CreateThread(nullptr, 0, recv_thread, pId, 0, nullptr);

        ++playerCount;
    }

    start_game();

    // 메인 게임 루프 (Server main thread)
    while (!g_game_manager.end_game())
    {
        {
            std::lock_guard<std::mutex> lg(g_buffer_guard);
            g_game_manager.update();
            g_game_manager.broadcast();
        }
        Sleep(16); // 약 60fps
    }

    // 정리
    WaitForMultipleObjects(playerCount, hRecvThreads, TRUE, INFINITE);
    for (int i = 0; i < playerCount; ++i)
        CloseHandle(hRecvThreads[i]);

    closesocket(listen_sock);
    WSACleanup();
    return 0;
}

// ----------------------- recv_thread ----------------------
DWORD WINAPI recv_thread(LPVOID arg)
{
    int playerId = *static_cast<int*>(arg);
    delete static_cast<int*>(arg);

    SOCKET sock = g_game_manager.get_player_socket(playerId);
    if (sock == INVALID_SOCKET) return 0;

    while (true)
    {
        PacketHeader hdr{};
        int ret = recv_all(sock, reinterpret_cast<char*>(&hdr), sizeof(hdr));
        if (ret <= 0) break; // 에러 or 클라이언트 종료

        if (hdr.type == PACKET_CHAR_INFO && hdr.size == sizeof(CharInfo))
        {
            CharInfo info{};
            ret = recv_all(sock, reinterpret_cast<char*>(&info), sizeof(info));
            if (ret <= 0) break;

            std::lock_guard<std::mutex> lg(g_buffer_guard);
            g_game_manager.update_char_info(playerId, info);

            char state_buf[5] = {};              // 4글자 + '\0'
            std::memcpy(state_buf, info.state, 4);
            state_buf[4] = '\0';

            std::cout << "[server] CharInfo pid=" << playerId
                << " x=" << info.x
                << " y=" << info.y
                << " state=" << state_buf << "\n";
        }
        else if (hdr.type == PACKET_SKILL_INFO && hdr.size == sizeof(SkillInfo))
        {
            SkillInfo info{};
            ret = recv_all(sock, reinterpret_cast<char*>(&info), sizeof(info));
            if (ret <= 0) break;

            std::lock_guard<std::mutex> lg(g_buffer_guard);
            g_game_manager.push_skill_info(playerId, info);

            std::cout << "[server] SkillInfo pid=" << playerId
                << " skill_id=" << info.skill_id
                << " x=" << info.x
                << " y=" << info.y
                << " dir=" << info.skill_direction
                << " ad=" << info.skill_ad << "\n";
        }
        else
        {
            if (hdr.size > 0)
            {
                // vector 대신 new[] 사용
                char* junk = new char[hdr.size];
                ret = recv_all(sock, junk, hdr.size);
                delete[] junk;
                if (ret <= 0) break;
            }
        }
    }

    return 0;
}
