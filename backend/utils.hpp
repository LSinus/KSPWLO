#ifndef UTILS_H
#define UTILS_H

#include <iostream>
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/graph_traits.hpp>
#include <boost/graph/graphml.hpp>
#include <boost/graph/graph_utility.hpp>
#include <boost/property_map/function_property_map.hpp>

#include <arlib/esx.hpp>
#include <arlib/graph_utils.hpp>
#include <arlib/multi_predecessor_map.hpp>
#include <arlib/onepass_plus.hpp>
#include <arlib/path.hpp>
#include <arlib/penalty.hpp>
#include <arlib/routing_kernels/types.hpp>


using Graph = boost::adjacency_list<boost::vecS, boost::vecS, boost::bidirectionalS, boost::property<boost::vertex_name_t, size_t>, boost::property<boost::edge_weight_t, double> , boost::no_property>;
using Vertex = typename boost::graph_traits<Graph>::vertex_descriptor;
using Edge = typename boost::graph_traits<Graph>::edge_descriptor;

namespace utils{

    template <typename WeightMap, typename MultiPredecessorMap, typename Engine>
    void run_alt_routing(std::string_view name, Graph const &G,WeightMap const &weight, MultiPredecessorMap &predecessors,Vertex s, Vertex t, int k, double theta, Engine* engine)
    {
        try {
            using arlib::routing_kernels;
            arlib::timer timer(std::chrono::milliseconds(300000));
            if (name == "onepass_plus") {
                arlib::onepass_plus(G, weight, predecessors, s, t, k, theta, engine,  timer);
            } else if (name == "esx") {
                arlib::esx(G, weight, predecessors, s, t, k, theta, engine,
                        routing_kernels::astar, timer);
            } else if (name == "penalty") {
                double p = 0.1, r = 0.1;
                int max_nb_updates = 10, max_nb_steps = 100000;
                arlib::penalty(G, weight, predecessors, s, t, k, theta, p, r,
                            max_nb_updates, max_nb_steps, engine,
                            routing_kernels::bidirectional_dijkstra, timer);
            } else {
                std::cerr << "Unknown algorithm '" << name << "'. Exiting...\n";
                std::exit(1);
            }
        } catch (std::exception &e) {
            std::cerr << "[ERROR]" << e.what() << "\n";
        }
    }

    void print_path(arlib::Path<Graph> const &path);
    std::string get_osmid_path(arlib::Path<Graph> const &path, Vertex source);

    Vertex find_vertex_by_osmid(const Graph& g, unsigned long target_osmid);

    struct Timer {
        std::chrono::time_point<std::chrono::steady_clock> start, end;
        std::chrono::duration<float> duration;
        std::ostream* m_results;

        Timer( std::ostream* results): m_results{results}
        {   
            start = std::chrono::high_resolution_clock::now();
        }

        ~Timer(){
            end = std::chrono::high_resolution_clock::now();
            duration = end - start;
            (*m_results) << "," << duration.count()*1000 << "\n";
        }

    };


}

#endif