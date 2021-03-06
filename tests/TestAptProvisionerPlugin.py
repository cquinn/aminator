# -*- coding: utf-8 -*-

#
#
#  Copyright 2013 Netflix, Inc.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
#
import logging
import os
from aminator.plugins.provisioner.apt import AptProvisionerPlugin
from aminator.config import Config

log = logging.getLogger(__name__)
console = logging.StreamHandler()
# add the handler to the root logger
logging.getLogger('').addHandler(console)


class TestAptProvisionerPlugin(object):

    def setup_method(self, method):
        self.config = Config()
        self.config.plugins = Config()
        self.config.plugins['aminator.plugins.provisioner.apt'] = self.config.from_file(yaml_file='apt_test.yml')

        self.plugin = AptProvisionerPlugin()
        self.plugin._config = self.config

        config = self.plugin._config.plugins['aminator.plugins.provisioner.apt']

        self.full_path = config.get('mountpoint', '/tmp') + "/" + \
                         config.get('policy_file_path', '/usr/sbin') + "/" + \
                         config.get('policy_file', 'policy-rc.d')

        self.plugin._mountpoint = config.get('mountpoint', '/tmp')
        if os.path.isfile(self.full_path):
            os.remove(self.full_path)

    def test_disable_enable_service_startup(self):
        assert self.plugin._deactivate_provisioning_service_block()
        assert os.path.isfile(self.full_path)

        with open(self.full_path) as f:
            content = f.readlines()

        # remove whitespace and newlines
        content = map(lambda s: s.strip(), content)
        # also remove whitespace and newlines
        original_content = self.config.plugins['aminator.plugins.provisioner.apt'].get('policy_file_content').splitlines()

        assert original_content == content

        assert self.plugin._activate_provisioning_service_block()
        assert False == os.path.isfile(self.full_path)
