# Copyright (C) 2012 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Emit extra commands needed for Group during OTA installation
(installing the bootloader)."""

import common

def FullOTA_InstallEnd(info):
  try:
    bootloader_bin = info.input_zip.read("RADIO/bootloader.raw")
  except KeyError:
    print "no bootloader.raw in target_files; skipping install"
  else:
    WriteBootloader(info, bootloader_bin)

  try:
    radio_img = info.input_zip.read("RADIO/radio.img")
  except KeyError:
    print "no radio.img in target_files; skipping install"
  else:
    WriteRadio(info, radio_img)


def IncrementalOTA_InstallEnd(info):
  try:
    target_bootloader_bin = info.target_zip.read("RADIO/bootloader.raw")
    try:
      source_bootloader_bin = info.source_zip.read("RADIO/bootloader.raw")
    except KeyError:
      source_bootloader_bin = None

    if source_bootloader_bin == target_bootloader_bin:
      print "bootloader unchanged; skipping"
    else:
      WriteBootloader(info, target_bootloader_bin)
  except KeyError:
    print "no bootloader.raw in target target_files; skipping install"

  try:
    target_radio_img = info.target_zip.read("RADIO/radio.img")
    try:
      source_radio_img = info.source_zip.read("RADIO/radio.img")
    except KeyError:
      source_radio_img = None

    if source_radio_img == target_radio_img:
      print "radio image unchanged; skipping"
    else:
      WriteRadio(info, target_radio_img)
  except KeyError:
    print "no radio.img in target_files; skipping install"


def WriteBootloader(info, bootloader_bin):
  common.ZipWriteStr(info.output_zip, "bootloader.raw", bootloader_bin)
  fstab = info.info_dict["fstab"]

  info.script.Print("Writing bootloader...")

  info.script.AppendExtra('''package_extract_file("bootloader.raw", "%s");''' %
                          (fstab["/staging"].device,))

def WriteRadio(info, radio_img):
  common.ZipWriteStr(info.output_zip, "radio.img", radio_img)
  fstab = info.info_dict["fstab"]

  info.script.Print("Writing radio...")
  info.script.AppendExtra("""assert(package_extract_file("radio.img", "%s"),
                          mount("ext4", "EMMC", "%s", "/radio"),
                          bach.update_modem("/radio/SAM_6260_ALL.fls"));""" %
                          (fstab["/radio"].device, fstab["/radio"].device))
