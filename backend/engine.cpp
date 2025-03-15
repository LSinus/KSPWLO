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
            //Clear result file
            std::ofstream output_file("result.txt");
            if (output_file.is_open()) {
                output_file.close();
            }
            message msg = m_netProvider.receive();
            buildGraph(msg);
            runAlg();
            sendResults();
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

    std::array<uint8_t, 8> tmp_source{}, tmp_dest{};
    std::array<uint8_t, 4> tmp_k{}, tmp_theta{};

    if (!graphStream) {
        throw std::runtime_error("Errore nella lettura dei dati m_dest, m_source, m_k, m_theta.");
    }

    // Read the bytes from the stream
    graphStream.read(reinterpret_cast<char*>(tmp_source.data()), sizeof(tmp_source));
    graphStream.read(reinterpret_cast<char*>(tmp_dest.data()), sizeof(tmp_dest));
    graphStream.read(reinterpret_cast<char*>(tmp_theta.data()), sizeof(tmp_theta));
    graphStream.read(reinterpret_cast<char*>(tmp_k.data()), sizeof(tmp_k));

    // Reconstruct the integers in big-endian order
    m_source =
        (static_cast<uint64_t>(tmp_source[0]) << 56) |
        (static_cast<uint64_t>(tmp_source[1]) << 48) |
        (static_cast<uint64_t>(tmp_source[2]) << 40) |
        (static_cast<uint64_t>(tmp_source[3]) << 32) |
        (static_cast<uint64_t>(tmp_source[4]) << 24) |
        (static_cast<uint64_t>(tmp_source[5]) << 16) |
        (static_cast<uint64_t>(tmp_source[6]) << 8) |
        (static_cast<uint64_t>(tmp_source[7]));

    m_dest =
        (static_cast<uint64_t>(tmp_dest[0]) << 56) |
        (static_cast<uint64_t>(tmp_dest[1]) << 48) |
        (static_cast<uint64_t>(tmp_dest[2]) << 40) |
        (static_cast<uint64_t>(tmp_dest[3]) << 32) |
        (static_cast<uint64_t>(tmp_dest[4]) << 24) |
        (static_cast<uint64_t>(tmp_dest[5]) << 16) |
        (static_cast<uint64_t>(tmp_dest[6]) << 8) |
        (static_cast<uint64_t>(tmp_dest[7]));
    m_k = 
        (tmp_k[0] << 24) |
        (tmp_k[1] << 16) |
        (tmp_k[2] << 8)  |
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

void Engine::sendResults() {
    std::ifstream input_file("result.txt", std::ios::binary | std::ios::ate);

    if (!input_file.is_open()) {
        throw std::runtime_error("Could not open file");
    }

    // Get file size
    std::streamsize size = input_file.tellg();
    input_file.seekg(0, std::ios::beg);

    // Create vector and read the data
    std::vector<char> buffer(size);
    if (!input_file.read(buffer.data(), size)) {
        throw std::runtime_error("Could not read file");
    }
    message msg(buffer);
    m_netProvider.send(msg);
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

void Engine::get_alternative_routes(std::string_view alg, Graph const &G, Vertex s,Vertex t, int k, double theta)
{
    auto predecessors = arlib::multi_predecessor_map<Vertex>{};
    auto weight = boost::get(boost::edge_weight, G); // Get Edge WeightMap
    utils::run_alt_routing(alg, G, weight, predecessors, s, t, k, theta);
    auto result = arlib::to_paths(G, predecessors, weight, s, t);

    size_t count = 0;

    for (auto const &route : result) {
        std::cout << "[INFO]: " << std::string(alg)+ ", " + std::to_string(count) + ", Length: " << route.length() << "\n";
        std::string path = std::string(alg)+ "," + std::to_string(count) + "," + utils::get_osmid_path(route, s);
        message msg(std::vector<char>(path.begin(), path.end()));

        m_resultsMutex.lock();
        m_netProvider.send(msg);
        m_resultsMutex.unlock();

        ++count;
    }

}

void Engine::runAlg() {
    // auto predecessors = arlib::multi_predecessor_map<Vertex>{};
    // auto weight = boost::get(boost::edge_weight, m_graph);
    // utils::Timer timer;

    Vertex source = utils::find_vertex_by_osmid(m_graph, m_source);
    Vertex dest = utils::find_vertex_by_osmid(m_graph, m_dest);

    if (source != -1 && dest != -1) {
        //get_alternative_routes("onepass_plus", m_graph, source, dest, m_k, m_theta);

        std::thread thread_opp([this, source, dest]() { this->get_alternative_routes("onepass_plus", m_graph, source, dest, m_k, m_theta);});
        std::thread thread_esx([this, source, dest]() { this->get_alternative_routes("esx", m_graph, source, dest, m_k, m_theta);});
        std::thread thread_penalty([this, source, dest]() { this->get_alternative_routes("penalty", m_graph, source, dest, m_k, m_theta);});

        thread_opp.join();
        thread_esx.join();
        thread_penalty.join();

        std::string done = "COMPUNTATION_DONE";
        message msg(std::vector<char>(done.begin(), done.end()));
        m_netProvider.send(msg);

        std::cout << "[INFO]:COMPUTATION DONE\n" << std::endl;
    }
    else {
        std::cout<<"INVALID OSMID ABORT...\n";
    }
}

Engine::~Engine(){
    saveProfilingResults();
}