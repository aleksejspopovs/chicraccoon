# Sharp electronic notebook backup format

`.bkup` files are essentially tar archives. Wikipedia has a [good description](https://en.wikipedia.org/wiki/Tar_(computing)) of how tar archives work.

Here are some things specific to Sharp backups:

- the files produced by the notebooks do not use the UStar format, and never contain symbolic links.

- mode is always `0400666` for directories and `0100666` for files. Owner/group information is always all-zero.

- last modification time doesn't appear to be Unix time, but it does increase when files are changed.

- the paths incorrectly use `\`, the backwards slash, as a separator. This will confuse the `tar` command-line utility.

- whereas tar files are normally terminated with two 512-bytes headers filled entirely with `00` bytes, `.bkup` files are terminated with one 512-byte header filled with `00` bytes, and another that starts with `75 78 46`, then contains two more bytes (probably a checksum), and then 507 `00` bytes.

- the first 1024 bytes of the file appear to contain some enote-specific information (such as the model number and firmware version of the device that produced the backup). Although a lenient tar parser (one that only looks for the file size and rounds it up to a multiple 512 bytes) can likely skip this, it's probably not meant to be interpreted as a part of a tar file.
