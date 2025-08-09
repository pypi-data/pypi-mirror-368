from horizon_tc_ui.config.config_info import ConfigBase


class VerifierParams(ConfigBase):
    model: str = ""
    board_ip: str = ""
    input: str = ""
    run_sim: bool = False
    dump_all_nodes_results: bool = False
    compare_digits: int = 5
    username: str = "root"
    password: str = ""
