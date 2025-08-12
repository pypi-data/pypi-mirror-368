from studio.app.common.core.experiment.experiment import ExptOutputPathIds
from studio.app.common.core.logger import AppLogger
from studio.app.common.dataclass import ScatterData
from studio.app.optinist.core.nwb.nwb import NWBDATASET
from studio.app.optinist.dataclass import FluoData, IscellData
from studio.app.optinist.wrappers.optinist.utils import standard_norm

logger = AppLogger.get_logger()


def TSNE(
    neural_data: FluoData,
    output_dir: str,
    iscell: IscellData = None,
    params: dict = None,
    **kwargs,
) -> dict():
    import numpy as np
    from sklearn.manifold import TSNE

    function_id = ExptOutputPathIds(output_dir).function_id
    logger.info("start TSNE: %s", function_id)

    neural_data = neural_data.data
    IOparams = params["I/O"]

    # data should be time x component matrix
    if IOparams["transpose"]:
        X = neural_data.transpose()
    else:
        X = neural_data

    if iscell is not None:
        iscell = iscell.data
        ind = np.where(iscell > 0)[0]
        X = X[:, ind]

    # preprocessing
    tX = standard_norm(X, IOparams["standard_mean"], IOparams["standard_std"])

    # calculate TSNE
    tsne = TSNE(**params["TSNE"])

    proj_X = tsne.fit_transform(tX)

    # NWB追加
    nwbfile = {}
    nwbfile[NWBDATASET.POSTPROCESS] = {function_id: {"projectedNd": proj_X}}

    info = {
        "projectedNd": ScatterData(proj_X, file_name="projectedNd"),
        "nwbfile": nwbfile,
    }

    return info
