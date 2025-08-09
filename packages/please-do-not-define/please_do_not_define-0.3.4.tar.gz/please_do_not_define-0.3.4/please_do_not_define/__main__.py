from please_do_not_define.all_name import get_name_usages_with_location
from please_do_not_define.invalid_name import _is_illegal_name as is_illegal_name
from please_do_not_define.__version__ import __version__
import sys
import os


def analyse_code(code):
    all_name = get_name_usages_with_location(code)
    illegal_name_dict = {}
    for key, value in all_name.items():
        if is_illegal_name(key):
            illegal_name_dict[key] = value
    return illegal_name_dict


def main():
    args = sys.argv[1:]

    if not args or (len(args) == 1 and args[0] == '-h'):
        sys.stderr.write(
            '''Usage:
    checkname filename      : analyse the name in the python code file
    checkname -s code       : analyse the name in the code string
    checkname -h            : for help
    checkname -v            : show the version\n''')
        return

    if len(args) == 1 and args[0] == '-v':
        print("version:", __version__)
        return

    if len(args) == 1 and args[0] not in ("-h", "-v", "-s"):
        filename = args[0]
        try:
            with open(filename, encoding='utf-8') as f:
                illegal_name_dict = analyse_code(f.read())
            if not illegal_name_dict:
                print("no illegal name")
            else:
                print("found the illegal name below:", end="\n\n", file=sys.stderr)
                for key, value in illegal_name_dict.items():
                    print("name", key, "at",
                          os.path.abspath(filename), "line",
                          value[0], "offset", value[1], file=sys.stderr)
                print("please don't try to define a female", file=sys.stderr)
        except Exception as e:
            sys.stderr.write(
                f"""cannot analyse file {filename}: {str(e)}
please ensure:
    1 the file exists and is encoded with "utf-8"
    2 the file is a python code\n""")
        return

    if len(args) >= 2 and args[0] == "-s":
        try:
            illegal_name_dict = analyse_code(" ".join(args[1:]))
            if not illegal_name_dict:
                print("no illegal name")
            else:
                print("found the illegal name below:", end="\n\n", file=sys.stderr)
                for key, value in illegal_name_dict.items():
                    print("name", key, "at",
                          "input", "line",
                          value[0], "offset", value[1], file=sys.stderr)
                print("please don't try to define a female", file=sys.stderr)
        except Exception as e:
            sys.stderr.write(f"""code wrong: {str(e)}\n""")
        return

    sys.stderr.write(
        f"""Unknown command: {" ".join(sys.argv)}
Use checkname -h for help.\n""")


if __name__ == "__main__":
    main()
