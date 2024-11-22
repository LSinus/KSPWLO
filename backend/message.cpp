#include "message.hpp"
#include <sstream>

std::istringstream message::read() const {
    const std::string body_string(body.data.begin(), body.data.end());
    std::istringstream stream(body_string);
    return stream;
}