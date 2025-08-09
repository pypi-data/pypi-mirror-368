import json
import sys

from robot_core.parse_function_definitions import parse_function_definitions

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("请输入源文件路径")
        exit(1)
    result = parse_function_definitions(sys.argv[1])
    print(json.dumps(result))
