#include "engine.hpp"
#include <iostream>
#include <boost/graph/graphml.hpp>

Engine::Engine(const int port)
: m_netProvider(NetworkProvider(port)), m_source(0), m_dest(0), port_(port) {}

void Engine::loop()
{
    m_netProvider.connect();
    try {
        while(true){
            message msg = m_netProvider.receive();
            auto graphStream = msg.read();
            buildGraph(graphStream);
            runAlg();
        }
    }catch (std::exception& e) {
        std::cerr << "Connessione terminata dal client: " << e.what() << std::endl;
        m_netProvider.disconnect();
    } 
}


void Engine::buildGraph(std::istream& graphStream)
{   

    // Legge i primi 4 byte come uint32_t e assegnali a m_dest
    std::array<uint8_t, 4> tmp_source{}, tmp_dest{};
    graphStream.read(reinterpret_cast<char*>(&tmp_source), sizeof(tmp_source));

    // Legge i successivi 4 byte come uint32_t e assegnali a m_source
    graphStream.read(reinterpret_cast<char*>(&tmp_dest), sizeof(tmp_dest));

    m_source = 
            (tmp_source[0] << 24) | 
            (tmp_source[1] << 16) | 
            (tmp_source[2] << 8) | 
             tmp_source[3];

    m_dest = 
            (tmp_dest[0] << 24) | 
            (tmp_dest[1] << 16) | 
            (tmp_dest[2] << 8) | 
             tmp_dest[3];

    if (!graphStream) {
        throw std::runtime_error("Errore nella lettura dei dati m_dest e m_source.");
    }

    std::cout << "source " << m_source << ", dest " << m_dest << std::endl;

    boost::dynamic_properties dp(boost::ignore_other_properties);
    dp.property("length", boost::get(boost::edge_weight, m_graph));
    boost::read_graphml(graphStream, m_graph, dp);
}

void Engine::runAlg() const {
    const auto res_opplus = utils::get_alternative_routes("onepass_plus", m_graph, m_source, m_dest);

    std::cout << "OnePass+ solutions...\n";
    for (auto const &route : res_opplus) {
        utils::print_path(route);
        std::cout << "--------\n";
    }

    

}
