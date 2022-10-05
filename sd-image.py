#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2022 Falk Werner
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse

CHUNK_SIZE = 50 * 1024

filename='/tmp/test/pfc-firmware-21.img'

def get_mbr(filename):
    with open(filename, 'rb') as f:
        mbr = f.read(512)
        if len(mbr) != 512:
            raise Exception('invalid image')
        if 0x55 != mbr[510] or 0xaa != mbr[511]:
            raise Exception('MBR invalid')
        return mbr

def get_partition_typename(code):
    names = {
        0x00: '<empty>',
        0x0c: 'FAT32',
        0x83: 'Linux'
    }
    return names.get(code, '<unknown>')

def get_u32(bytes, offset):
    value = 0
    for i in range(4):
        value = value * 256 + bytes[offset + 3 - i]
    return value

def get_partition_info(mbr, partition):
    if partition < 0 or 3 < partition:
            raise Exception('invalid partition nr')
    offset = 0x01be + (16 * partition)
    status = "active" if mbr[offset] == 0x80 else "inactive" if mbr[offset] == 0x00 else "invalid"
    partition_type = mbr[offset + 0x04]
    start = 512 * get_u32(mbr, offset + 0x08)
    count = 512 * get_u32(mbr, offset + 0x0c)
    return {
        'status': status,
        'type': get_partition_typename(partition_type),
        'start': start,
        'count': count
    }

def get_partition(filename, i):
    mbr = get_mbr(filename)
    return get_partition_info(mbr, i)
            
def list(args):
    print('NR STATUS     TYPE            START       SIZE')
    print('----------------------------------------------')
    mbr = get_mbr(args.image)
    for i in range(4):
        partition = get_partition_info(mbr, i)
        if partition['type'] != '<empty>':
            print(f'{i}  {partition["status"]:10} {partition["type"]:10} {partition["start"]:10} {partition["count"]:10}')

def extract(args):
    partition = get_partition(args.image, args.partition)
    if partition['type'] == '<empty>':
        raise Exception('failed to extract empty partition') 
    with open(args.file, 'wb') as outfile:
        with open(args.image, 'rb') as imagefile:
            imagefile.seek(partition['start'])
            remaining = partition['count']
            while remaining > 0:
                chunk = imagefile.read(min(remaining, CHUNK_SIZE))
                outfile.write(chunk)
                remaining -= len(chunk)

def update(args):
    partition = get_partition(args.image, args.partition)
    if partition['type'] == '<empty>':
        raise Exception('failed to update empty partition') 
    with open(args.file, 'rb') as partfile:
        with open(args.image, 'rb+') as imagefile:
            imagefile.seek(partition['start'])
            remaining = partition['count']
            while remaining > 0:
                chunk = partfile.read(min(remaining, CHUNK_SIZE))
                imagefile.write(chunk)
                remaining -= len(chunk)

def main():
    parser = argparse.ArgumentParser()
    subcommands = parser.add_subparsers(title='commands', required=True, dest='command')

    listparser = subcommands.add_parser("list", help='list partitions in image')
    listparser.add_argument('-i', '--image', required=True, type=str, help='name of the .img file')
    listparser.set_defaults(func=list)

    extractparser = subcommands.add_parser("extract", help='extract a partition form an image')
    extractparser.add_argument('-i', '--image', required=True, type=str, help='name of the .img file')
    extractparser.add_argument('-p', '--partition', required=False, type=int, default=0, help='number of the partition to extract (default: 0)')
    extractparser.add_argument('-f', '--file', required=False, default='part.bin', help='file name of extracted partition (default: part.bin)')
    extractparser.set_defaults(func=extract)

    updateparser = subcommands.add_parser("update", help='updates a partition of an image')
    updateparser.add_argument('-i', '--image', required=True, type=str, help='name of the .img file')
    updateparser.add_argument('-p', '--partition', required=False, type=int, default=0, help='number of the partition to update (default: 0)')
    updateparser.add_argument('-f', '--file', required=False, default='part.bin', help='file name of partition update (default: part.bin)')
    updateparser.set_defaults(func=update)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
