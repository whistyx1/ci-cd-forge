import sys
import json
from detect.language_detector  import detect_language
from detect.framework_detect import detect_framework
from detect.stack import create_stack

if __name__ == "__main__":
    try:
        path = sys.argv[1]
        stack = create_stack(path)
        print(json.dumps(stack, indent=2))
    except IndexError:
        print("You entered an invalid path. Please provide a valid directory path as an argument.")