#pragma once
#include <string>

class config_loader{
private:
	std::string filePath;

public:
	config_loader(std::string_view path) : filePath{ path } {}

	unsigned short get_port_number() const;
};

