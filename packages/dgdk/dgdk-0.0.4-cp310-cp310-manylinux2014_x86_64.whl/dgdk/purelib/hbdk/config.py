## -*- coding: utf-8 -*-
## AUTOMATICALLY GENERATED. DO NOT EDIT
"""Get various HBDK related path or compiler options."""
import os
from os import path
from enum import Enum, EnumMeta
import sys
import argparse
import collections
import subprocess
import warnings
from pkg_resources.extern import packaging
import hbdk
from hbdk.util.parser import add_warning_for_duplidate_arguments


def get_git_version():
    """Get the git version of hbdk. Empty version if fails"""
    full_version = subprocess.check_output(
        [path.join(HbdkConfig.bin_prefix, "hbdk-cc"),
         "--version"]).strip().decode('utf-8')
    for line in full_version.split('\n'):
        if line.find('git_version:') != -1:
            line = line.replace('git_version:', '')
            line = line.strip()
            return line
    return ""


def get_git_full_commit_hash():
    """Get the git full commmit hash of hbdk. Return empty if fails"""
    full_version = subprocess.check_output(
        [path.join(HbdkConfig.bin_prefix, "hbdk-cc"),
         "--version"]).strip().decode('utf-8')
    for line in full_version.split('\n'):
        if line.find('git_full_commit_hash:') != -1:
            line = line.replace('git_full_commit_hash:', '')
            line = line.strip()
            return line
    return ""


def get_git_branch():
    """Get the git branch of hbdk. Empty version if fails"""
    full_version = subprocess.check_output(
        [path.join(HbdkConfig.bin_prefix, "hbdk-cc"),
         "--version"]).strip().decode('utf-8')
    for line in full_version.split('\n'):
        if line.find('git_branch:') != -1:
            line = line.replace('git_branch:', '')
            line = line.strip()
            return line
    return ""


def get_source_dir():
    """Get source dir if recorded. Empty if not"""
    full_version = subprocess.check_output(
        [path.join(HbdkConfig.bin_prefix, "hbdk-cc"),
         "--version"]).strip().decode('utf-8')
    for line in full_version.split('\n'):
        if line.find('source_dir:') != -1:
            line = line.replace('source_dir:', '')
            line = line.strip()
            return line
    return ""


def get_x86_64_objects():
    ## For code coverage, find executable or .so files
    hbdk_cc = path.join(HbdkConfig.bin_prefix, 'hbdk-cc')
    ## Use this root dir to include unit tests executables
    root_dir = os.path.dirname(os.path.dirname(os.path.realpath(hbdk_cc)))
    objects = set()
    for root, _, files in os.walk(root_dir, followlinks=False):
        if root.find('aarch64') != -1:
            continue
        if root.find('xtensa') != -1:
            continue
        if root.find(os.path.join(root_dir, 'CMakeFiles')) != -1:
            continue
        if root.find(os.path.join(root_dir, 'public/include')) != -1:
            continue
        for filename in files:
            filename = os.path.join(root, filename)
            filename = os.path.realpath(filename)
            if not os.access(filename, os.X_OK):
                continue
            if filename in objects:
                continue
            try:
                with open(filename, "rb") as f:
                    header = f.read(20)
                    if header[:
                              8] == b'\x7f\x45\x4c\x46\x02\x01\x01\x00':  # ELF MAGIC
                        if header[
                                -2:] == b'\x3e\x00':  # e_machine == EM_X86_64 (62)
                            if header[-4:-2] in [
                                    b'\x02\x00', b'\x03\x00'
                            ]:  # e_type in [ET_EXEC, ET_DYN]
                                objects.add(filename)
            except IOError:
                pass
    return list(objects)


def get_elf_executables():
    executables = []
    for f in os.listdir(HbdkConfig.bin_prefix):
        filename = os.path.join(HbdkConfig.bin_prefix, f)
        if os.path.isfile(filename):
            try:
                with open(filename, "rb") as f:
                    magic = f.read(8)
                    if magic == b'\x7f\x45\x4c\x46\x02\x01\x01\x00':
                        executables.append(filename)
            except IOError:
                pass
    return executables


class MarchMeta(EnumMeta):
    """Make March.XXXXXX as March.UNKNOWN"""

    def __getattr__(cls, item):
        try:
            return super().__getattr__(item)
        except AttributeError:
            return super().__getattr__('UNKNOWN')


class March(Enum, metaclass=MarchMeta):
    ## NOTE: name of the members must be acceptable by other tools
    UNKNOWN = 0
    BERNOULLI = 2110040
    BERNOULLI2 = 4272728
    BAYES = 3486274
    B25E = 4534850  # NOTE-march-magic-header
    B253 = 5452354  # NOTE-march-magic-header


def get_normalized_march(march):
    """
    :param march: string (case insensitive) or March
    :return: March
    """
    if isinstance(march, str):
        march = march.lower()
    if march == March.UNKNOWN:
        raise ValueError('unrecognized march %s' % str(march))
    if march in ('x2', 'j2', 'bernoulli', March.BERNOULLI):
        return March.BERNOULLI
    if march in ('x2a', 'j2a', 'bernoulli2', March.BERNOULLI2):
        return March.BERNOULLI2
    if march in ('bpu25', 'b25', 'bayes', March.BAYES):
        return March.BAYES
    if march in ('bpu25e', 'b25e', 'bayes-e', March.B25E):
        return March.B25E
    if march in ('bpu2503', 'b253', 'bayes-a825-03', March.B253):
        return March.B253
    raise ValueError('unrecognized march %s' % str(march))


def get_tool_chain_march(march):
    march_enum = march
    if isinstance(march_enum, str):
        march_enum = get_normalized_march(march)
    if march == March.UNKNOWN:
        raise ValueError('unrecognized march %s' % str(march))
    if march_enum == March.BERNOULLI:
        return 'bernoulli'
    if march_enum == March.BERNOULLI2:
        return 'bernoulli2'
    if march_enum == March.BAYES:
        return 'bayes'
    if march_enum == March.B25E:
        ## The front end b25 and b25e are the same, current plugin not support bayes-e (need update),
        ## so bayes is returned here
        return 'bayes'
    if march_enum == March.B253:
        ## Reuse bayes front end
        return 'bayes'
    raise ValueError('unrecognized march %s' % str(march))


def is_march_supported(march):
    """Return true if the march is supported by the installed hbdk"""
    march = get_normalized_march(march)
    command = [path.join(HbdkConfig.bin_prefix, "hbdk-cc"), "--version"]
    full_version = subprocess.check_output(command).strip().decode('utf-8')
    for line in full_version.split('\n'):
        if line.find('supported_march:') != -1 and line.find(
                march.name.lower() + ",") != -1:
            return True
    return False


class HbdkConfig:
    """Helper class to get path of HBDK
    Attributes:
    prefix: root path of HBDK installation
    bin_prefix: The directory where HBDK executable locates
    include_dir: The include directory of HBDK header files.
    include_flag: The compiler flag to include HBDK header.
    cmake_dir: The cmake directory under the HBDK prefix
    """
    prefix = os.path.realpath(os.path.dirname(hbdk.__file__))
    bin_prefix = os.path.join(prefix, "bin")
    include_dir = os.path.join(prefix, "include")
    include_flag = "-I " + include_dir
    cmake_dir = os.path.join(prefix, "cmake")
    aarch64_lib_prefix = os.path.join(prefix, "lib64", "aarch64")
    aarch64_link_flag = "-L " + aarch64_lib_prefix + " -lhbrt_bernoulli_aarch64"
    x86_sim_lib_prefix = os.path.join(prefix, "lib64")
    x86_sim_link_flag = "-L " + x86_sim_lib_prefix + " -lhbdk_sim_x86"
    hbdktest_cmake_file = os.path.join(prefix, "test", "hbdktest.cmake")


def _print_include_dir() -> None:
    if not os.path.exists(HbdkConfig.include_dir):
        warnings.warn(
            'Include directory %s not found. hbdk-extra package not installed?'
            % HbdkConfig.include_dir)
    print(HbdkConfig.include_dir, end='')


def main() -> None:
    """main() function for hbdk-config"""
    parser = argparse.ArgumentParser(
        description="print various HBDK related path or compiler flags")
    add_warning_for_duplidate_arguments(parser)

    def add_arg(*args, **kwargs):
        parser.add_argument(
            *args, required=False, action="store_true", **kwargs)

    add_arg("--prefix", help="Print the root path of HBDK installation")
    add_arg(
        "--bin-prefix",
        help="Print the directory where HBDK executable locates")
    add_arg(
        "--include-dir",
        help="Print the include directory of HBDK header files")
    ## NOTE: The reason to call this option "--includes" is to follow
    ## python3-config style
    add_arg(
        "--includes", help="Print the compiler option to include HBDK headers")
    add_arg(
        "--aarch64-ldflags",
        "--aarch64-links",
        dest="aarch64_links",
        help="Print the compiler option to link HBDK aarch64 libraries")
    add_arg("--aarch64-link-dir", help="Print the aarch64 library path")
    add_arg(
        "--x86-sim-ldflags",
        "--x86-sim-links",
        dest="x86_sim_links",
        help="Print the compiler option to link HBDK x86 simulator libraries")
    add_arg("--x86-sim-link-dir", help="Print the x86 simulator library path")
    add_arg("--version", help="Print the version of HBDK")
    add_arg("--public-version", help="Print the public version of HBDK")
    add_arg(
        "--hbdktest-cmake-file",
        help="Print the path to the hbdktest CMake file")
    add_arg(
        "--dev-elf-executables",
        help=argparse.SUPPRESS,
    )
    add_arg("--source-dir", help=argparse.SUPPRESS)
    add_arg(
        "--dev-x86-64-objects",
        help=argparse.SUPPRESS,
    )
    vargs = vars(parser.parse_args())
    vargs = collections.OrderedDict(vargs)
    if not [x for x in vargs.values() if x is True]:
        parser.print_usage()
        print(
            "Error: At least one argument should be specified",
            file=sys.stderr)
        sys.exit(1)
    else:
        conversions = {
            'prefix':
            HbdkConfig.prefix,
            'bin_prefix':
            HbdkConfig.bin_prefix,
            'include_dir':
            _print_include_dir,
            'includes':
            HbdkConfig.include_flag,
            'aarch64_links':
            HbdkConfig.aarch64_link_flag,
            'aarch64_link_dir':
            HbdkConfig.aarch64_lib_prefix,
            'x86_sim_links':
            HbdkConfig.x86_sim_link_flag,
            'x86_sim_link_dir':
            HbdkConfig.x86_sim_lib_prefix,
            'cmake_dir':
            HbdkConfig.cmake_dir,
            'version':
            hbdk.__version__,
            'public_version':
            packaging.version.Version(hbdk.__version__).public,
            'hbdktest_cmake_file':
            HbdkConfig.hbdktest_cmake_file,
            'dev_elf_executables':
            (lambda: print(' '.join(get_elf_executables()), end='')),
            'source_dir': (lambda: print(get_source_dir(), end='')),
            'dev_x86_64_objects':
            (lambda: print(' '.join(get_x86_64_objects()), end='')),
        }
        is_first = True
        for arg, value in vargs.items():
            if value:
                v = conversions[arg]
                if callable(v):
                    v()
                else:
                    print(conversions[arg], end='')
                if is_first:
                    print(" ", end='')
                is_first = False
        print('')
        sys.exit(0)


if __name__ == "__main__":
    main()
