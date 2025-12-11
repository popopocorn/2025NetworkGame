#pragma once
#include "GameManager.h"
#include "ConfigLoader.h"


int current_player_count{};

void game_roop();
std::unique_ptr<game_manager> main_game;