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
            std::cerr << "Unknown algorithm '" << name << "'. Exiting...\n";
            std::exit(1);
        }
    }

    void get_alternative_routes(std::string_view alg, Graph const &G, Vertex s,Vertex t, int k, double theta, std::vector<arlib::Path<Graph>> &result)
    {
        auto predecessors = arlib::multi_predecessor_map<Vertex>{};
        auto weight = boost::get(boost::edge_weight, G); // Get Edge WeightMap
        run_alt_routing(alg, G, weight, predecessors, s, t, k, theta);
        result = arlib::to_paths(G, predecessors, weight, s, t);
    }

    void print_path(arlib::Path<Graph> const &path) {
        using namespace boost;
        
        for (auto [v_it, v_end] = vertices(path); v_it != v_end; ++v_it) {
            for (auto [e_it, e_end] = out_edges(*v_it, path); e_it != e_end; ++e_it) {
            std::cout << source(*e_it, path) << " -- "
                        << target(*e_it, path) << "\n";
            }
        }
        std::cout << path.length() << '\n';
    }

    /* Custom Depth First Visitor for the graph used to store osmid of each discovered vertex in the solution,
     * this is important in order to show the result on a map in the frontend layer, because thanks to the
     * osmid is it possible to find the univocal position on the map */
    template <typename Graph>
    class DFSVisitor : public boost::default_dfs_visitor {
    public:
        DFSVisitor(std::ostringstream* vertex_results) : m_vertex_results{vertex_results} {};
    private: 
        std::ostringstream* m_vertex_results;
    public:
        void discover_vertex(typename boost::graph_traits<Graph>::vertex_descriptor v, const Graph& g) {
            auto osmid_map = get(boost::vertex_name, g);
            (*m_vertex_results) << osmid_map[v] << ",";
        }

    };

    std::string get_osmid_path(arlib::Path<Graph> const &path, Vertex source) {
        using namespace boost;

        std::ostringstream results;
        DFSVisitor<arlib::Path<Graph>> vis(&results);
        depth_first_search(path, visitor(vis).root_vertex(source));
        
        std::string res = results.str();
        res.pop_back();
        return res;
    }


    Vertex find_vertex_by_osmid(const Graph& g, unsigned long target_osmid) {
        auto osmid_map = get(boost::vertex_name, g);
        for (auto v : boost::make_iterator_range(boost::vertices(g))) {
            if (osmid_map[v] == target_osmid) {
                return v;
            }
        }
        return boost::graph_traits<Graph>::null_vertex();
    }
}