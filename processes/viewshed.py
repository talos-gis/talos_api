import tempfile

import processes.io_generator as iog
from backend.formats import czml_format
from gdalos.gdalos_color import ColorPalette
from gdalos import gdalos_util
from gdalos.rectangle import GeoRectangle
from gdalos.viewshed.radio_params import RadioCalcType
from gdalos.viewshed.viewshed_calc import viewshed_calc, CalcOperation
from gdalos.viewshed.viewshed_params import ViewshedParams
from processes import process_helper
from pywps import FORMATS
from pywps.app import Process
from pywps.app.Common import Metadata
from pywps.response.execute import ExecuteResponse
from .process_defaults import process_defaults


class Viewshed(Process):
    def __init__(self):
        process_id = 'viewshed'
        defaults = process_defaults(process_id)

        inputs = \
            iog.io_crs(defaults) + \
            iog.of_raster(defaults) + \
            iog.raster_input(defaults) + \
            iog.central_meridian_input(defaults) + \
            iog.raster_co(defaults) + \
            iog.raster_ranges(defaults) + \
            iog.observer(defaults, xy=True, z=True, msl=True) + \
            iog.target(defaults, xy=False, z=True, msl=True) + \
            iog.directions(defaults) + \
            iog.apertures(defaults) + \
            iog.viewshed_values(defaults) + \
            iog.slice(defaults) + \
            iog.backend(defaults) + \
            iog.refraction(defaults) + \
            iog.calc_mode(defaults, default=RadioCalcType.FOS.name) + \
            iog.color_palette(defaults) + \
            iog.extent(defaults) + \
            iog.extent_combine(defaults) + \
            iog.operation(defaults) + \
            iog.resolution_output(defaults) + \
            iog.threads(defaults) + \
            iog.radio(defaults) + \
            iog.fake_raster(defaults)

        outputs = iog.output_r() + iog.output_output(is_output_raster=True)

        super().__init__(
            self._handler,
            identifier=process_id,
            version='1.0',
            title='viewshed raster analysis',
            abstract='runs viewshed or radio analysis',
            profile='',
            metadata=[Metadata('raster')],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response: ExecuteResponse):
        of = str(process_helper.get_request_data(request.inputs, 'of')).lower()
        if of == 'tif':
            of = 'gtiff'
        ext = gdalos_util.get_ext_by_of(of)
        is_czml = ext == '.czml'

        extent = process_helper.get_request_data(request.inputs, 'extent')
        if extent is not None:
            # I'm not sure why the extent is in format miny, minx, maxy, maxx
            extent = [float(x) for x in extent]
            extent = GeoRectangle.from_min_max(extent[1], extent[3], extent[0], extent[2])
        else:
            extent = request.inputs['extent_c'][0].data

        cutline = process_helper.get_request_data(request.inputs, 'cutline', True)
        threads = process_helper.get_request_data(request.inputs, 'threads')
        operation, operation_hidendv = process_helper.get_operation(request.inputs)
        color_palette = process_helper.get_request_data(request.inputs, 'color_palette', True)
        if color_palette is None and is_czml:
            raise Exception('color_palette is required for czml output')
        discrete_mode = process_helper.get_request_data(request.inputs, 'discrete_mode')

        output_filename = tempfile.mktemp(suffix=ext)

        co = None
        files = []
        if 'fr' in request.inputs:
            for fr in request.inputs['fr']:
                fr_filename, ds = process_helper.open_ds_from_wps_input(fr)
                if operation:
                    files.append(ds)
                else:
                    output_filename = fr_filename
            bi = vp_arrays_dict = in_coords_srs = out_crs = color_palette = backend = raster_filename = ovr_idx = None

        else:
            in_coords_srs, out_crs = iog.get_io_crs(request.inputs)
            raster_filename, bi, ovr_idx, input_file = iog.get_input_raster(request.inputs, use_data_selector=True)
            backend, vp_arrays_dict = iog.get_vp(request.inputs, ViewshedParams)
            co = iog.get_creation_options(request.inputs)

        vp_slice = process_helper.get_request_data(request.inputs, 'vps')

        viewshed_calc(input_filename=input_file, ovr_idx=ovr_idx, bi=bi, backend=backend,
                      output_filename=output_filename, co=co, of=of,
                      vp_array=vp_arrays_dict, extent=extent, cutline=cutline,
                      operation=operation, operation_hidendv=operation_hidendv,
                      in_coords_srs=in_coords_srs, out_crs=out_crs,
                      color_palette=color_palette, discrete_mode=discrete_mode,
                      files=files, vp_slice=vp_slice, threads=threads)

        response.outputs['r'].data = raster_filename
        response.outputs['output'].output_format = czml_format if is_czml else FORMATS.GEOTIFF
        response.outputs['output'].file = output_filename

        return response
