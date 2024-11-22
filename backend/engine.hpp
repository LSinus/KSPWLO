#ifndef ENGINE_H
#define ENGINE_H

#include "network.hpp"
#include "utils.hpp"
#include <sstream>

class Engine {

public:
    explicit Engine(int port = 10714);
    void loop();
    void end();
private:
    NetworkProvider m_netProvider;
    Graph m_graph;
    Vertex m_source;
    Vertex m_dest;
    int port_;

private:
    void buildGraph(std::istream& graphStream);
    void runAlg() const;
};

#endif