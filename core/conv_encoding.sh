#!/bin/bash
# try 'iconv -l' to get the list of supported encodings first.

for file in ./asset/words/*.txt
do
    iconv -f UTF-16 -t UTF-8 "$file" >"$file.new" &&
	mv -f "$file.new" "$file"
done

# after process above, the file encoding would be 'utf-8 with bom', sometime this is not correct. to convert 'utf-8 with bom' to 'utf', use operation below
dos2unix ./asset/words/*.txt
