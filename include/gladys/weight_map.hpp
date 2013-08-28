/*
 * weight_map.hpp
 *
 * Graph Library for Autonomous and Dynamic Systems
 *
 * author:  Pierrick Koch <pierrick.koch@laas.fr>
 * created: 2013-06-12
 * license: BSD
 */
#ifndef WEIGHT_MAP_HPP
#define WEIGHT_MAP_HPP

#include <cmath>    // for HUGE_VALF
#include <string>

#include "gladys/gdal.hpp"
#include "gladys/robot_model.hpp"

namespace gladys {

/*
 * from terrains model (in multi-layers GeoTiff)
 * to single layers weight map (after inflating obstacles by robot size)
 */
class weight_map {
    gdal terrains; // probalistic models (multi-layers GeoTiff)
    gdal map; // weight map (after inflating robot size)
    robot_model rmdl;
    enum {W_FLAG_OBSTACLE=-2, W_UNKNOWN=-1};
public:
    /* Names of the visual terrain classes */
    enum {NO_3D_CLASS, FLAT, OBSTACLE, ROUGH, SLOPE, N_RASTER};

    /** load region and robot model
     *
     * @param f_region path to a region.tif file
     * (multi-layers terrains classification probabilities, float32)
     *
     * @param f_robot_model TODO path to a robot model
     * to generate the weight map (at least its size)
     *
     */
    void load(const std::string& f_region, const std::string& f_robot_model) {
        terrains.load(f_region);
        rmdl.load(f_robot_model);
        _load();
    }
    void _load();

    void flag_as_obstacle(float& weight) {
        if (!is_obstacle(weight))
            weight = W_FLAG_OBSTACLE;
    }
    bool is_flag_obstacle(float weight) const {
        return weight == W_FLAG_OBSTACLE;
    }
    bool is_obstacle(float weight) const {
        return weight == HUGE_VALF;
    }

    /** compute a mix of ponderated classes
     *
     * w/ threshold on obstacle
     * @returns weight in [1, 100] or -1 if unknown
     *
     */
    float compute_weight(const gdal::raster& data) {
        if (data[NO_3D_CLASS] > 0.9)
            return W_UNKNOWN; // UNKNOWN
        if (data[OBSTACLE] > 0.4) // TODO tune this threshold
            return HUGE_VALF; // OBSTACLE
        else // compute a mix of ponderated classes TODO dynamicaly json conf
            return 1 + 98 * (data[FLAT] * 0.1 + data[ROUGH] * 0.3 + data[SLOPE] * 0.6 );
    }

    gdal::raster get_weight_band() {
        return map.bands[0];
    }
    gdal get_map() {
        return map;
    }
    gdal get_region() {
        return terrains;
    }

    size_t get_width() {
        return map.get_width();
    }

    size_t get_height() {
        return map.get_height();
    }

    double get_scale_x() {
        return map.get_scale_x();
    }

    double get_scale_y() {
        return map.get_scale_y();
    }

    double get_utm_pose_x() {
        return map.get_utm_pose_x();
    }

    double get_utm_pose_y() {
        return map.get_utm_pose_y();
    }

    void save(const std::string& filepath) {
        map.save(filepath);
    }
};

} // namespace gladys

#endif // WEIGHT_MAP_HPP

