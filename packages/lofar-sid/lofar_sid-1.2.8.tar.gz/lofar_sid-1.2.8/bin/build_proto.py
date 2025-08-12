#!/usr/bin/env python3

#  Copyright (C) 2023 ASTRON (Netherlands Institute for Radio Astronomy)
#  SPDX-License-Identifier: Apache-2.0

import os
import glob
from importlib import resources
from grpc_tools import protoc

proto_dir = os.path.join(os.getcwd(), "proto")
print(f"Compiling proto files in dir {proto_dir}...")

if not os.path.exists(proto_dir):
    exit(-1)

files = glob.glob('./**/*.proto', recursive=True)

proto_file_name = (resources.files("grpc_tools") / "_proto").resolve()
for file in files:
    print(f"Process {file}")
    protoc.main([
        '-c', '-Ilofar_sid/interface=proto', f'-I{proto_file_name}', '--python_out=.', '--pyi_out=.', '--grpc_python_out=.', file
    ])

print("Complete")
