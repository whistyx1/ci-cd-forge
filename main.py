import sys
from detect.stack_detector  import detect_stack

if __name__ == "__main__":
    detect_stack(sys.argv[1])