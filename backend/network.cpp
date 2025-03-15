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
    char resbuf[32];

    sendHeader(message);

    // Wait for client response
    m_socket.wait(m_socket.wait_read);
    size_t bytes_read = m_socket.read_some(boost::asio::buffer(resbuf, sizeof(resbuf) - 1));
    resbuf[bytes_read] = '\0';

    if (std::string(resbuf) == "ok") {
        sendBody(message);
        std::cout << "Response body sent\n";
    } else {
        std::cerr << "Invalid response from client: " << resbuf << "\n";
    }
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

        std::string response = "ok";
        sendData(response);
        std::cout << '\n';
        std::cout << "-------------------------------------------------------- " << std::endl;
        std::cout << "Header ricevuto, in attesa di un messaggio di dimensione " << size-4 << std::endl;
        std::cout << "m_bodyBuffer size is: "<< m_bodyBuffer.size() << std::endl;
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

void NetworkProvider::sendHeader(const message &msg) {
    char msg_size[4];
    int size = msg.size();
    std::memcpy(msg_size, &size, 4);
    boost::asio::write(m_socket, boost::asio::buffer(msg_size, 4));
}

void NetworkProvider::sendBody(const message &msg) {
    boost::asio::write(m_socket, boost::asio::buffer(std::string(msg.body.data.data()).c_str(), msg.size()-4));
}

message NetworkProvider::buildMessage() const
{
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

NetworkProvider::~NetworkProvider()
{   
    m_socket.close();
}