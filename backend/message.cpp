#include "message.hpp"
#include <sstream>

std::istringstream message::read() const {
    const std::string body_string(body.data.begin(), body.data.end());
    std::istringstream stream(body_string);
    return stream;
}

uint32_t message::size() const{
    return header.size;
}

message::message(const std::vector<char>& data) {
    header.size = data.size()+4;
    body.data = data;
}
