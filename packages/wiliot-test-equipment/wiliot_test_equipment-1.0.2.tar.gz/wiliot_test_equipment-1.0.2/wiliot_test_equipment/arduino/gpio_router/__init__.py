from wiliot_test_equipment.utils import parse_h_defines
from pathlib import Path

header_path = Path(__file__).parent / "GPIO_Router.h"
defines_dict = parse_h_defines(header_path)
