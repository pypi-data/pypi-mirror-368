import os
import sys
if __name__ == "__main__":
    if os.getenv("DEV") is not None:
        p=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        sys.path.insert(0, p)
    from py_az_vm_controller_xethhung12._cmd import run
    run.main()