#pragma once
#include "Common.h"
#include "GameManager.h"

DWORD WINAPI recv_thread(LPVOID arg);

extern std::unique_ptr<game_manager> main_game;
