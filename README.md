# comic-builder

Auxiliary tool for [manga-py](https://github.com/manga-py/manga-py) to organize, merge and export the files in a ebook
format (EPUB or MOBI)

## Dependencies

- [Python 3](https://www.python.org/)
- [kcc](https://github.com/ciromattia/kcc) >> To convert the images in ebook format

### Optional dependencies

- KindleGen >> EPUB to MOBI conversion
    * Can be found in [AUR](https://aur.archlinux.org/packages/kindlegen/)
      and [here](https://archive.org/details/kindlegen2.9)

## Suggested Workflow

For sites that support chapter and comic metadata (Ex. MangaDex)

```
manga-py --save-chapter-info --save-manga-info [-d|--destination] "COMIC_DOWNLOAD_PATH" [other-options...] URL
python MANGA_PY_ASSEMBLER_PATH/main.py [other-options...] --comic-path "COMIC_DOWNLOAD_PATH/COMIC_NAME"
```

For other sites

* Create a metadata file based
  in [this file](https://github.com/eduhoribe/comic-builder/blob/main/samples/comic-metadata-sample.json)

```
manga-py [-d|--destination] "COMIC_DOWNLOAD_PATH" [other-options...] URL
python MANGA_PY_ASSEMBLER_PATH/main.py --metadata "METADATA_FILE" [other-options...] --comic-path "COMIC_DOWNLOAD_PATH/COMIC_NAME"
```
