from copy import deepcopy
from numpy import arange, asarray, diff, isnan, mean, median, nanmax, nanmin, ndim, r_, std, zeros, nan, min,max
from numpy import any as npany
from numpy import dtype as npdtype
from xarray import DataArray as xr_DataArray
from xarray import register_dataarray_accessor
from ..metadata.Metadata import Metadata

default_metadata = ('standard_name', 'long_name', 'null_value', 'units')

@register_dataarray_accessor("gs")
class DataArray:
    """Accessor for xarray.DataArray.

    See Also
    --------
    DataArray.from_values : for instantiation

    """

    def __init__(self, xarray_obj):
        self._obj = xarray_obj


    @classmethod
    def add_bounds_to_coordinate_dimension(cls, coordinate, name, bounds=None, **kwargs):
        """For an existing DataArray, compute its bounds and attach them.

        Automatically modifies any attached metadata keys.

        Parameters
        ----------
        coordinate : xarray.DataArray
            Existing DataArray inside an xarray.Dataset
        name : str
            Used purely for error messages.
        bounds : array_like, optional
            * Has shape (size of dimension, 2) defining the bounds of each "cell" in the coordinate
            * if not present, bounds are computed. Otherwise assign them.

        Returns
        -------
        xarray.DataArray

        """
        # Return if the coordinate already has bounds
        if 'bounds' in coordinate.attrs:
            return

        if bounds is None:
            bounds = zeros((coordinate.size, 2))
            centre = median(diff(coordinate.values)) * 0.5
            bounds[:, 0] = coordinate.values - centre
            bounds[:, 1] = coordinate.values + centre
        else:
            bounds = asarray(bounds)
            centers = coordinate.values
            if bounds.shape == (centers.size+1, ):
                bounds = asarray((bounds[:-1], bounds[1:])).transpose()
            else:
                assert bounds.shape == (centers.size, 2), ValueError('size of coordinate bounds must be 2D array size of centers, or +1 list size of centers that can be reshaped')

        attrs = coordinate.attrs.copy()
        attrs['standard_name'] = coordinate.attrs['standard_name'] + '_bounds'
        attrs['long_name'] = coordinate.attrs['long_name'] + ' cell boundaries'
        attrs['valid_range'] = cls.valid_range(bounds, name, **kwargs)

        self = xr_DataArray(bounds,
                            dims=kwargs.pop('dims', None),
                            coords=kwargs.pop('coords', None),
                            attrs=attrs)

        return self

    @staticmethod
    def check_metadata(name, **kwargs):
        """Check the metadata provided and ensure GS standard compliance, i.e. at least long_name, standard_name, and units.

        Parameters
        ----------
        name : str
            Name of the variable
        long_name : str, optional
            CF convention long name
        null_value : int or float, optional
            Number that represents unusable data. default is 'not_defined'
        standard_name : str, optional
            CF convention standard name
        units : str, optional
            units of the coordinate

        Raises
        ------
        Exception
            If required metadata is missing.

        """
        missing = [x for x in default_metadata if x not in kwargs.keys()]

        assert len(missing) == 0, ValueError(f"Metadata for variable {name} is missing entries {missing}")

    @classmethod
    def from_values(cls, name, **kwargs):
        """Generates an xarray.DataArray using an array of values

        Wraps around the xarray.DataArray instantiator and checks for Nans and adds CF convention metadata entries like valid_range, grid_mapping.

        Parameters
        ----------
        name : str
            Name of the DataArray.
        values : array_like
            Values to assign to the DataArray.

        Other Parameters
        ----------------
        coords : dict, optional
            Dictionary of DataArrays along each dimension of this variable
        dtype : dtype, optional
            Coerce values into this dtype.
        dimensions : list of str
            names of this variables dimesions
        grid_mapping : str, optional
            Name of the grid_mapping. Default is 'spatial_ref' and refers to any attached spatial_ref class, handled by gspy
        long_name : str, optional
            CF convention long name
        null_value : int or float, optional
            Number that represents unusable data. default is 'not_defined'
        standard_name : str, optional
            CF convention standard name
        units : str, optional
            units of the coordinate

        Returns
        -------
        xarray.DataArray

        """
        values = kwargs.pop('values')
        nd = ndim(values)

        if kwargs.pop('check', True):
            cls.check_metadata(name, **kwargs)

            if nd:
                assert "dimensions" in kwargs, ValueError("dimensions must be specified for array_like variables")

        if nd > 0:
            if not isinstance(values[0], str):
                kwargs['valid_range'] = cls.valid_range(values, name=name, **kwargs)

        kwargs['grid_mapping'] = kwargs.pop('grid_mapping', 'spatial_ref')

        if 'dtype' in kwargs:
            values = values.astype(kwargs['dtype'])

        return xr_DataArray(values,
                dims=kwargs.pop('dimensions', None),
                coords=kwargs.pop('coords', None),
                attrs=kwargs)

    @staticmethod
    def catch_nan(values, name, **kwargs):
        """Replace NaNs with the defined null_value in the metadata.

        Parameters
        ----------
        values : array_like
            Values to check
        name : str
            Name of the variable being checked

        Other Parameters
        ----------------
        null_value : str, optional
            Number that represents unusable data. default is 'not_defined'

        Returns
        -------
        array_like

        Raises
        ------
        If there are NaNs in the values, and no defined null_value in the kwargs, notify the user.

        """

        if isinstance(values[0], str):
            return values

        nv = kwargs.get('null_value', 'not_defined')

        if nv == 'not_defined':
            assert not npany(isnan(values)), ValueError((f"\nThere are NaNs or Empty values in data column {name} and no defined null value in the json metadata file.\n"
                                                         f"Define the 'null_value' for {name} in the json file"))
        else:
            values[isnan(values)] = nv
        return values

    @staticmethod
    def valid_range(values, name, **kwargs):
        """Generate a valid range for some values

        Parameters
        ----------
        values : array_like
            numerical array
        name : str
            name of the variable

        Other Parameters
        ----------------
        null_value : scalar, optional
            Representation of unusable data values
        dtype : dtype, optional
            Coerce the min, max to this dtype default is values.dtype.

        Returns
        -------
        array_like
            [nanmin(values), nanmax(values)]
        """

        nv = kwargs.get('null_value', 'not_defined')

        if nv == 'not_defined':
            valid_range = asarray([nanmin(values), nanmax(values)], dtype=kwargs.get('dtype', None))
        else:
            assert not isinstance(nv, str), ValueError(f"Numerical null_value defined as a string in metadata file for variable {kwargs['standard_name']}.\nPlease make it a number. If this number is in scientific notation please use the following format x.xe+10 or x.xe-10.")
            tmp = values[values != nv]
            valid_range = asarray([nanmin(tmp), nanmax(tmp)], dtype=kwargs.get('dtype', None))

        return valid_range

    @property
    def label(self):
        return f'{self._obj.attrs['long_name']} [{self._obj.attrs['units']}]'

    @staticmethod
    def metadata_template(**kwargs):
        return Metadata.merge({key: "not_defined" for key in default_metadata}, kwargs)