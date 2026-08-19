import sys
from detect.language_detector  import detect_language
from detect.framewrok_detect import detect_framework

if __name__ == "__main__":
    try:
        detect_language(sys.argv[1])
        detect_framework(sys.argv[1], detect_language(sys.argv[1]))
    except IndexError:
        print("You entered an invalid path. Please provide a valid directory path as an argument.")