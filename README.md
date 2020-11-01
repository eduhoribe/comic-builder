# manga-py-assembler

Auxiliary tool for [manga-py](https://github.com/manga-py/manga-py) to organize, merge and export the files in a ebook
format

## Dependencies

- [kcc](https://github.com/ciromattia/kcc) >> To convert the images in ebook format

### Optional dependencies

- [calibre](https://github.com/kovidgoyal/calibre) >> For metadata edit

## Suggested Workflow

```
manga-py --destination "$COMIC_PATH" --save-current-chapter-info --save-manga-info [other-options...] URL
manga-py-assembler [other-options...] --comic-path "$COMIC_PATH"
```
