# comic-builder

Auxiliary tool for [manga-py](https://github.com/manga-py/manga-py) to organize, merge and export the files in a ebook
format (EPUB or MOBI)

## Dependencies

- [Python 3.6](https://www.python.org/)
- [KCC](https://github.com/ciromattia/kcc) >> To convert the images in ebook format

### Optional dependencies

- KindleGen >> EPUB to MOBI conversion
    * Can be installed running the `kindlegen-installer` command after install the `comic-builder` pip package
    * Can also be found in [AUR](https://aur.archlinux.org/packages/kindlegen/)
      and [here](https://archive.org/details/kindlegen2.9) for manual installation

## Installation

```
pip install comic-builder
kindlegen-installer # to install KindleGen
```

## Modules

Actually there is 4 modules in this repository

- `comic-builder` > Join the comic files into a ebook format
- `kindlegen-installer` > Install the KindleGen binary
- `comic-metadata-inject` > Inject metadata files into the chapters files with the same name
- `comic-metadata-eject` > Extract the chapters metadata files

P.S. The commands `comic-metadata-inject` and `comic-metadata-eject` can be used together to edit some details in the
chapters metadata

## Suggested Workflow

For sites that support chapter and comic metadata (Ex. MangaDex)

```
manga-py --save-chapter-info --save-manga-info [-d|--destination] "COMIC_DOWNLOAD_PATH" [other-options...] URL
comic-builder [other-options...] "COMIC_DOWNLOAD_PATH/COMIC_NAME"
```

For other sites

* Create a metadata file based
  in [this file](https://github.com/eduhoribe/comic-builder/blob/goshujin-sama/samples/comic-metadata-sample.json)

```
manga-py [-d|--destination] "COMIC_DOWNLOAD_PATH" [other-options...] URL
comic-builder --metadata "METADATA_FILE" [other-options...] "COMIC_DOWNLOAD_PATH/COMIC_NAME"
```
