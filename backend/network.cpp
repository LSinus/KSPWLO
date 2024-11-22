#include "network.hpp"
#include <iostream>


NetworkProvider::NetworkProvider(const int port) : m_headerBuffer(),
                                                   m_endpoint(boost::asio::ip::tcp::endpoint(
                                                       boost::asio::ip::tcp::v4(), port)),
                                                   m_acceptor(m_io_context, m_endpoint),
                                                   m_socket(m_io_context) {
    std::cout << "Server in ascolto sulla porta " << port << "..." << std::endl;
}

void NetworkProvider::connect()
{
    m_acceptor.accept(m_socket);
    std::cout << "Connessione accettata da: " 
              << m_socket.remote_endpoint().address().to_string() << std::endl;
}


void NetworkProvider::sendData(const std::string& data)
{
    boost::asio::write(m_socket, boost::asio::buffer(data.c_str(), data.length()));
}

auto NetworkProvider::send(const message& message) -> void {
    //boost::asio::write(m_socket, boost::asio::buffer(data.c_str(), data.length()));
}

void NetworkProvider::receiveHeader()
{
    m_socket.wait(m_socket.wait_read);
    auto bytes = m_socket.available();

    if(bytes == 4){
        m_socket.read_some(boost::asio::buffer(m_headerBuffer));
        int32_t size = 
            (m_headerBuffer[0] << 24) | 
            (m_headerBuffer[1] << 16) | 
            (m_headerBuffer[2] << 8) | 
             m_headerBuffer[3];

        m_bodyBuffer.resize(size-4);

        std::cout << m_bodyBuffer.size() << std::endl;
        std::string response = "ok";
        sendData(response);
        std::cout << "Header ricevuto, in attesa di un grafo di dimensione " << size-4 << std::endl;
    }
    else{
        std::string response = "Error: invalid header";
        sendData(response);
    }

}

void NetworkProvider::receiveBody()
{   
    m_socket.wait(m_socket.wait_read);
    size_t len = boost::asio::read(m_socket, boost::asio::buffer(m_bodyBuffer));
    if(len == m_bodyBuffer.size()){
        std::string response = "ok";
        sendData(response);
        std::cout << "Grafo ricevuto" << std::endl;
    }
    else
        std::cout << "Errore nella ricezione del grafo" << std::endl;
}

message NetworkProvider::buildMessage() const {
    message msg;
    msg.header.size = m_bodyBuffer.size() + 4;
    msg.body.data = m_bodyBuffer;

    return msg;
}


message NetworkProvider::receive()
{   
    NetworkProvider::receiveHeader();
    NetworkProvider::receiveBody();
    return NetworkProvider::buildMessage();
}



void NetworkProvider::disconnect()
{
    m_socket.close();
}
