#include "Timer.h"
#include <thread>

timer::timer()
{
	timeGetDevCaps(&m_timecaps, sizeof(m_timecaps));
	timeBeginPeriod(m_timecaps.wPeriodMin);
}

timer::~timer()
{
	timeEndPeriod(m_timecaps.wPeriodMin);
}

void timer::restore()
{
	m_prev_time = std::chrono::steady_clock::now();
}

void timer::tick(float max_fps)
{
	std::chrono::steady_clock::time_point now{ std::chrono::steady_clock::now() };

	std::chrono::duration<float> elapsed_duration = now - m_prev_time;
	m_elapsed_time = elapsed_duration.count();



    if (max_fps > 0.0f) {
		std::chrono::nanoseconds target_duration(static_cast<long long>(1.0 / max_fps * 1000000000.0f));
		std::chrono::time_point next = m_prev_time + target_duration;
        if (now < next) { 
			const std::chrono::nanoseconds threshold(2000000);

			if (next - now > threshold) {
				std::this_thread::sleep_until(next - threshold);
			}

			while (std::chrono::steady_clock::now() < next) {
				std::this_thread::yield();
			}

            now = std::chrono::steady_clock::now();
            elapsed_duration = now - m_prev_time;
        }
    }
	m_delta_time = elapsed_duration.count();

	m_prev_time = now;
}
 
float timer::get_elapsed_time() const
{
	return m_elapsed_time;
}

float timer::get_delta_time() const
{
	return m_delta_time;
}

float timer::get_fps() const
{
	if (m_delta_time > 0) {
		return 1.0f / m_delta_time;
	}
	return 0.0f;
}