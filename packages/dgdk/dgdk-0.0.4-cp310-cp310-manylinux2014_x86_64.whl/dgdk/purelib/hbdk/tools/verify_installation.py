r"""
Verify that HBDK has been correctly installed
"""
import sys
import subprocess

hbdk_executables = ['hbdk-cc', 'hbdk-disas', 'hbdk-gen-license', 'hbdk-hbm-attach', 'hbdk-layout-convert', 'hbdk-model-check', 'hbdk-pack', 'hbdk-perf', 'hbdk-resize', 'hbdk-sim', 'hbdk-config', 'hbdk-pred']


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == '--help':
        print("==== Check if hbdk installation succeeds")
        sys.exit(0)

    print("==== Checking if hbdk installation succeeds")
    for exe in hbdk_executables:
        args = [exe, '--help']
        print("==== Check if %s is installed, running %s" % (exe, str(args)))
        try:
            p = subprocess.Popen(args, stdout=subprocess.PIPE)
            try:
                p.communicate(60)
            except subprocess.TimeoutExpired:
                p.kill()
                print("**** Timeout expires while calling %s. HBDK is not correctly installed" % str(args), file=sys.stderr)
                sys.exit(1)
        except (subprocess.SubprocessError, OSError):
            print("**** Fail to call %s. HBDK is not correctly installed" % str(args), file=sys.stderr)
            sys.exit(1)
        if p.returncode != 0:
            print("**** %s returns non-zero exitcode %d. HBDK is not correctly installed" % (str(args), p.returncode),
                  file=sys.stderr)
            sys.exit(1)

        print("==== %s has been correctly installed" % exe)

    print("==== All HBDK installation checks done. HBDK has been correctly installed")
    sys.exit(0)


if __name__ == '__main__':
    main()
