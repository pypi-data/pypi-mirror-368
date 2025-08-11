from lt_utils.common import *
from lt_utils.file_ops import load_json, save_json, FileScan, load_yaml, save_yaml
from lt_utils.misc_utils import log_traceback, get_current_time
from lt_utils.type_utils import is_pathlike, is_file, is_dir, is_dict, is_str
from lt_tensor.misc_utils import updateDict
from typing import OrderedDict


class ModelConfig(ABC, OrderedDict):
    _forbidden_list: List[str] = ["_forbidden_list"]

    def __init__(
        self,
        **settings,
    ):
        self.set_state_dict(settings)

    def reset_settings(self):
        raise NotImplementedError("Not implemented")

    def post_process(self):
        """Implement the post process, to do a final check to the input data"""
        pass

    def save_config(
        self,
        path: str,
    ):
        assert Path(path).name.endswith(
            (".json", ".yaml", ".yml")
        ), "No valid extension was found in '{path}', It must end with either '.json' or '.yaml' or '.yml'."
        if Path(path).name.endswith(".json") == ".json":
            base = {
                k: v
                for k, v in self.state_dict().items()
                if isinstance(v, (str, int, float, list, tuple, dict, set, bytes))
            }

            save_json(path, base, indent=4)
        else:
            save_yaml(path, self.state_dict())

    def set_value(self, var_name: str, value: str) -> None:
        assert var_name not in self._forbidden_list, "Not allowed!"
        updateDict(self, {var_name: value})
        self.update({var_name: value})

    def get_value(self, var_name: str) -> Any:
        return self.__dict__.get(var_name)

    def set_state_dict(self, new_state: dict[str, str]):
        new_state = {
            k: y for k, y in new_state.items() if k not in self._forbidden_list
        }
        updateDict(self, new_state)
        self.update(**new_state)
        self.post_process()

    def state_dict(self):
        return {k: y for k, y in self.__dict__.items() if k not in self._forbidden_list}

    @classmethod
    def from_dict(cls, dictionary: Dict[str, Any]):
        assert is_dict(dictionary)
        return cls(**dictionary)

    @classmethod
    def from_path(cls, path: PathLike, encoding: Optional[str] = None):
        assert is_file(
            path, extensions=[".json", ".yaml", ".yml"]
        ), "path must point to a valid file!"
        if Path(path).name.endswith(".json"):
            settings = load_json(path, {}, encoding=encoding, errors="ignore")
        else:
            settings = load_yaml(path, {})
        return cls(**settings)
