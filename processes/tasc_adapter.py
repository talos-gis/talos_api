from typing import Dict, Any

from gdalos.viewshed.viewshed_params import atmospheric_refraction_coeff, rf_refraction_coeff

from shapely.geometry import Polygon, mapping

# workaround ValueError: GEOSGeom_createLineString_r returned a NULL pointer
# https://stackoverflow.com/questions/62075847/using-qgis-and-shaply-error-geosgeom-createlinearring-r-returned-a-null-pointer
from shapely import speedups
speedups.disable()


def aoi_to_shapely(in_poly: list) -> Polygon:
    if in_poly[0] != in_poly[len(in_poly) - 1]:
        in_poly.append(in_poly[0])
    poly = Polygon([[p['lon'], p['lat']] for p in in_poly])
    return poly


def shapely_to_geojson(poly):
    return None if poly is None else \
        {"type": "complex", "mimeType": 'application/geo+json', "data": mapping(poly)}


def aoi_to_geojson(inputs: Dict[str, Any], name: str = 'aoi'):
    aoi = inputs.get(name, None)
    if not aoi:
        return None
    poly = aoi_to_shapely(aoi)
    return shapely_to_geojson(poly)


def get_tasc_refraction(inputs: Dict[str, Any], name: str = 'isuserefraction'):
    is_refraction = inputs.get(name, False)
    return atmospheric_refraction_coeff if not is_refraction else rf_refraction_coeff


def get_raster_names(inputs):
    names = ["heights", "ranges", "azangles", "elangles"]
    prefixes = ['', 'return', 'isreturn']
    result = ['v'] + [k for k in names if any([inputs.get(p + k) for p in prefixes])]
    return result


def handle_aoi(inputs):
    aoi = inputs.get('aoi', None)

    # once there were two way to set the extent of the output raster:
    # 1. "LimitToAOI" - meaning clip to the extent of the AOI (cutline)
    # 2. "CenterGeoRaster" - meaning take the position in pixels of the observer
    # in the output raster and set the extent around it so it will be EXACTLY in
    # in the middle of the output raster.
    if aoi:
        aoi = aoi_to_shapely(aoi)
        inputs['cutline'] = shapely_to_geojson(aoi)
        clip_extent_to_aoi = inputs.get('limittoaoi', True)
        if not clip_extent_to_aoi:
            minx, miny, maxx, maxy = aoi.bounds
            inputs['extent']: {
                "type": "bbox",
                "bbox": [miny, minx, maxy, maxx]
            }
    if inputs.get('centergeoraster'):
        raise Exception('Sorry, CenterGeoRaster is not supported.')
