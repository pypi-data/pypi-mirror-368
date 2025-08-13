# -*- coding: utf-8 -*-
import errno
import logging
import os
from pathlib import Path
import platform
import requests
import shutil
import subprocess
try:
    from tqdm import tqdm
except ImportError:
    def __dummy_tqdm(iterable, total=None):
        return iterable
    tqdm = __dummy_tqdm


def mkdirp(dir: Path, dryrun: bool=False) -> None:
    """ Equivalent to mkdir -p <dir> """
    logging.info(f"Make dir: {dir}")
    if dryrun:
        return
    dir.mkdir(parents=True, exist_ok=True)


def download(url: str, file_path: Path, dryrun: bool=False) -> None:
    """ Download file from the url to file_path. """
    logging.info(f"Download: {url} -> {file_path}")
    if dryrun:
        return
    if file_path.exists():
        return
    resp = requests.get(url, stream=True)
    total_length = resp.headers.get('content-length')
    if total_length is not None:
        total_length = int(total_length)
    with open(file_path, "wb") as fs:
        for data in tqdm(resp.iter_content(), total=total_length):
            fs.write(data)


def unpack(package_path: Path, target_dir: Path, dryrun: bool=False) -> None:
    logging.info(f"Unpack: {package_path} -> {target_dir}")
    if dryrun:
        return
    shutil.unpack_archive(package_path, target_dir)


def cmake_prepare_build_dir(build_dir: Path, rebuild: bool = True, dryrun: bool=False) -> None:
    logging.info(f"Prepare cmake build dir: {build_dir} rebuild: {rebuild}")
    if dryrun:
        return
    # Windows seems can't remove hidden directories, like .git, raising
    # "PermissionError: [WinError 5] Access is denied".
    def __rm_readonly(func, path, exc):
        excvalue = exc[1]
        if (platform.system() == "Windows" and
            excvalue.errno in (errno.EACCES, errno.ENOTEMPTY)):
            # Try platform specific commands.
            if Path(path).is_dir():
                cmd = f"rmdir /s /q {path}"
            else:
                cmd = f"del /f /q {path}"
            logging.warning(
                f"Failed to run {func} on {path}, err={excvalue} try command={cmd}")
            run_cmd(cmd)
        else:
            raise Exception(exc)
    if rebuild and build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=False,
                      onexc=__rm_readonly)
    mkdirp(build_dir)


def run_cmd(cmd: str, dryrun: bool=False) -> None:
    segments = cmd.split("\n")
    segments = [seg.strip(" ") for seg in segments]
    formatted_cmd = " ".join(segments)
    logging.info(f"Execute: {os.getcwd()}$ {formatted_cmd}")
    if dryrun:
        return
    # Use shell=True since commands are provided by project author, security check is useless.
    proc = subprocess.Popen(
        formatted_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        shell=True, env=os.environ)
    for line in iter(proc.stdout.readline, b""):
        print(line.decode(), end="")
    returncode = proc.wait()
    if returncode != 0:
        raise Exception(f"Failed to execute cmd=\"{formatted_cmd}\" exit={returncode}")

