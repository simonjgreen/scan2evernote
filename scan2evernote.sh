#!/bin/bash

BASEPATH=$(mktemp -d)

scanimage \
    --device-name=pixma:04A9176B_319DC7 \
    --source="ADF Duplex" \
    --format=tiff \
    --batch="$BASEPATH/%d.tiff" \
    --batch-start=101 \
    --resolution=300

for file in $BASEPATH/*.tiff
do
    PAGE=$(basename $file .tiff)
    echo -n "Page $PAGE ($file): "

    REM=$(( $PAGE % 2 ))
    if [ $REM -eq 0 ]
    then
        echo "Flipping, Trimming"
        convert $file -rotate 180 -trim $file
    else
        echo "Trimming"
        convert $file -trim $file
    fi
done

echo "Performing OCR and creating PDFs"
for file in $BASEPATH/*.tiff
do
    PAGE=$(basename $file .tiff)

    tesseract $file $BASEPATH/$PAGE -l eng hocr
    hocr2pdf -i $file -s -o $BASEPATH/$PAGE.pdf < $BASEPATH/$PAGE.hocr
done

FILEORDER=$(find $BASEPATH -maxdepth 1 -type f -name "*.pdf" | sort -n | paste -sd\ )

echo "Combining to single PDF and compressing ($BASEPATH/scan.pdf)"
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook -sOutputFile=$BASEPATH/scan.pdf $FILEORDER

echo "Uploading to Evernote"
/usr/bin/python send2evernote.py $BASEPATH/scan.pdf

echo "Cleaning up temporary files"
rm -rf $BASEPATH
