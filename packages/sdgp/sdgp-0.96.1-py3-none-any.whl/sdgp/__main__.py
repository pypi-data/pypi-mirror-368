#!/home/twinkle/venv/bin/python

import os
import re
import json
import argparse

import urllib.parse

######################################################################
# LIBS

from sdgp import sdgp
from sdgp.Gtk import *

######################################################################
# ArgParse

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, required=True)
    parser.add_argument('--textview', action="store_true", required=False)
    args = parser.parse_args()

    path = args.i
    flag = args.textview

    path = re.sub('^file://', '', path)
    path = urllib.parse.unquote(path)

    hako = sdgp(path)

    if hako is not None:

        # Pass Nothing
        if "prompt" in hako:
            prmp = hako.pop("prompt")
            prmp = prmp.replace("<", "[")
            prmp = prmp.replace(">", "]")
            prmp = prmp.replace("\x22", "&quot;")
            prmp = prmp.replace("&", "&amp;")
            prmp = prmp.replace("|", "\\|")
            prmp = re.sub("[\r\n]$", "", prmp)
        else: prmp = ""

        # Pass Nothing
        if "negativePrompt" in hako:
            ngtv = hako.pop("negativePrompt")
            ngtv = ngtv.replace("<", "[")
            ngtv = ngtv.replace(">", "]")
            ngtv = ngtv.replace("\x22", "&quot;")
            ngtv = ngtv.replace("&", "&amp;")
            ngtv = ngtv.replace("|", "\\|")
            ngtv = re.sub("[\r\n]$", "", prmp)
        else: ngtv = ""

        if flag is True:
            hall = f"Prompt: {prmp}\n\nNegative Prompt: {ngtv}\n\n"
            for k in hako.keys():
                hall = hall + f"{k}: {hako[k]}, "
            gtxview(hall, 'Stable Diffusion Creation Info', 'sd-get-prompt', GTK_MESSAGE_INFO, GTK_BUTTONS_OK, False)
        else:
            hall = f"<big><b>Prompt:</b></big> {prmp}\n\n<big><b>Negative Prompt:</b></big> {ngtv}\n\n"
            for k in hako.keys():
                hall = hall + f"<big><b>{k}:</b></big> {hako[k]}, "
            hall = hall.replace("&", "&amp;")
            gdialog(hall, 'Stable Diffusion Creation Info', 'sd-get-prompt', GTK_MESSAGE_INFO, GTK_BUTTONS_OK, True)

######################################################################
# MAIN
if __name__ == "__main__":
    main()

""" __DATA__

11 {'class_type': 'TripleCLIPLoader', 'inputs': {'clip_name1': 'clip_g_sdxl_base.safetensors', 'clip_name2': 'clip_l_sdxl_base.safetensors', 'clip_name3': 't5xxl.safetensors'}, '_properties': {'Node name for S&R': 'TripleCLIPLoader'}}
13 {'class_type': 'ModelSamplingSD3', 'inputs': {'model': ['252', 0], 'shift': 3.0}, '_properties': {'Node name for S&R': 'ModelSamplingSD3'}}
135 {'class_type': 'EmptySD3LatentImage', 'inputs': {'batch_size': 1, 'height': 1024, 'width': 1024}, '_properties': {'Node name for S&R': 'EmptySD3LatentImage'}}
231 {'class_type': 'VAEDecode', 'inputs': {'samples': ['271', 0], 'vae': ['252', 2]}, '_properties': {'Node name for S&R': 'VAEDecode'}}
233 {'class_type': 'PreviewImage', 'inputs': {'images': ['231', 0]}, '_properties': {'Node name for S&R': 'PreviewImage'}}
252 {'class_type': 'CheckpointLoaderSimple', 'inputs': {'_base_model': 'SD 3', 'ckpt_name': 'EMS-398059-EMS.safetensors', 'tams_ckpt_name': 'stable-diffusion-3 - medium'}, '_properties': {'Node name for S&R': 'CheckpointLoaderSimple'}}
271 {'class_type': 'KSampler', 'inputs': {'cfg': 4.5, 'denoise': 1.0, 'latent_image': ['135', 0], 'model': ['13', 0], 'negative': ['69', 0], 'positive': ['6', 0], 'sampler_name': 'dpmpp_2m', 'scheduler': 'sgm_uniform', 'seed': 813265401979403, 'steps': 28}, '_properties': {'Node name for S&R': 'KSampler'}}
6 {'class_type': 'CLIPTextEncode', 'inputs': {'clip': ['11', 0], 'text': "a female character with long, flowing hair that appears to be made of ethereal, swirling patterns resembling the Northern Lights or Aurora Borealis. The background is dominated by deep blues and purples, creating a mysterious and dramatic atmosphere. The character's face is serene, with pale skin and striking features. She wears a dark-colored outfit with subtle patterns. The overall style of the artwork is reminiscent of fantasy or supernatural genres"}, '_properties': {'Node name for S&R': 'CLIPTextEncode'}}
67 {'class_type': 'ConditioningZeroOut', 'inputs': {'conditioning': ['71', 0]}, '_properties': {'Node name for S&R': 'ConditioningZeroOut'}}
68 {'class_type': 'ConditioningSetTimestepRange', 'inputs': {'conditioning': ['67', 0], 'end': 1.0, 'start': 0.1}, '_properties': {'Node name for S&R': 'ConditioningSetTimestepRange'}}
69 {'class_type': 'ConditioningCombine', 'inputs': {'conditioning_1': ['68', 0], 'conditioning_2': ['70', 0]}, '_properties': {'Node name for S&R': 'ConditioningCombine'}}
70 {'class_type': 'ConditioningSetTimestepRange', 'inputs': {'conditioning': ['71', 0], 'end': 0.1, 'start': 0.0}, '_properties': {'Node name for S&R': 'ConditioningSetTimestepRange'}}
71 {'class_type': 'CLIPTextEncode', 'inputs': {'clip': ['11', 0], 'text': 'bad quality, poor quality, doll, disfigured, jpg, toy, bad anatomy, missing limbs, missing fingers, 3d, cgi'}, '_properties': {'Node name for S&R': 'CLIPTextEncode'}}

__END__ """
