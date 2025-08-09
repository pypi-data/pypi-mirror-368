import sys

from robot_core.flow_executor import main

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("参数错误", file=sys.stderr)
    else:
        main(sys.argv[1])
