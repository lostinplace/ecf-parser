import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

if __name__ == "__main__":

    import ecf_parser

    src_file = sys.argv[2]
    if sys.argv[1] == "json":
        for line in ecf_parser.ecf_file_to_json(src_file):
            print(line)
    elif sys.argv[1] == "ecf":
        for entry in ecf_parser.jsonl_file_to_ecf(src_file):
            print(entry)
