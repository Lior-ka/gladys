/*
 * region_graph.cpp
 *
 * Tool for Graph Library for Autonomous and Dynamic Systems
 *
 * author:  Pierrick Koch <pierrick.koch@laas.fr>
 * created: 2013-07-02
 * license: BSD
 */
#include <ostream> // standard C error stream
#include <cstdlib> // exit status

#include "gladys/weight_map.hpp"
#include "gladys/nav_graph.hpp"

int main(int argc, char * argv[])
{
    if (argc < 4) {
        std::cerr<<"usage: region_graph region.tif robot.json graph.dot"<<std::endl;
        return EXIT_FAILURE;
    }
    gladys::weight_map wm(argv[1], argv[2]);
    gladys::nav_graph ng(wm);
    ng.write_graphviz( argv[3] );
    return EXIT_SUCCESS;
}
