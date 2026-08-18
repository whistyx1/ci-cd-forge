import sys
from detect.stack_detector  import detect_stack

if __name__ == "__main__":
    try:
        detect_stack(sys.argv[1])
    except IndexError:
        print("You entered an invalid path. Please provide a valid directory path as an argument.")