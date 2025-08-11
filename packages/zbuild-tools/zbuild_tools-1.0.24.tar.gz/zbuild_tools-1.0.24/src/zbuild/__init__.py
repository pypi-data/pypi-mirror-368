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
        self.conan_api = Conan(output=ConanOutput(StringIO()))
        self.command = Command(self.conan_api)
        self.conan_api.create_app()
        try:
            self.conan_api.users_list(self.remote_name)
        except NoRemoteAvailable:
            self.conan_api.config_init()
            for remote in self.conan_api.remote_list():
                if remote.name == CONAN_CENTER_REMOTE_NAME or (remote.name == self.remote_name and remote.url != self.remote_url):
                    self.conan_api.remote_remove(remote.name)
            self.add_remote()
            self.gen_hook()
        try:
            split_char = '/'
            try:
                idx = sys.argv.index("version")
                version = sys.argv[idx + 1]
                sdk_version, release_candidate = version.split(split_char)
                self.set_version(sdk_version, release_candidate)
            except Exception:
                pass
            self.user = self.conan_api.app.cache.config.get_item('SDK.version')
            self.channel = self.conan_api.app.cache.config.get_item('SDK.channel')
        except Exception:
            self.user, self.channel = None, None
        self.install_zbuild()

    def add_remote(self):
        self.conan_api.remote_add(self.remote_name, self.remote_url)
        self.conan_api.user_set(self.conan_user, self.remote_name)
        info = self.conan_api.users_list(self.remote_name)
        for remote in info['remotes']:
            if remote['name'] == self.remote_name and not remote['authenticated']:
                self.conan_api.authenticate(self.conan_user, self.conan_api_key, self.remote_name)
                break
        self.conan_api.users_list(self.remote_name)['remotes'][0]['authenticated']

    def set_version(self, user, channel):
        if user == '_' or channel == '_' or not user or not channel:
            if self.conan_api.app.cache.config.has_section('SDK'):
                self.conan_api.app.cache.config.rm_item('SDK')
        else:
            self.conan_api.app.cache.config.set_item('SDK.version', user)
            self.conan_api.app.cache.config.set_item('SDK.channel', channel)

    def new_reference(self, text) -> ConanFileReference:
        name, version, user, channel, revision = get_reference_fields(text)
        version = version or '*'
        user = user or self.user
        channel = channel or self.channel
        return ConanFileReference(name, version, user, channel, revision)

    def gen_hook(self):
        complete_hook = """
import os

def pre_source(output, conanfile, conanfile_path, **kwargs):
    conanfile = os.path.join(conanfile.source_folder, "conanfile.py")
    if os.path.exists(conanfile):
        os.rename(conanfile, conanfile + '.bak')

def post_source(output, conanfile, conanfile_path, **kwargs):
    conanfile1 = os.path.join(conanfile.source_folder, "conanfile.py.bak")
    conanfile2 = os.path.join(conanfile.source_folder, "conanfile.py")
    if os.path.exists(conanfile1):
        os.rename(conanfile1, conanfile2)
"""
        hook_path = os.path.join(self.conan_api.app.cache.hooks_path, "hook_source.py")
        save(hook_path, complete_hook, only_if_modified=True)
        self.conan_api.app.cache.config.set_item('hooks.hook_source', None)

    def install_module(self, ref):
        try:
            info = self.conan_api.install_reference(ref, remote_name=self.remote_name, update=True, build=['missing'])
        except Exception:
            try:
                info = self.conan_api.install_reference(ref, remote_name=self.remote_name, update=False, build=['missing'])
            except Exception:
                return False
        if not info['error'] and 'installed' in info:
            zbuild_recipe_path = info['installed'][0]['packages'][0]['cpp_info']['rootpath']
            zbuild_recipe_path = os.path.join(zbuild_recipe_path, 'zbuild')
            if os.path.exists(zbuild_recipe_path):
                sys.path.insert(0, zbuild_recipe_path)
                return True
        return False

    def get_output_yml(self):
        build_path = pathlib.Path('build')
        conanbuildinfo_file = build_path.joinpath('conanbuildinfo.json')
        if conanbuildinfo_file.exists():
            self.conandata_info = json.loads(conanbuildinfo_file.read_text())
            build_type = self.conandata_info['settings']['build_type']
            output_file = build_path.joinpath(build_type, 'output.yml')
            if output_file.exists():
                return output_file
        output_file = pathlib.Path('build/output.yml')
        if output_file.exists():
            return output_file
        return None

    def get_existed_build_version(self):
        output_file = self.get_output_yml()
        if output_file:
            with output_file.open() as f:
                data = yaml_load(f)
                version = data.get('sdk_version', '_')
                channel = data.get('sdk_channel', '_')
                return version, channel
        return None, None

    def install_zbuild(self):
        zbuild_ref_str = 'zbuild/1.0@'
        # for zflash cmd, need to check sdk version in output.yml in build dir
        if pathlib.Path(sys.argv[0]).name in ['zflash']:
            user, channel = self.get_existed_build_version()
            if user == '_' or channel == '_' or (user and channel):
                self.user = user
                self.channel = channel
        zbuild_ref = self.new_reference(zbuild_ref_str)
        if not self.install_module(zbuild_ref):
            ref = ConanFileReference.loads(zbuild_ref_str, validate=False)
            self.install_module(ref)


zbuild = Zbuild()


def zbuild_main():
    from conanex import build
    build.main()


def zrun_main():
    from conanex import zrun
    zrun.main()


def zflash_main():
    from conanex import zflash
    zflash.main()


def ndb_main():
    from adb import adb_debug
    adb_debug.main()


def tapnet_main():
    from conanex import tap
    tap.main()


def mkuenv_main():
    from uboot import mkimg
    mkimg.main()


def board_main():
    from conanex import board
    board.main()


def boardserver_main():
    from server import boardserver
    boardserver.main()


def mainserver_main():
    from server import mainserver
    mainserver.main()


def sudo_main():
    os.setuid(0)
    sys.exit(os.system(' '.join(sys.argv[1:])))


if __name__ == '__main__':
    cmd = os.path.basename(sys.argv[0])
    if cmd == 'board':
        board_main()
    elif cmd == 'zrun':
        zrun_main()
    elif cmd == 'zflash':
        zflash_main()
    elif cmd == 'sudo':
        sudo_main()
    else:
        zbuild_main()
