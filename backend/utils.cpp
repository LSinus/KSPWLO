#include "utils.hpp"
#include <chrono>

namespace utils{

    template <typename WeightMap, typename MultiPredecessorMap>
    void run_alt_routing(std::string_view name, Graph const &G,WeightMap const &weight, MultiPredecessorMap &predecessors,Vertex s, Vertex t, int k, double theta) 
    {
        using arlib::routing_kernels;
        if (name == "onepass_plus") {
            arlib::onepass_plus(G, weight, predecessors, s, t, k, theta);
        } else if (name == "esx") {
            arlib::esx(G, weight, predecessors, s, t, k, theta,
                    routing_kernels::astar);
        } else if (name == "penalty") {
            double p = 0.1, r = 0.1;
            int max_nb_updates = 10, max_nb_steps = 100000;
            arlib::penalty(G, weight, predecessors, s, t, k, theta, p, r,
                        max_nb_updates, max_nb_steps,
                        routing_kernels::bidirectional_dijkstra);
        } else {
            std::cout << "Unknown algorithm '" << name << "'. Exiting...\n";
            std::exit(1);
        }
    }

    std::vector<arlib::Path<Graph>> get_alternative_routes(std::string_view alg,Graph const &G, Vertex s,Vertex t, int k, double theta, std::ostream* results) 
    {
        auto predecessors = arlib::multi_predecessor_map<Vertex>{};
        auto weight = boost::get(boost::edge_weight, G); // Get Edge WeightMap

        (*results) << alg << "," << s << "," << t << "," << k << "," << theta;
        {
            Timer timer(results);
            run_alt_routing(alg, G, weight, predecessors, s, t, k, theta);
        }
        auto alt_routes = arlib::to_paths(G, predecessors, weight, s, t);
        return alt_routes;
    }

    void print_path(arlib::Path<Graph> const &path) {
        using namespace boost;

        for (auto [v_it, v_end] = vertices(path); v_it != v_end; ++v_it) {
            for (auto [e_it, e_end] = out_edges(*v_it, path); e_it != e_end; ++e_it) {
            std::cout << source(*e_it, path) << " -- "
                        << target(*e_it, path) << "\n";
            }
        }
    }
}