#ifndef MESSAGE_H
#define MESSAGE_H

#include <vector>
#include <cstdint>
#include <sstream>

////////////// message structure definition //////////////////
/*
The message is composed of a header of fixed size and a body.
The header contains an uint32_t variable called size that is
the full size of the message (header + body). body dimension
is calculated with this parameter before message reception.
In fact every communication must start with a header transmission
or reception and then after response the body is transmitted
*/

/*
First of all the client sends to the server graphml data
of the graph in which the algorithms have to be run on and
source and destination vertex of the graph, the header contains
the message size and the NetworkProvider m_bodyBuffer is resized 
based on the header data. after that the message is decoded and
the graph is built.
*/

/*
The server sends back to the client data after processing
with all results encoded in graphml data, every result is encoded
in graphml and a size parameter is placed at the beginning so the
body structure of the message will be --size1-graphml1--size2-graphml2--...
*/


struct message{
    struct header{
        uint32_t size;
    } header{};
    struct body
    {
       std::vector<char> data;
    } body;

    [[nodiscard]] std::istringstream read() const;
};

#endif