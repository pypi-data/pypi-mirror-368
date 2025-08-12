import os
import subprocess


def get_filepath_filename_ext(fire_url):
    """
    获取文件路径， 文件名， 后缀名
    :param fire_url:
    :return:
    """
    filepath, tmp_filename = os.path.split(fire_url)
    short_name, extension = os.path.splitext(tmp_filename)
    return filepath, short_name, extension


def exec_cmd(cmd_text):
    process = subprocess.Popen(cmd_text, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    command_output = process.stdout.read()
    print(command_output)
