from studio.app.optinist.dataclass.fluo import FluoData


def fluo_from_hdf5(
    fluo: FluoData, output_dir: str, params: dict = None, **kwargs
) -> dict(fluorescence=FluoData):
    if params["transpose"]:
        import numpy as np

        return {
            "fluorescence": FluoData(np.transpose(fluo.data), file_name="fluorescence"),
        }
    else:
        return {
            "fluorescence": FluoData(fluo.data, file_name="fluorescence"),
        }
