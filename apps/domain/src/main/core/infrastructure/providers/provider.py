import json
import os
import subprocess
import time
from pathlib import Path
from types import SimpleNamespace

import terrascript
import terrascript.data as data
import terrascript.provider as provider
import terrascript.resource as resource
from terrascript import Module

from ..tf import Terraform
from ..utils import Config


class Provider:
    def __init__(self, root_dir, provider=None):
        os.makedirs(root_dir, exist_ok=True)
        self.TF = Terraform(dir=root_dir, provider=provider)
        self.tfscript = terrascript.Terrascript()
        self.validated = False

    def validate(self):
        self.TF.write(self.tfscript)
        try:
            self.TF.init()
            self.TF.validate()
            self.validated = True
            return True
        except subprocess.CalledProcessError as err:
            return False

    def deploy(self):
        if not self.validated:
            return (False, {})

        try:
            self.TF.apply()
            output = self.TF.output()
            return (True, output)
        except subprocess.CalledProcessError as err:
            return (False, {"ERROR": err})

    def destroy(self):
        try:
            self.TF.destroy()
            return True
        except subprocess.CalledProcessError as err:
            return False
