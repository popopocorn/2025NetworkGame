#include "ConfigLoader.h"
#include <fstream>

// 파일 열 수 없을 시 0 리턴
unsigned short config_loader::get_port_number() const
{
    std::ifstream in(filePath);
    if (!in) {
        return 0;           // 파일이 열리지 않을 시.
    }

    std::string line;
    while (std::getline(in, line)) {        // 문장 하나씩 추출
        size_t eq_pos{ line.find('=') };    // '=' 찾음
        if (eq_pos == std::string::npos) { continue; }  // '=' 없을 시 다음 문장으로

        // '=' 앞뒤로 절삭
        std::string key{ line.substr(0,eq_pos) };       
        std::string value{ line.substr(eq_pos + 1) };
        if ("PORT" == key) {
            int n_port;
            try {
                n_port = std::stoi(value);
            }
            catch (...) {
                return 0;   // string -> int 변환 에러 시.
            }

            return static_cast<unsigned short>(n_port);
        }
    }
    return 0;               // 파일 끝까지 찾지 못했을 시.
}
