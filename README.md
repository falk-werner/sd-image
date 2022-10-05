# sd-image

Extract and update partitions of a filesystem image file.

## Use case

Sometimes one might need to modify an sd card image, e.g. exchange a file in
the root file system. This might be achieved in two steps

1. determine the position of the desired partition within the image  
   _(`fdisk -l sd.img` might be used for this)_
2. mounting the image as loopback device  
  _(typically something like `mount -o loop,offset=$((49152*512)) sd.img /mnt`)_

This works pretty fine as long as one has the privileges to use the `mount`
command. Unfortunately, this is not always the case. While it is a good idea
to restrict access to `mount` command, there is no security problem with the
use case to change the contents of a file one has already access to.

Tools like [e2tools](https://github.com/e2tools/e2tools) allow to modify
`ext2/3/4` file system images. The only thing missing is a tool to extract
partitions from an image and updates them.

This is were `sd-image.py` comes in handy. To add a local file to an existing
image, the following sequence can be used:

````
sd-image.py extract -i sd.img -p 1 -f rootfs.ext4
e2cp some.file rootfs.ext4:/path/to/some.file
sd-image.py update -i sd.img -p 1 -f rootfs.ext4
````

## Usage

### List paritions

````
sd-image.py list -i sd.img

NR STATUS     TYPE            START       SIZE
----------------------------------------------
0  active     FAT32         8388608   16777216
1  inactive   Linux        25165824  262144000
````

| Argument | Description |
| -------- | ----------- |
| -i image | file name of the sd card image |

### Extract partition form image

````
sd-image.py extract -i sd.img -p 1 -f rootfs.ext4
````

| Argument  | Description |
| --------- | ----------- |
| -i image  | file name of the sd card image |
| -p number | number of the partition to extract (zero-based) |
| -f file   | file name of the parition to extract |

### Update partition of image

````
sd-image.py update -i sd.img -p 1 -f rootfs.ext4
````

| Argument  | Description |
| --------- | ----------- |
| -i image  | file name of the sd card image |
| -p number | number of the partition to extract (zero-based) |
| -f file   | file name of the parition to extract |

## Further information

- [Master boot record](https://en.wikipedia.org/wiki/Master_boot_record)
- [e2tools](https://github.com/e2tools/e2tools)