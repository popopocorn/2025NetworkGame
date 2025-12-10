#pragma once
#include "Common.h"
#include <chrono>
#include <windows.h>

class timer
{
private:
	std::chrono::steady_clock::time_point m_prev_time{ std::chrono::steady_clock::now() };
	float m_elapsed_time{};
	float m_delta_time{};
	float m_total_time{};

	TIMECAPS m_timecaps{};
public:
	timer();
	~timer();

	void tick(float max_fps = 0.0f);
	float get_elapsed_time() const;
	float get_delta_time() const;
	float get_fps() const;
	float get_total_time();
	void reset_total_time();
};

