#!/bin/bash
# try 'iconv -l' to get the list of supported encodings first.

for file in ./words/*.txt
do
    iconv -f UTF-16LE -t UTF-8-MAC "$file" >"$file.new" &&
	mv -f "$file.new" "$file"
done
