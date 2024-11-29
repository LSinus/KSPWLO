#include "engine.hpp"
#include <iostream>
#include <boost/graph/graphml.hpp>

Engine::Engine(const int port)
: m_netProvider(NetworkProvider(port)), m_source(0), m_dest(0), port_(port) {
    m_results << "alg,s,t,k,theta,time\n";
}

void Engine::loop()
{
    m_netProvider.connect();
    try {
        while(true){
            message msg = m_netProvider.receive();
            buildGraph(msg);
            runAlg();
        }
    }catch (std::exception& e) {
        std::cerr << "Connessione terminata dal client: " << e.what() << std::endl;
        m_netProvider.disconnect();
        saveProfilingResults();
    } 
}


void Engine::buildGraph(message& msg)
{   
    std::istringstream graphStream = msg.read();

    std::array<uint8_t, 4> tmp_source{}, tmp_dest{}, tmp_k{}, tmp_theta{};

    if (!graphStream) {
        throw std::runtime_error("Errore nella lettura dei dati m_dest, m_source, m_k, m_theta.");
    }

    graphStream.read(reinterpret_cast<char*>(&tmp_source), sizeof(tmp_source));
    graphStream.read(reinterpret_cast<char*>(&tmp_dest), sizeof(tmp_dest));
    graphStream.read(reinterpret_cast<char*>(&tmp_theta), sizeof(tmp_theta));
    graphStream.read(reinterpret_cast<char*>(&tmp_k), sizeof(tmp_k));

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

    m_k = 
            (tmp_k[0] << 24) | 
            (tmp_k[1] << 16) | 
            (tmp_k[2] << 8) | 
             tmp_k[3]; 
    
    float tmp_float;
    std::reverse(tmp_theta.begin(), tmp_theta.end());
    std::memcpy(&tmp_float, tmp_theta.data(), sizeof(tmp_float));
    m_theta = tmp_float;

    std::cout << "source " << m_source << ", dest " << m_dest << ", k " << m_k << ", theta " << m_theta << std::endl;

    if(msg.size() > 20) {
        std::cout << "costruzione grafo\n";
        boost::dynamic_properties dp(boost::ignore_other_properties);
        dp.property("osmid", boost::get(boost::vertex_name, m_graph));
        dp.property("length", boost::get(boost::edge_weight, m_graph));
        boost::read_graphml(graphStream, m_graph, dp);

        std::cout << "Numero vertici: " << boost::num_vertices(m_graph) << "\n";
        std::cout << "Numero archi: " << boost::num_edges(m_graph) << "\n";

        // auto osmid_map = boost::get(boost::vertex_name, m_graph);
        // for (const auto& v : boost::make_iterator_range(boost::vertices(m_graph))) {
        //     std::cout << "Nodo: " << v << ", OSMID: " << osmid_map[v] << "\n";
        // }
    }
}

void Engine::saveProfilingResults() {
    std::string data_to_save = m_results.str();
    std::ofstream output_file("output.csv");

    if (output_file.is_open()) {
        output_file << data_to_save;
        output_file.close();
        std::cout << "Dati salvati con successo su output.csv" << std::endl;
    } else {
        std::cerr << "Impossibile aprire il file per la scrittura!" << std::endl;
    }
}

void Engine::saveResults(const std::string& result) {
    std::ofstream output_file("result.txt", std::ios::app);

    if (output_file.is_open()) {
        output_file << result << '\n';
        output_file.close();
    } else {
        std::cerr << "Impossibile aprire il file per la scrittura!" << std::endl;
    }
}

void Engine::runAlg() {
    // auto predecessors = arlib::multi_predecessor_map<Vertex>{};
    // auto weight = boost::get(boost::edge_weight, m_graph);
    // utils::Timer timer;
    std::cout<<"calcolo onepass+\n";
    const auto res_opplus = utils::get_alternative_routes("onepass_plus", m_graph, m_source, m_dest, m_k, static_cast<double>(m_theta), &m_results);
    for (auto const &route : res_opplus) {
        std::cout << "Length: " << route.length() << "\n";
        std::string path = utils::get_osmid_path(route, m_source);
        saveResults(path);
    }

    std::cout<<"calcolo esx\n";
    const auto res_esx = utils::get_alternative_routes("esx", m_graph, m_source, m_dest, m_k, static_cast<double>(m_theta), &m_results);
    for (auto const &route : res_esx) {
        std::cout << "Length: " << route.length() << "\n";
        std::string path = utils::get_osmid_path(route, m_source);
        saveResults(path);
    }

    std::cout<<"calcolo penalty\n";
    const auto res_penalty = utils::get_alternative_routes("penalty", m_graph, m_source, m_dest, m_k, static_cast<double>(m_theta), &m_results);
    for (auto const &route : res_penalty) {
        std::cout << "Length: " << route.length() << "\n";
        std::string path = utils::get_osmid_path(route, m_source);
        saveResults(path);
    }
}

Engine::~Engine(){
    saveProfilingResults();
}