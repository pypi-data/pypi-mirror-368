"""
 Copyright Femtosense 2024
 
 By using this software package, you agree to abide by the terms and conditions
 in the license agreement found at https://femtosense.ai/legal/eula/
"""

from femtocrux import ManagedCompilerClient


def pull_femtocrux_image():
    """
    Pull the matching femtocrux image and ask for password before running femtodriver.
    """

    docker_kwargs = {"environment": {"FS_HW_CFG": "spu1p3v1.dat"}}
    with ManagedCompilerClient(docker_kwargs=docker_kwargs) as client:
        pass
