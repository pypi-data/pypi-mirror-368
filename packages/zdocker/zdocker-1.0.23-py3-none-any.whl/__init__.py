#!/usr/bin/env python3

import os
import sys
import pathlib
import json
import yaml
from six import StringIO  # Python 2 and 3 compatible

from conans.client.output import ConanOutput
from conans.client.conan_api import Conan
from conans.client.command import Command
from conans.client.cache.remote_registry import CONAN_CENTER_REMOTE_NAME
from conans.util.files import save
from conans.model.ref import ConanFileReference, get_reference_fields
from conan.tools.scm import Version
from conans.errors import NoRemoteAvailable


def in_docker():
    return os.path.exists("/.dockerenv")


def yaml_load(f):
    if (Version(yaml.__version__) < Version("5.1")):
        return yaml.load(f)
    else:
        return yaml.full_load(f)


class Zbuild:
    remote_name = "zhihe"
    remote_url = os.environ.get("CONAN_URL") or 'http://10.0.11.200:8082/artifactory/api/conan/linux-sdk'
    conan_user = os.environ.get("CONAN_USER") or 'riscv.sdk'
    conan_api_key = os.environ.get("CONAN_API_KEY") or 'eyJ2ZXIiOiIyIiwidHlwIjoiSldUIiwiYWxnIjoiUlMyNTYiLCJraWQiOiJiSFM1VGhaTmpLMFVnU0UtYlROb2kzS21naW5KbG9vaEtPcDFjN282NVZjIn0.eyJzdWIiOiJqZmFjQDAxajBoeGVidncxYXFqMDF3MjF5MDcwZDltL3VzZXJzL3Jpc2N2LnNkayIsInNjcCI6ImFwcGxpZWQtcGVybWlzc2lvbnMvYWRtaW4iLCJhdWQiOiIqQCoiLCJpc3MiOiJqZmZlQDAxajBoeGVidncxYXFqMDF3MjF5MDcwZDltIiwiaWF0IjoxNzI5NjU0NDE2LCJqdGkiOiI4YjE2OTA1Yi05ZGYzLTQwMmItYThmNi02Yzc1NmZkMzY3YTMifQ.RlbaWtUZMTqT9a3xb5Zh8b6ThvluyWlIt4iTMWUkSyrNt-UD2PFRDqdcHENRSNa5dLqziRtmERrCMuGbLjiFjzFXim0Wc3S179ikqOe_ud5Y969i4All-Cg5mPcnuQNhpmPDvaHVC5G_QV6kgUi3P6Y-iJvGJafSIvBPn0KR-Qj9b_RXgfqZ9EtTxO8XUaT-BTCsMALdYaOyVRk9qxOSiMbo9VVEFY0ZzGGWbasFpmqTJ_yfTuI25SlLlnY6lRXsZk79v7b8j7r-GBTvQUYgjofYDQti2AhJhCahdsTdpN3pr3mdS6Wqd2c0BtTCzEnIIV4ZyY1XYM0PjAxxgwAaYQ'

    def __init__(self):
        pass


zbuild = Zbuild()


def zdocker_main():
    from conanex import zflash
    zflash.main()


if __name__ == '__main__':
    zdocker_main()
