from typing import Dict

from studio.app.common.core.snakemake.smk import Rule
from studio.app.common.core.snakemake.smk_builder import RuleBuilder
from studio.app.common.core.utils.filepath_creater import get_pickle_file
from studio.app.common.core.workflow.workflow import Edge, Node, NodeType
from studio.app.common.core.workflow.workflow_params import get_typecheck_params
from studio.app.const import FILETYPE


class SmkRule:
    RETURN_ARG_KEY_DELIMITER = "@"

    def __init__(
        self,
        workspace_id: str,
        unique_id: str,
        node: Node,
        edgeDict: Dict[str, Edge],
        nwbfile=None,
    ) -> None:
        self._workspace_id = workspace_id
        self._unique_id = unique_id
        self._node = node
        self._edgeDict = edgeDict
        self._nwbfile = nwbfile

        _return_name = self.get_return_name()

        _output_file = get_pickle_file(
            self._workspace_id,
            self._unique_id,
            self._node.id,
            self._node.data.label.split(".")[0],
        )

        self.builder = RuleBuilder()
        (
            self.builder.set_input(
                self._node.data.path, workspace_id=self._workspace_id
            )
            .set_return_arg(_return_name)
            .set_params(self._node.data.param)
            .set_output(_output_file)
            .set_nwbfile(self._nwbfile)
        )

    def image(self) -> Rule:
        return self.builder.set_type(FILETYPE.IMAGE).build()

    def csv(self, nodeType=FILETYPE.CSV) -> Rule:
        return self.builder.set_type(nodeType).build()

    def hdf5(self) -> Rule:
        return (
            self.builder.set_type(FILETYPE.HDF5)
            .set_hdf5Path(self._node.data.hdf5Path)
            .build()
        )

    def mat(self) -> Rule:
        return (
            self.builder.set_type(FILETYPE.MATLAB)
            .set_matPath(self._node.data.matPath)
            .build()
        )

    def microscope(self) -> Rule:
        return self.builder.set_type(FILETYPE.MICROSCOPE).build()

    def algo(self, nodeDict: Dict[str, Node]) -> Rule:
        algo_input = []
        return_arg_names = {}
        for edge in self._edgeDict.values():
            if self._node.id == edge.target:
                arg_name = edge.targetHandle.split("--")[1]

                sourceNode = nodeDict[edge.source]
                if sourceNode.type == NodeType.ALGO:
                    return_name = edge.sourceHandle.split("--")[1]
                    funcname = sourceNode.data.label
                else:
                    return_name = edge.sourceHandle.split("--")[0]
                    funcname = sourceNode.data.label.split(".")[0]

                input_file = get_pickle_file(
                    self._workspace_id, self._unique_id, sourceNode.id, funcname
                )

                if input_file not in algo_input:
                    algo_input.append(input_file)

                return_arg_names[return_name] = arg_name

        params = get_typecheck_params(self._node.data.param, self._node.data.label)
        algo_output = get_pickle_file(
            self._workspace_id, self._unique_id, self._node.id, self._node.data.label
        )

        return (
            self.builder.set_input(algo_input)
            .set_return_arg(return_arg_names)
            .set_params(params)
            .set_output(algo_output)
            .set_path(self._node.data.path)
            .set_type(self._node.data.label)
            .set_nwbfile(self._nwbfile)
            .build()
        )

    def get_return_name(self) -> str or None:
        for edge in self._edgeDict.values():
            if self._node.id == edge.source:
                return edge.sourceHandle.split("--")[0]
        return None
