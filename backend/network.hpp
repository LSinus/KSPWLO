#ifndef NETWORK_H
#define NETWORK_H

#include <boost/asio.hpp>
#include <fstream>
#include <string>
#include "message.hpp"

class NetworkProvider {

public:
    NetworkProvider(int port);
    ~NetworkProvider();
    void connect();
    void disconnect();
    void send(const message& msg);
    message receive();

private:
    std::array<uint8_t, 4> m_headerBuffer;
    std::vector<char> m_bodyBuffer;
    boost::asio::io_context m_io_context;
    boost::asio::ip::tcp::endpoint m_endpoint;
    boost::asio::ip::tcp::acceptor m_acceptor;
    boost::asio::ip::tcp::socket m_socket;

private:
    void receiveHeader();
    void receiveBody();
    void sendHeader(const message& msg);
    void sendBody(const message& msg);
    message buildMessage() const;
    void sendData(const std::string& data);
};

#endif