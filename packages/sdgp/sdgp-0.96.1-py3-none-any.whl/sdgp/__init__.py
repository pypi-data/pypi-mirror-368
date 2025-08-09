#!/home/twinkle/venv/bin/python

import json
import re

######################################################################
# LIBS

from sdgp.Gtk import *

######################################################################
# VARS

PNGH = b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"
IHDR = b"\x00\x00\x00\x0d\x49\x48\x44\x52"

######################################################################
# DEFS

def read_exif(f) -> dict:

    e = {}
    t = ''
    w = 0
    h = 0
    d = 0
    p = ''

    try:
        fh = open(f ,'rb')
    except Exception as e:
        e['_ERROR_'] = e
        return e
    # PNG Header
    t = fh.read(8)
    if(t != PNGH):
        fh.close()
        e['_ERROR_'] = 'Invalid PNG Signature'
        return e
    # IHDR Chunk
    t = fh.read(8)
    if(t != IHDR):
        fh.close()
        e['_ERROR_'] = 'Invalid IHDR'
        return e

    e['PNG'] = 1

    # Width
    t = fh.read(4)
    e['width'] = int.from_bytes(t)
    # Height
    t = fh.read(4)
    e['height'] = int.from_bytes(t)
    # Pixel Depth
    t = fh.read(1)
    e['depth'] = int.from_bytes(t)
    # Color Type
    t = fh.read(1)
    e['color'] = int.from_bytes(t)
    # Compression Method
    t = fh.read(1)
    e['compression'] = int.from_bytes(t)
    # Filter Type
    t = fh.read(1)
    e['filter'] = int.from_bytes(t)
    # Interlace
    t = fh.read(1)
    e['interlace'] = int.from_bytes(t)
    # CRC
    t = fh.read(4)
    e['CRC'] = int.from_bytes(t)

    e['parameters_Pos'] = fh.tell()

    # getChunkSize()
    t = fh.read(4)
    # Size of parameters
    e['parameters_Size'] = int.from_bytes(t);

    # check tEXt(when iTXt on Meitu)
    t = fh.read(4)
    if t != b'tEXt' and t != b'iTXt':
        fh.close()
        e['_ERROR_'] = 'tEXt: Nothing tEXt chunk!('+t.decode('utf-8')+')'
        return e

    # parameters
    p = fh.read(e['parameters_Size'])

    # Stable-Diffusion
    if re.match('parameters', p.decode('utf-8')):
        t = re.sub('^parameters.', '', p.decode('utf-8'))
        s = t.split('\n', 2);
        e['prompt'] = s.pop(0)
        e['negativePrompt'] = s.pop(0)
        r = s[0].split(', ')
        for i in range(len(r)):
            k, v = r[i].split(': ', 1)
            e[k] = v
    # Flux
    elif re.match('prompt', p.decode('utf-8')):
        t = re.sub('^prompt.', '', p.decode('utf-8'))
        s = t.split('\n', 2);
        t = re.sub('[^\w\}]$', '', t)
        mg = json.loads(t)
        for k in mg.keys():
            if k.isdigit() and mg[k]["class_type"] == "CLIPTextEncode":
                e['prompt'] = mg[k]["inputs"]["text"]
                del mg[k]["inputs"]["text"]
            else: e[k] = mg[k]
    # Tensor.Art
    elif re.match('generation_data', p.decode('utf-8')):
        t = re.sub('^generation_data.', '', p.decode('utf-8'))
        t = re.sub('[^\w\}]$', '', t)
        mg = json.loads(t)
        for k in mg.keys():
            e[k] = mg[k]
    else:
        fh.close()
        e['_ERROR_'] = 'tEXt: Not a Stable Diffusion Parameters!'
        return e

    # CRC
    t = fh.read(4)
    e['tEXt_CRC'] = int.from_bytes(t)

    fh.close()

    if len(e) == 0:
        e['_ERROR_'] = 'LEN: Not have a length!'
        return e

    return e

######################################################################
# FRONT

def sdgp(path):

    hako = read_exif(path)

    if '_ERROR_' in hako:
        print(hako['_ERROR_'])
        gdialog(hako['_ERROR_'], 'Stable Diffusion Creation Info', 'sd-get-prompt', GTK_MESSAGE_ERROR, GTK_BUTTONS_OK, True)
        return None

    hako.pop("PNG")

    return hako

######################################################################
# MAIN
if __name__ == "__main__":
    print(f"[{__name__}]")
    print(__doc__)

#=====================================================================
# ALL - Make it directly accessible from the top level of the package
__all__ = ["sdgp"]

""" __DATA__

__END__ """
