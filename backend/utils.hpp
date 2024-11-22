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

using Graph = boost::adjacency_list<boost::vecS, boost::vecS, boost::bidirectionalS, boost::no_property, boost::property<boost::edge_weight_t, double> , boost::no_property>;
using Vertex = typename boost::graph_traits<Graph>::vertex_descriptor;
using Edge = typename boost::graph_traits<Graph>::edge_descriptor;

namespace utils{

    template <typename WeightMap, typename MultiPredecessorMap>
    void run_alt_routing(std::string_view name, Graph const &G,WeightMap const &weight, MultiPredecessorMap &predecessors,Vertex s, Vertex t, int k, double theta);
    
    std::vector<arlib::Path<Graph>> get_alternative_routes(std::string_view alg,Graph const &G, Vertex s,Vertex t);

    void print_path(arlib::Path<Graph> const &path);
}

#endif