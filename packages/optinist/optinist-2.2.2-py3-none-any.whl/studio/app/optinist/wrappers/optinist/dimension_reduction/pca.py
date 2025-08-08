from studio.app.common.core.experiment.experiment import ExptOutputPathIds
from studio.app.common.core.logger import AppLogger
from studio.app.common.dataclass import BarData, ScatterData
from studio.app.optinist.core.nwb.nwb import NWBDATASET
from studio.app.optinist.dataclass import FluoData, IscellData
from studio.app.optinist.wrappers.optinist.utils import standard_norm

logger = AppLogger.get_logger()


def PCA(
    neural_data: FluoData,
    output_dir: str,
    iscell: IscellData = None,
    params: dict = None,
    **kwargs,
) -> dict():
    # modules specific to function
    import numpy as np
    from sklearn.decomposition import PCA

    function_id = ExptOutputPathIds(output_dir).function_id
    logger.info("start PCA: %s", function_id)

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

    # # preprocessing
    tX = standard_norm(X, IOparams["standard_mean"], IOparams["standard_std"])

    # calculate PCA
    pca = PCA(**params["PCA"])
    proj_X = pca.fit_transform(tX)

    # NWB追加
    nwbfile = {}
    nwbfile[NWBDATASET.POSTPROCESS] = {
        function_id: {
            "pca_projectedNd": proj_X,
            "components": pca.components_,
            "explained_variance": pca.explained_variance_,
            "explained_variance_ratio": pca.explained_variance_ratio_,
            "singular_values": pca.singular_values_,
            "mean": pca.mean_,
            "n_components": [pca.n_components_],
            "n_samples": [pca.n_samples_],
            "noise_variance": [pca.noise_variance_],
            "n_features_in": [pca.n_features_in_],
        }
    }

    # import pdb; pdb.set_trace()
    info = {
        "explained_variance": BarData(pca.explained_variance_ratio_, file_name="evr"),
        "projectedNd": ScatterData(proj_X, file_name="projectedNd"),
        "contribution": BarData(
            pca.components_,
            index=[f"pca: {i}" for i in range(len(pca.components_))],
            file_name="contribution",
        ),
        "cumsum_contribution": BarData(
            np.cumsum(pca.components_, axis=0),
            index=[f"pca: {i}" for i in range(len(pca.components_))],
            file_name="cumsum_contribution",
        ),
        "nwbfile": nwbfile,
    }

    return info
