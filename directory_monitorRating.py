import sys
import os
import time
import RatingCalculator


# monitors a directory for new files and calls the results parser if they're json
def main(argv):
    path_to_watch = argv[0]
    before = dict([(f, None) for f in os.listdir(path_to_watch)])
    while 1:
        time.sleep(10)
        after = dict([(f, None) for f in os.listdir(path_to_watch)])
        added = [f for f in after if f not in before]
        if added:
            for new_file in added:
                if new_file.endswith('.json'):
                    print("parsing: " + new_file)
                    arguments = [str(path_to_watch) + '\\' + str(new_file)]
                    RatingCalculator.main(arguments)
        before = after


if __name__ == '__main__':
    main(sys.argv[1:])
