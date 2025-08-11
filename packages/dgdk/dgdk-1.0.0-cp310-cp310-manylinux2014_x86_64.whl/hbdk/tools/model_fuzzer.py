# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
"""script of fuzz one model"""

import sys
import os
import argparse
import subprocess
import random
import multiprocessing
import json
from shutil import rmtree
from hbdk import hbir_helper as hbir


def parse_args():
    """
    parse arguments
    :return: a dict containing arguments
    """
    parser = argparse.ArgumentParser(description="fuzz one model")
    parser.add_argument(
        '-i',
        '--input-dir',
        required=True,
        help='seed is a directory, contain model.hbir and cc_options.yml')
    parser.add_argument(
        '-o',
        '--output-dir',
        required=True,
        help=
        'output directory, contain files for hbdk-cc, hbdk-sim and new seed')
    parser.add_argument(
        '--ip-bpu', required=False, help='the ip addr of the bpu')
    parser.add_argument(
        '--march',
        required=True,
        help='the hardware architecture of the model, valid: x2, x3')
    parser.add_argument(
        '--no-model-verifier',
        required=False,
        default=False,
        action='store_true',
        help='do not run model verifier')
    parser.add_argument(
        '--run-sim',
        required=False,
        default=False,
        action='store_true',
        help='run hbdk-sim')
    parser.add_argument(
        '-n',
        '--fuzz-iter',
        required=False,
        default=1,
        help='max fuzz iterations')
    parser.add_argument(
        '-V',
        '--verbose',
        required=False,
        default=False,
        action='store_true',
        help='print some log')
    parser.add_argument(
        '-k',
        '--keep-failed-only',
        required=False,
        default=False,
        action='store_true',
        help='keep failed models only')
    parser.add_argument(
        '-j',
        '--thread-num',
        required=False,
        default=1,
        help='number of threads when running')
    parser.add_argument(
        '--start-id',
        required=False,
        default=None,
        help=
        'start fuzzing id. If none, the program will detect it automatically')
    parser.add_argument(
        '--model-dict',
        required=False,
        default=False,
        action='store_true',
        help='enable fuzzer updating model dict')
    parser.add_argument(
        '--public',
        required=False,
        default=False,
        action='store_true',
        help='set true if fuzzer is running for public internal clients')
    parser.add_argument(
        '--enable-pruning',
        required=False,
        default=False,
        action='store_true',
        help='set true if fuzzer is allowed to prune the failed models')
    t_options = vars(parser.parse_args())
    return t_options


def run_step_cmd(t_steps,
                 step,
                 t_verbose,
                 t_cmd,
                 timeout=None,
                 log_fn=None,
                 shell=False,
                 cmds_fn=None):
    """
    run cmd
    :return:
    """
    if step is not None and t_steps is not None:
        assert step <= len(t_steps)
        print("  step ", step, "/", len(t_steps), t_steps[step - 1])
    if cmds_fn is not None:
        cmds = open(cmds_fn, 'a')
        if not shell:
            cmds.write(' '.join(t_cmd) + '\n\n')
        else:
            cmds.write(t_cmd + '\n\n')
        cmds.close()
    if t_verbose:
        if not shell:
            print("    ", ' '.join(t_cmd))
        else:
            print("    ", t_cmd)
    try:
        if log_fn is None:
            ret = subprocess.call(
                t_cmd,
                stdout=sys.stdout,
                stderr=sys.stderr,
                close_fds=True,
                timeout=timeout,
                shell=shell)
        else:
            log = open(log_fn, 'a')
            log.write('\n' + ' '.join(t_cmd) + '\n')
            ret = subprocess.call(
                t_cmd,
                stdout=log,
                stderr=log,
                close_fds=True,
                timeout=timeout,
                shell=shell)
            log.close()
    except subprocess.TimeoutExpired:
        if t_steps is not None:
            print("ERROR: step ", step, "/", len(t_steps), t_steps[step - 1])
        if log_fn:
            log = open(log_fn, 'a')
            log.write('Error: timeout!\n')
            log.close()
        print("Subprocess time out")
        return 3

    if ret != 0:
        if step is not None and t_steps is not None:
            print("ERROR: step ", step, "/", len(t_steps), t_steps[step - 1])
            print("Return code: " + str(ret))
    return ret


def delete_dir_r(d):
    try:
        output_files = os.listdir(d)
        for of in output_files:
            real_path = os.path.join(d, of)
            if os.path.isfile(real_path):
                os.remove(real_path)
            elif os.path.isdir(real_path):
                rmtree(real_path, ignore_errors=True)
            else:
                assert 0
        rmtree(d, ignore_errors=True)
    except OSError as e:  # name the Exception `e`
        print("Failed with:", e.strerror)


def handle_keep(output_d):
    if keep_failed_only:
        delete_dir_r(output_d)


def handle_model_dict_size():
    try:
        lock.acquire()
        fsize_ = os.path.getsize('./model.dict')
        lock.release()
    except (IOError, OSError):
        print("get model.dict file size failed")
        fsize_ = 0
    print("model.dict size: " + str(fsize_))
    lock.acquire()
    size_log = open('./dict_size_log.txt', 'a')
    size_log.write(str(fsize_) + "\n")
    size_log.close()
    lock.release()
    return fsize_


def run(iter_list):
    idx = 0
    while idx < len(iter_list):
        curr_iter = iter_list[idx]
        seed_len = len(seeds)
        seed_idx = random.randint(0, seed_len - 1)
        input_hbir_fn = os.path.join(input_dir, seeds[seed_idx])

        prefix_pos = seeds[seed_idx].find("_id")
        assert prefix_pos != -1
        assert len(seeds[seed_idx]) > prefix_pos + 7

        postfix_pos = seeds[seed_idx].find("_F")
        if postfix_pos == -1:
            postfix_pos = seeds[seed_idx].find(".hbir")
        assert postfix_pos != -1
        assert postfix_pos >= prefix_pos + 7

        orig_fuzz_id = seeds[seed_idx][prefix_pos + 3:postfix_pos]
        id_str = str(max_fuzz_id + curr_iter).zfill(id_num_digits)

        print("ITERATION ", curr_iter, ": [id" + id_str + "]")

        # mkdir
        output_dir = os.path.join(output_dir_orig, "id" + id_str)
        t_cmd = ['mkdir', '-p', output_dir]
        ret = subprocess.call(t_cmd, stdout=sys.stdout, stderr=sys.stderr)
        assert ret == 0

        output_fn_prefix = seeds[seed_idx][
            0:prefix_pos] + "_id" + id_str + "_F_id" + orig_fuzz_id
        output_hbir_fn = os.path.join(output_dir, output_fn_prefix + ".hbir")
        output_hbm_fn = os.path.join(output_dir, output_fn_prefix + ".hbm")
        output_hbm_fn_o2 = os.path.join(output_dir,
                                        output_fn_prefix + "_o2.hbm")

        cc_options_fn = os.path.join(output_dir, output_fn_prefix + ".ccopt")

        mxnet_json_fn = os.path.join(output_dir, 'model.json')
        mxnet_param_fn = os.path.join(output_dir, 'model.param')
        # input_data_fn = os.path.join(output_dir, "input_ddr_native.bin")
        mxnet_pred_output_fn = os.path.join(output_dir, 'mxnet_pred.onnx')
        mxnet_py_fn = os.path.join(output_dir, 'model.py')
        # inputs_option_fn = os.path.join(output_dir, 'tmp_binary.txt')

        fuzz_log_fn = os.path.join(output_dir,
                                   output_fn_prefix + '_fuzz_log.txt')

        pred_log_fn = os.path.join(output_dir,
                                   output_fn_prefix + '_pred_log.txt')

        mxnet_hbir_log_fn = os.path.join(
            output_dir, output_fn_prefix + '_mxnet_hbir_log.txt')

        hbir_mxnet_log_fn = os.path.join(
            output_dir, output_fn_prefix + '_hbir_mxnet_log.txt')

        check_log_fn = os.path.join(output_dir,
                                    output_fn_prefix + '_check_log.txt')

        cc1_log_fn = os.path.join(output_dir,
                                  output_fn_prefix + '_cc1_log.txt')

        cc2_log_fn = os.path.join(output_dir,
                                  output_fn_prefix + '_cc2_log.txt')

        prune_log_fn = os.path.join(output_dir,
                                    output_fn_prefix + '_prune_log.txt')

        verifier_log_fn = os.path.join(output_dir,
                                       output_fn_prefix + '_verifier_log.txt')

        cmds_fn = os.path.join(output_dir, 'cmds.txt')

        def try_pruning_model():
            hbir.CleanUpContext()
            pruning_model = hbir.Model()
            pruning_model.DeserializeFromFile(input_hbir_fn)
            pruning_model.InitParam(march, 'rand')
            pruning_model.SerializeToFile(input_hbir_fn)
            pruning_cmd = [
                "hbdk-fuzz", "--prune", input_hbir_fn, "--march", march, "-o",
                os.path.join(output_dir, "tmp_pruned.hbir")
            ]
            print("Start pruning failed model ...")
            ret_pruning = run_step_cmd(None, None, verbose, pruning_cmd, 3600,
                                       prune_log_fn)
            if ret_pruning != 0:
                copy_cmd = ['cp', prune_log_fn, hbir_prune_fail_dir]
                copy_ret = subprocess.call(
                    copy_cmd, stdout=sys.stdout, stderr=sys.stderr)
                assert copy_ret == 0

        cmd_fuzz = [
            "hbdk-fuzz", "-c", "-g", "-l", "-o", output_hbir_fn, input_hbir_fn,
            "--march", march, "--enable-model-dict"
        ]
        if public_mode:
            cmd_fuzz = [
                "hbdk-fuzz", "-c", "-g", "-l", "-o", output_hbir_fn,
                input_hbir_fn, "--march", march, "-p"
            ]
        lock.acquire()
        retcode = run_step_cmd(
            steps, 1, verbose, cmd_fuzz, log_fn=fuzz_log_fn, timeout=300)
        lock.release()
        if retcode != 0:
            will_copy = True
            fuzz_log = open(fuzz_log_fn, 'r')
            for line in fuzz_log.readlines():
                if line.find("Unsupported") != -1:
                    will_copy = False
                    break
                if line.find("Abort") != -1:
                    will_copy = False
                    break
                if line.find("not implemented") != -1:
                    will_copy = False
                    break
                if line.find("not supported") != -1:
                    will_copy = False
                    break
            fuzz_log.close()
            if will_copy:
                t_cmd = ['cp', fuzz_log_fn, fuzz_fail_dir]
                ret = subprocess.call(
                    t_cmd, stdout=sys.stdout, stderr=sys.stderr)
                assert ret == 0
            if public_mode:
                delete_dir_r(output_dir)
            elif enable_model_dict:
                handle_model_dict_size()
            idx += 1
            continue

        if enable_model_dict:
            fsize = handle_model_dict_size()
            if fsize > 100 * 1024 * 1024:  # clear when file size excedds 100MB
                print("Error: model.dict too big")
                return
        print("fuzz success")

        save_hbir = True
        if not os.path.exists(output_hbir_fn):
            output_hbir_fn = os.path.join(output_dir,
                                          'old_' + output_fn_prefix + ".hbir")
            save_hbir = False
        else:
            lock.acquire()
            hbir_saved.value += 1
            lock.release()

        # idx += 1
        # continue

        # opts file example:
        # --march x2
        # -s 1x128x128x3
        # --O0
        input_names = None
        shape = None
        roi_shape = None
        roi_name = None

        for i in open(cc_options_fn):
            if i.startswith("-s ") or i.startswith("--shape "):
                shape = i.split(" ")[1].strip()
            if i.startswith("roi_shape: "):
                roi_shape = i.split(" ")[1].strip()
            if i.startswith("roi_name: "):
                roi_name = i.split(" ")[1].strip()
            if i.startswith("--input-name "):
                input_names = i.split(" ")[1].strip()

        assert input_names is not None

        if roi_shape is not None:
            shape = ','.join(shape.split(',') + roi_shape.split(','))
            assert roi_name is not None
            input_names = ','.join(
                input_names.split(',') + roi_name.split(','))

        input_data_fn = ','.join([
            os.path.join(output_dir,
                         input_names.split(',')[i] + '.bin')
            for i, j in enumerate(input_names.split(','))
        ])

        retcode = run_step_cmd(
            steps,
            2,
            verbose,
            ['hbdk-hbir-mxnet', '-i', output_hbir_fn, '-o', mxnet_py_fn],
            log_fn=hbir_mxnet_log_fn)
        if retcode != 0:
            print("hbir2mxnet FAILED")
            t_cmd = ['cp', hbir_mxnet_log_fn, hbir_mxnet_fail_dir]
            ret = subprocess.call(t_cmd, stdout=sys.stdout, stderr=sys.stderr)
            assert ret == 0
            if public_mode:
                delete_dir_r(output_dir)
            idx += 1
            continue
            # assert 0
        retcode = run_step_cmd(
            steps, 3, verbose, ['python3', mxnet_py_fn], cmds_fn=cmds_fn)
        if retcode != 0:
            print("python FAILED")
            t_cmd = ['cp', output_hbir_fn, python_fail_dir]
            ret = subprocess.call(t_cmd, stdout=sys.stdout, stderr=sys.stderr)
            assert ret == 0
            if public_mode:
                delete_dir_r(output_dir)
            idx += 1
            continue
            # assert 0
        retcode = run_step_cmd(
            steps,
            4,
            verbose, [
                'hbdk-pred', '--march', march, '-m', mxnet_json_fn, '-s',
                shape, '--input-name', input_names, '-p', mxnet_param_fn,
                '--gen-random-param-and-exit'
            ],
            timeout=7200,
            log_fn=pred_log_fn,
            cmds_fn=cmds_fn)
        if retcode != 0:
            print("pred FAILED")
            t_cmd = ['cp', pred_log_fn, pred_fail_dir]
            ret = subprocess.call(t_cmd, stdout=sys.stdout, stderr=sys.stderr)
            assert ret == 0
            if public_mode:
                delete_dir_r(output_dir)
            idx += 1
            continue
        retcode = run_step_cmd(
            steps,
            5,
            verbose, [
                'hbdk-pred', '--march', march, '-m', mxnet_json_fn, '-s',
                shape, '--input-name', input_names, '-b', input_data_fn,
                '--gen-random-input-and-exit'
            ],
            timeout=7200,
            log_fn=pred_log_fn,
            cmds_fn=cmds_fn)
        if retcode != 0:
            print("pred FAILED")
            t_cmd = ['cp', pred_log_fn, pred_fail_dir]
            ret = subprocess.call(t_cmd, stdout=sys.stdout, stderr=sys.stderr)
            assert ret == 0
            if public_mode:
                delete_dir_r(output_dir)
            idx += 1
            continue
        retcode = run_step_cmd(
            steps,
            6,
            verbose, [
                'hbdk-pred', '--march', march, '-m', mxnet_json_fn, '-s',
                shape, '--input-name', input_names, '-p', mxnet_param_fn, '-b',
                input_data_fn, '-o', mxnet_pred_output_fn
            ],
            timeout=7200,
            log_fn=pred_log_fn,
            cmds_fn=cmds_fn)
        if retcode != 0:
            print("pred FAILED")
            t_cmd = ['cp', pred_log_fn, pred_fail_dir]
            ret = subprocess.call(t_cmd, stdout=sys.stdout, stderr=sys.stderr)
            assert ret == 0
            if public_mode:
                delete_dir_r(output_dir)
            idx += 1
            continue
        retcode = run_step_cmd(
            steps,
            7,
            verbose, [
                'hbdk-mxnet-hbir', '-j', mxnet_json_fn, '-s', shape, '-o',
                output_hbir_fn, '--input-name', input_names
            ],
            log_fn=mxnet_hbir_log_fn,
            cmds_fn=cmds_fn)
        if retcode != 0:
            print("mxnet2hbir FAILED")
            t_cmd = ['cp', mxnet_hbir_log_fn, mxnet_hbir_fail_dir]
            ret = subprocess.call(t_cmd, stdout=sys.stdout, stderr=sys.stderr)
            assert ret == 0
            if public_mode:
                delete_dir_r(output_dir)
            idx += 1
            continue

        cmd_check = [
            'hbdk-model-check', '--march', march, '-m', mxnet_json_fn, '-s',
            shape, '-p', mxnet_param_fn, '--input-name', input_names
        ]
        check_ret_v = run_step_cmd(
            steps,
            8,
            verbose,
            cmd_check,
            timeout=7200,
            log_fn=check_log_fn,
            cmds_fn=cmds_fn)
        # 255 can be -1 from ret of target binary, 255 here means logic checker fails
        if check_ret_v == 255:
            will_copy = True
            check_log = open(check_log_fn, 'r')
            for line in check_log.readlines():
                if line.find("UNSUPPORTED") != -1:
                    will_copy = False
                    break
            check_log.close()
            if will_copy:
                t_cmd = ['cp', check_log_fn, check_fail_dir]
                ret = subprocess.call(
                    t_cmd, stdout=sys.stdout, stderr=sys.stderr)
                assert ret == 0
            print("CHECK FAILED")
            if public_mode:
                delete_dir_r(output_dir)
            elif enable_pruning:
                try_pruning_model()
            idx += 1
            continue
        if check_ret_v not in (0, 255):
            will_copy = True
            check_log = open(check_log_fn, 'r')
            for line in check_log.readlines():
                if line.find("UNSUPPORTED") != -1:
                    will_copy = False
                    break
            check_log.close()
            if will_copy:
                t_cmd = ['cp', check_log_fn, check_cc_fail_dir]
                ret = subprocess.call(
                    t_cmd, stdout=sys.stdout, stderr=sys.stderr)
                assert ret == 0
            print("CHECK FAILED")
            if public_mode:
                delete_dir_r(output_dir)
            elif enable_pruning:
                try_pruning_model()
            idx += 1
            continue

        cc1_ret_v = 0
        if not public_mode:
            cc1_ret_v = run_step_cmd(
                steps,
                9,
                verbose, [
                    'hbdk-cc', '--march', march, '-m', mxnet_json_fn, '-s',
                    shape, '-p', mxnet_param_fn, '-o', output_hbm_fn,
                    '--input-name', input_names, '--dev-enable-hw-perf'
                ],
                timeout=7200,
                log_fn=cc1_log_fn,
                cmds_fn=cmds_fn)

        cmd_cc2 = [
            'hbdk-cc', '--march', march, '-m', mxnet_json_fn, '-s', shape,
            '-p', mxnet_param_fn, '--O2', '-o', output_hbm_fn_o2,
            '--input-name', input_names, '--dev-enable-hw-perf'
        ]
        if public_mode:
            try:
                tmp_cc_dir = os.path.join(output_dir, "tmp_cc")
                os.mkdir(tmp_cc_dir)
            except OSError:
                pass
            cmd_cc2 = [
                "hbdk-cc", "-f", "mxnet", "--march", march, "-m",
                mxnet_json_fn, "-s", shape, "-p", mxnet_param_fn, "-g",
                "--reference", mxnet_pred_output_fn, "-o",
                os.path.join(tmp_cc_dir, output_fn_prefix + ".hbm"), "-n",
                output_fn_prefix, "--input-layout", "NCHW", "--output-layout",
                "NCHW", "-b", input_data_fn, "--save-temps", "--execute",
                "--enable-logging", "--dev-enable-hw-perf", "--dev-dump-graph",
                "--O2", "--dev-init-sram", "0xdeadbeef"
            ]
        cc2_ret_v = run_step_cmd(
            steps,
            10,
            verbose,
            cmd_cc2,
            timeout=7200,
            log_fn=cc2_log_fn,
            cmds_fn=cmds_fn)

        if cc1_ret_v or cc2_ret_v:
            if cc1_ret_v:
                t_cmd = ['cp', cc1_log_fn, cc_fail_dir]
                ret = subprocess.call(
                    t_cmd, stdout=sys.stdout, stderr=sys.stderr)
                assert ret == 0
            if cc2_ret_v:
                t_cmd = ['cp', cc2_log_fn, cc_fail_dir]
                ret = subprocess.call(
                    t_cmd, stdout=sys.stdout, stderr=sys.stderr)
                assert ret == 0

            print("CC FAILED")
            if public_mode:
                delete_dir_r(output_dir)
            elif enable_pruning:
                try_pruning_model()
            idx += 1
            continue

        if check_ret_v != cc1_ret_v or check_ret_v != cc2_ret_v:
            t_cmd = ['cp', output_hbir_fn, candidates_dir]
            ret = subprocess.call(t_cmd, stdout=sys.stdout, stderr=sys.stderr)
            assert ret == 0
            print("CANDIDATE")
            if public_mode:
                delete_dir_r(output_dir)
            idx += 1
            continue

        if run_sim:
            sim_log_fn = os.path.join(output_dir,
                                      output_fn_prefix + '_sim_log.txt')
            tmp_sim_dir = os.path.join(output_dir, "tmp_sim")
            try:
                os.mkdir(tmp_sim_dir)
            except OSError:
                pass
            sram_records_dir = os.path.join(tmp_sim_dir, "sram_records")
            try:
                os.mkdir(sram_records_dir)
            except OSError:
                pass

            cmd_sim = [
                'hbdk-sim', '--hbm', output_hbm_fn, '--model-name',
                output_fn_prefix, '--reference', mxnet_pred_output_fn, '-o',
                tmp_sim_dir, '--perf', '--enable-logging', '--input-binary',
                input_data_fn, '--dev-export-snapshot', '0,0'
            ]
            if public_mode:
                cmd_sim = [
                    'hbdk-sim', '--hbm',
                    os.path.join(tmp_cc_dir,
                                 output_fn_prefix + ".hbm"), '--model-name',
                    output_fn_prefix, '--reference', mxnet_pred_output_fn,
                    '-o', tmp_sim_dir, '--perf', '--enable-logging',
                    '--input-binary', input_data_fn, '--dev-export-snapshot',
                    '0,0', '--dev-dump-sram', '--dev-dump-read-sram'
                ]
            ret_sim = run_step_cmd(
                steps,
                11,
                verbose,
                cmd_sim,
                log_fn=sim_log_fn,
                cmds_fn=cmds_fn)
            if ret_sim != 0:
                print("sim hbm FAILED")
                if public_mode:
                    delete_dir_r(output_dir)
                idx += 1
                continue
            ret_sim2 = 0
            if public_mode:
                tmp_sim_from_snapshot_dir = os.path.join(
                    output_dir, "tmp_sim_from_snapshot")
                try:
                    os.mkdir(tmp_sim_from_snapshot_dir)
                except OSError:
                    pass
                ret_sim2 = run_step_cmd(
                    steps,
                    12,
                    verbose, [
                        "hbdk-sim", "--snapshot",
                        os.path.join(tmp_sim_dir, "snapshot_fc_0_inst_0.json"),
                        "-o", tmp_sim_from_snapshot_dir, "--enable-logging"
                    ],
                    log_fn=sim_log_fn,
                    cmds_fn=cmds_fn)
            if ret_sim == 0 and ret_sim2 == 0:
                print('SIM SUCCESS')
            else:
                t_cmd = ['cp', output_hbir_fn, sim_fail_dir]
                ret = subprocess.call(
                    t_cmd, stdout=sys.stdout, stderr=sys.stderr)
                assert ret == 0
                print("sim snapshot FAILED")
                if public_mode:
                    delete_dir_r(output_dir)
                idx += 1
                continue

            if public_mode:
                tmp_tool_check_dir = os.path.join(output_dir, "tmp_tool_check")
                try:
                    os.mkdir(tmp_tool_check_dir)
                except OSError:
                    pass
                ret_public = run_step_cmd(
                    None,
                    None,
                    verbose,
                    "hbdk-unpack " + os.path.join(tmp_cc_dir, "*.hbm") + " -o "
                    + tmp_tool_check_dir,
                    shell=True,
                    cmds_fn=cmds_fn)
                if ret_public != 0:
                    print("Unpack failed")
                    delete_dir_r(output_dir)
                    idx += 1
                    continue
                ret_public = run_step_cmd(
                    None,
                    None,
                    verbose,
                    "hbdk-pack " + os.path.join(tmp_tool_check_dir, "*") +
                    " -o " + os.path.join(tmp_tool_check_dir, "packed.hbm"),
                    shell=True,
                    cmds_fn=cmds_fn)
                if ret_public != 0:
                    print("Pack failed")
                    delete_dir_r(output_dir)
                    idx += 1
                    continue
                ret_public = run_step_cmd(
                    None,
                    None,
                    verbose,
                    "hbdk-disas " + mxnet_param_fn + " -o " + os.path.join(
                        tmp_tool_check_dir, "disassembled.param.txt"),
                    shell=True,
                    cmds_fn=cmds_fn)
                if ret_public != 0:
                    print("Diassemble param failed")
                    delete_dir_r(output_dir)
                    idx += 1
                    continue
                ret_public = run_step_cmd(
                    None,
                    None,
                    verbose,
                    "hbdk-disas " + os.path.join(
                        tmp_tool_check_dir, "*.hbm") + " -o " + os.path.join(
                            tmp_tool_check_dir, "disassembled.hbm.txt"),
                    shell=True,
                    cmds_fn=cmds_fn)
                if ret_public != 0:
                    print("Diassemble hbm to txt failed")
                    delete_dir_r(output_dir)
                    idx += 1
                    continue
                ret_public = run_step_cmd(
                    None,
                    None,
                    verbose,
                    "hbdk-disas " + os.path.join(tmp_tool_check_dir, "*.hbm") +
                    " --json " + " -o " + os.path.join(
                        tmp_tool_check_dir, "disassembled.hbm.json"),
                    shell=True,
                    cmds_fn=cmds_fn)
                if ret_public != 0:
                    print("Diassemble hbm to json failed")
                    delete_dir_r(output_dir)
                    idx += 1
                    continue
                ret_public = run_step_cmd(
                    None,
                    None,
                    verbose,
                    "hbdk-disas " + os.path.join(
                        tmp_tool_check_dir,
                        "*.hbdesc") + " -o " + os.path.join(
                            tmp_tool_check_dir, "disassembled.hbdesc.txt"),
                    shell=True,
                    cmds_fn=cmds_fn)
                if ret_public != 0:
                    print("Diassemble hbdesc")
                    delete_dir_r(output_dir)
                    idx += 1
                    continue
                ret_public = run_step_cmd(
                    None,
                    None,
                    verbose,
                    "hbdk-disas " + os.path.join(
                        tmp_tool_check_dir,
                        "*.hbinst") + " -o " + os.path.join(
                            tmp_tool_check_dir, "disassembled.hbinst.txt"),
                    shell=True,
                    cmds_fn=cmds_fn)
                if ret_public != 0:
                    print("Diassemble hbinst")
                    delete_dir_r(output_dir)
                    idx += 1
                    continue
                ret_public = run_step_cmd(
                    None,
                    None,
                    verbose,
                    "hbdk-as " + os.path.join(tmp_tool_check_dir,
                                              "*.hbinst.txt") + " -o " +
                    os.path.join(tmp_tool_check_dir, "assembled.hbinst"),
                    shell=True,
                    cmds_fn=cmds_fn)
                if ret_public != 0:
                    print("Assemble *.hbinst.txt back to *.hbinst failed")
                    delete_dir_r(output_dir)
                    idx += 1
                    continue
                ret_public = run_step_cmd(
                    None,
                    None,
                    verbose,
                    "hbdk-disas " + os.path.join(
                        tmp_sim_dir, "snapshot_fc_0_inst_0.hbfunc") +
                    " --filetype hbfunc --march " + march + " -o " +
                    os.path.join(tmp_sim_dir, "disassembled.hbfunc.txt"),
                    shell=True,
                    cmds_fn=cmds_fn)
                if ret_public != 0:
                    print("Disassemble func failed")
                    delete_dir_r(output_dir)
                    idx += 1
                    continue
                ret_public = run_step_cmd(
                    None,
                    None,
                    verbose,
                    "hbdk-as " + os.path.join(tmp_sim_dir, "*.hbfunc.txt")
                    + " --no-header -o " + os.path.join(
                        tmp_sim_dir, "assembled.hbfunc"),
                    shell=True,
                    cmds_fn=cmds_fn)
                if ret_public != 0:
                    print("Assemble func failed")
                    delete_dir_r(output_dir)
                    idx += 1
                    continue
                tmp_perf_dir = os.path.join(output_dir, "tmp_perf")
                try:
                    os.mkdir(tmp_perf_dir)
                except OSError:
                    pass
                ret_public = run_step_cmd(
                    None,
                    None,
                    verbose,
                    "hbdk-perf " + os.path.join(
                        tmp_cc_dir, output_fn_prefix + ".hbm") + " -o " +
                    tmp_perf_dir,
                    shell=True,
                    cmds_fn=cmds_fn)
                if ret_public != 0:
                    print("Perf from hbm failed")
                    delete_dir_r(output_dir)
                    idx += 1
                    continue
                ret_public = run_step_cmd(
                    None,
                    None,
                    verbose,
                    "hbdk-perf " + os.path.join(
                        tmp_cc_dir, output_fn_prefix + ".hbinst") + " -o " +
                    tmp_perf_dir,
                    shell=True,
                    cmds_fn=cmds_fn)
                if ret_public != 0:
                    print("Perf from hbinst failed")
                    delete_dir_r(output_dir)
                    idx += 1
                    continue

        if no_model_verifier:
            if save_hbir:
                t_cmd = ['cp', output_hbir_fn, input_dir]
                ret = subprocess.call(
                    t_cmd, stdout=sys.stdout, stderr=sys.stderr)
                assert ret == 0
                t_cmd = ['cp', cc_options_fn, ccopt_dir]
                ret = subprocess.call(
                    t_cmd, stdout=sys.stdout, stderr=sys.stderr)
                assert ret == 0
                output_file_name = output_fn_prefix + ".hbir"
                lock.acquire()
                seeds.append(output_file_name)
                lock.release()
            handle_keep(output_dir)
            print("SUCCESS")
            idx += 1
            continue

        # below handles model verifier
        try:
            fsize = os.path.getsize(output_hbm_fn)
        except (IOError, OSError):
            fsize = 0
        if fsize > 100 * 1024 * 1024:  # clear when file size exceeds 100MB
            handle_keep(output_dir)
            print("Hbm file too big")
            idx += 1
            continue

        disas_json_fn = os.path.join(output_dir, 'disas.json')
        f_disas = open(disas_json_fn, 'w')
        ret = subprocess.call(['hbdk-disas', output_hbm_fn, '--json'],
                              stdout=f_disas,
                              stderr=sys.stderr,
                              close_fds=True)
        f_disas.close()
        assert ret == 0

        f_disas = open(disas_json_fn, 'r')
        js_obj = json.load(f_disas)
        output_region_size = js_obj[0]['total output region size']
        if output_region_size > 50 * 1024 * 1024:
            handle_keep(output_dir)
            print("Output region size too big")
            idx += 1
            continue

        input_features = js_obj[0]['input features']
        names = []
        for input_feature in input_features:
            postfix_idx = input_feature['feature name'].find('_output')
            if postfix_idx == -1:
                postfix_idx = input_feature['feature name'].find(
                    '_inhardwarelayout')
            if postfix_idx != -1:
                names.append(input_feature['feature name'][:postfix_idx])
            else:
                names.append(input_feature['feature name'])

        f_orig_json = open(os.path.join(output_dir, 'model.json'), 'r')
        orig_json = json.load(f_orig_json)
        nodes = orig_json['nodes']
        names_in_cmd = []
        for name in names:
            for node in nodes:
                if node['name'] == name:
                    if node['op'] == 'QuantiInput':
                        user_input_idx = node['inputs'][0][0]
                        names_in_cmd.append(nodes[user_input_idx]['name'])
                    elif node['op'] == 'null':
                        names_in_cmd.append(name)
                    else:
                        assert 0

        assert len(names_in_cmd) == len(names)
        names_in_cmd = ','.join([
            os.path.join(output_dir, n_in_cmd + '.bin')
            for n_in_cmd in names_in_cmd
        ])

        ret_model_verifier1 = run_step_cmd(
            steps,
            13,
            verbose, [
                'hbdk-model-verifier', '--model-input', names_in_cmd, '--hbm',
                output_hbm_fn, '--model-json',
                os.path.join(output_dir, 'model.json'), '--model-param',
                os.path.join(output_dir, 'model.param'), '--ip', ip_bpu,
                '--local-work-path', output_dir
            ],
            timeout=7200,
            log_fn=verifier_log_fn,
            cmds_fn=cmds_fn)

        if ret_model_verifier1 == 0:
            if save_hbir:
                t_cmd = ['cp', output_hbir_fn, input_dir]
                ret = subprocess.call(
                    t_cmd, stdout=sys.stdout, stderr=sys.stderr)
                assert ret == 0
                t_cmd = ['cp', cc_options_fn, ccopt_dir]
                ret = subprocess.call(
                    t_cmd, stdout=sys.stdout, stderr=sys.stderr)
                assert ret == 0
                output_file_name = output_fn_prefix + ".hbir"
                lock.acquire()
                seeds.append(output_file_name)
                lock.release()
            handle_keep(output_dir)
            print("SUCCESS")
        else:
            t_cmd = ['cp', verifier_log_fn, verifier_fail_dir]
            ret = subprocess.call(t_cmd, stdout=sys.stdout, stderr=sys.stderr)
            assert ret == 0
            print("VERIFIER FAILED")

        idx += 1


lock = multiprocessing.Lock()

options = parse_args()

steps = [
    'fuzz hbir', 'hbir to py', 'py to json', 'gen param', 'gen input',
    'mxnet pred', 'json to hbir', 'model check', 'compiler O0', 'compiler O2',
    'sim hbm', 'sim snapshot', 'model verifier'
]
run_sim = options['run_sim']
no_model_verifier = options['no_model_verifier']
if not no_model_verifier:
    steps.append('model verifier')

input_dir = options['input_dir']
ccopt_dir = './ccopt_files'
output_dir_orig = options['output_dir']
iter_num = int(options['fuzz_iter'])
verbose = options['verbose']
enable_pruning = options['enable_pruning']
start_id = options['start_id']
keep_failed_only = options['keep_failed_only']
num_thread = int(options['thread_num'])
ip_bpu = options['ip_bpu']
march = options['march']
enable_model_dict = options['model_dict']
if march not in ['x2', 'x3']:
    print("Unsupported march. Supported arg: x2, x3")
    exit(1)
public_mode = options['public']

if num_thread > 1:
    verbose = False
    steps = None
    print(
        "Warning: program automatically disabled verbose due to multi-thread processing"
    )

if public_mode and keep_failed_only:
    print(
        "error: Options \'--public\' and \'-k\' cannot exist at the same time")
    exit(1)

if public_mode and enable_model_dict:
    print(
        "error: Options \'--public\' and \'--model-dict\' cannot exist at the same time"
    )
    exit(1)

# mkdir
candidates_dir = os.path.join(output_dir_orig, "candidates")
os.makedirs(candidates_dir, exist_ok=True)

fuzz_fail_dir = os.path.join(output_dir_orig, "fuzz_fails")
os.makedirs(fuzz_fail_dir, exist_ok=True)

pred_fail_dir = os.path.join(output_dir_orig, "pred_fails")
os.makedirs(pred_fail_dir, exist_ok=True)

mxnet_hbir_fail_dir = os.path.join(output_dir_orig, "mxnet_hbir_fails")
os.makedirs(mxnet_hbir_fail_dir, exist_ok=True)

hbir_mxnet_fail_dir = os.path.join(output_dir_orig, "hbir_mxnet_fails")
os.makedirs(hbir_mxnet_fail_dir, exist_ok=True)

hbir_prune_fail_dir = os.path.join(output_dir_orig, "hbir_prune_fails")
os.makedirs(hbir_prune_fail_dir, exist_ok=True)

python_fail_dir = os.path.join(output_dir_orig, "python_fails")
os.makedirs(python_fail_dir, exist_ok=True)

check_fail_dir = os.path.join(output_dir_orig, "check_fails")
os.makedirs(check_fail_dir, exist_ok=True)

cc_fail_dir = os.path.join(output_dir_orig, "cc_fails")
os.makedirs(cc_fail_dir, exist_ok=True)

check_cc_fail_dir = os.path.join(output_dir_orig, "check_cc_fails")
os.makedirs(check_cc_fail_dir, exist_ok=True)

verifier_fail_dir = os.path.join(output_dir_orig, "model_verifier_fails")
os.makedirs(verifier_fail_dir, exist_ok=True)

sim_fail_dir = os.path.join(output_dir_orig, "sim_fails")
os.makedirs(sim_fail_dir, exist_ok=True)

seeds = multiprocessing.Manager().list()
files = os.listdir(input_dir)
for f in files:
    if f.endswith('.hbir'):
        seeds.append(f)
seeds.sort()
if len(seeds) < 50:
    print("SEEDS: ", seeds)

seed_num = len(seeds)
assert seed_num > 0
start_pos = seeds[seed_num - 1].find("_id")
end_pos = seeds[seed_num - 1].find("_F")
if end_pos == -1:
    end_pos = seeds[seed_num - 1].find(".hbir")
max_fuzz_id = 100000
if start_pos != -1 and end_pos != -1:
    max_fuzz_id = int(seeds[seed_num - 1][start_pos + 3:end_pos]) + 1
if start_id is not None:
    max_fuzz_id = int(start_id)
id_num_digits = 6

hbir_saved = multiprocessing.Manager().Value('i', 0)


def main():
    print("ITERATIONS: ", iter_num)

    num_thread_batch = int((iter_num - iter_num % num_thread) / num_thread)
    iter_list_list = []
    for n in range(num_thread):
        curr_iter_list = []
        for j in range(num_thread_batch):
            curr_iter_list.append(n + j * num_thread)
        iter_list_list.append(curr_iter_list)

    rest_iter_list_list = []
    for i in range(num_thread_batch * num_thread, iter_num):
        rest_iter_list_list.append([i])

    with multiprocessing.Pool(processes=num_thread) as pool:
        pool.map(run, iter_list_list)

    num_rest_thread = iter_num % num_thread
    assert num_rest_thread == len(rest_iter_list_list)
    if num_rest_thread > 0:
        with multiprocessing.Pool(processes=num_rest_thread) as pool:
            pool.map(run, rest_iter_list_list)

    if public_mode:
        for d in os.listdir(output_dir_orig):
            if d.startswith('id'):
                d_path = os.path.join(output_dir_orig, d)
                if not os.listdir(d_path):
                    os.removedirs(d_path)

    print("Total number of updated models in model dict: " +
          str(hbir_saved.value))


if __name__ == "__main__":
    main()
