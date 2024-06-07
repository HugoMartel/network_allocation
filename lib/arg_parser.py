def parse_arguments(options:list[tuple[str,str,type]], argv:list[str], help_header:str) -> dict[str,any]:
    skip_arg:bool = False
    output = {}
    argc = len(argv)

    for i,arg in enumerate(argv[1:]):# We skip the program name in argv
        # Check if we have to skip this arg
        if skip_arg:
            skip_arg = False
            continue

        # Check if the program asked for help
        if arg == "--help":
            print(help_header)
            for option in options:
                print(f"  {option[0]:<30}{option[1]}")
            print("  --help                        Prints this text")
            exit(0)

        not_found:bool = True
        for option in options:
            if arg != option[0]:
                continue
            if option[2] == None:
                output[arg] = True
            else:
                if argc == i+1:
                    print(f"Missing value for argument {options}")
                output[arg] = option[2](argv[i+2])# +2 since we removed the first arg
                skip_arg = True
            not_found = False
            break

        if not_found:
            print(f"Unknown argument {arg}")
            exit(-1)

    return output
