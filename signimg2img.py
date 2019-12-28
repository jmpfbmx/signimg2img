#!/usr/bin/env python3

         #====================================================#
         #              FILE: signimg2img.py                  #
         #              AUTHOR: R0rt1z2                       #
         #====================================================#

#   Android signed images extractor. To use the script:
#   "python3 signimg2img -b/-r/-s" or -i image_name to unpack any other image.
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#   All copyrights of simg2img goes for anestisb.

from argparse import ArgumentParser
from subprocess import Popen, PIPE, DEVNULL, STDOUT, check_call, call
from sys import version_info as __pyver__
import struct
import sys
import glob
import time
import os

# Defines section
__version__ = '1.2'
__pyver__ = str(__pyver__[0])

BFBF_HDR = 1178748482

# Check for platform
if sys.platform.startswith("linux"):
    print("")
else:
    print("Unsopported platform!")
    exit()

# Check for python version
if __pyver__[0] == "3":
    time.sleep(0.1)
else:
    print(f'Invalid Python Version.. You need python 3.X to use this script. Your Version is: {__pyver__}\n')
    exit()

def display(s):
    text = f"[signimg2img-log] {s}"
    print(text)

def shCommand(sh_command, stderr):
    if stderr == "out":
       call(sh_command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    else:
       call(sh_command, shell=True)

# display and shCommand should be the first functions. If not, will cause errors.

def grep_filetype(type):
    typefiles = str(glob.glob(type))
    typefiles = typefiles.replace("[", "").replace("'", "").replace("]", "").replace(",", "")
    return typefiles # I don't really know if this is needed...

def delete_header(image, outimage):
    display("Deleting the header...")
    time.sleep(0.5)
    shCommand(f'dd if={image} of={outimage} bs=$((0x4040)) skip=1', "out")

def check_header(image, ext):
    if ext == "img":
        images = str(grep_filetype("*.img"))
    elif ext == "bin":
        images = str(grep_filetype("*.bin"))
    if image in images:
      with open(image, "rb") as binary_file:
         data = binary_file.read(4)
         img_hdr = struct.unpack('<I', data)
      if img_hdr == BFBF_HDR
         display(f"Detected BFBF header: {header}")
      else:
         display("This is not a signed image!!\n")
         exit()
    else:
      display(f"Cannot find {image}!\n")
      exit()

def check_simg2img():
    display("Checking if simg2img is installed...")
    simg2img = Popen('apt list --installed | grep simg2img', shell=True, bufsize=64, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True).stdout.read().strip().decode('utf-8')
    if "simg2img" in simg2img:
       display("simg2img is installed... Continue")
    else:
       display("simg2img is not installed, install it for unpack the system!\n")
       exit()

def unpack_system():
      check_simg2img()
      oldfiles()
      delete_header("system-sign.img", "system.img" )
      display("Converting to ext4 image...")
      shCommand("simg2img system.img system.ext4", "out")
      display("Unpacking system image...")
      os.mkdir("system_out")
      shCommand("sudo mount -r -t ext4 -o loop system.ext4 /mnt", "noout")
      shCommand("sudo cp -r /mnt/* system_out", "noout")
      shCommand("sudo umount /mnt", "noout")
      shCommand("sudo chown -R $USER:$USER system_out", "noout")
      display("system-sign.img extracted at >>system_out<<\n")
      exit()

def oldfiles():
       display("Removing old files if they're present...")
       shCommand("rm boot.img && rm recovery.img && system.img && rm system.ext4 && rm -rf system_out && rm *.unpack", "out")

def help():
         display("USAGE: signimg2img.py -b/-r/-s (To unpack any other image: -i image_name):\n")
         print("     -b: Convert Android Signed Boot Image.")
         print("     -r: Convert Android Signed Recovery Image.")
         print("     -s: Convert & extract Android Signed System Image.")
         print("     -i: Convert any other image (i.e: cache-sign, lk-sign, etc).")
         print("")
         exit()

def main():
    print('signimg2img binary - version: {}\n'.format(__version__))
    if len(sys.argv) == 1:
         display("Expected more arguments.\n")
         help()
         exit()
    elif sys.argv[1] == "-h":
         help()      
    elif sys.argv[1] == "-s":
      display("Selected: Unpack system-sign.img")
      check_header("system-sign.img", "img")
      unpack_system()
    elif sys.argv[1] == "-b":
      display("Selected Image to unpack: boot-sign.img")
      check_header("boot-sign.img", "img")
      oldfiles()
      delete_header("boot-sign.img", "boot.img")
      display("Done, image extracted as boot.img\n")
    elif sys.argv[1] == "-r":
      display("Selected: Unpack recovery-sign.img")
      check_header("recovery-sign.img", "img")
      oldfiles()
      delete_header("recovery-sign.img", "recovery.img")
      display("Done, image extracted as recovery.img\n")
    elif sys.argv[1] == "-i":
      image = sys.argv[2]
      display(f"Selected: Unpack {image}")
      if "bin" in sys.argv[2]:
         imgis = "bin"
      elif "img" in sys.argv[2]:
         imgis = "img"
      check_header(sys.argv[2], imgis)
      oldfiles()
      delete_header(f"{image}", f"{image}.unpack")
      display(f"Done, image extracted as {image}.unpack\n")
    else:
      display(f"Invalid option: {sys.argv[1]}\n")
      help()
      exit()

if __name__ == "__main__":
   main()
