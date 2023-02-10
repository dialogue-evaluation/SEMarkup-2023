#!/bin/bash

wget -O ru_syntagrus-ud-train-a.conllu https://raw.githubusercontent.com/UniversalDependencies/UD_Russian-SynTagRus/master/ru_syntagrus-ud-train-a.conllu
wget -O ru_syntagrus-ud-train-b.conllu https://raw.githubusercontent.com/UniversalDependencies/UD_Russian-SynTagRus/master/ru_syntagrus-ud-train-b.conllu
wget -O ru_syntagrus-ud-train-c.conllu https://raw.githubusercontent.com/UniversalDependencies/UD_Russian-SynTagRus/master/ru_syntagrus-ud-train-c.conllu
wget -O ru_syntagrus-ud-dev.conllu https://raw.githubusercontent.com/UniversalDependencies/UD_Russian-SynTagRus/master/ru_syntagrus-ud-dev.conllu
wget -O ru_syntagrus-ud-test.conllu https://raw.githubusercontent.com/UniversalDependencies/UD_Russian-SynTagRus/master/ru_syntagrus-ud-test.conllu

cat ru_syntagrus-ud-train-a.conllu ru_syntagrus-ud-train-b.conllu ru_syntagrus-ud-train-c.conllu ru_syntagrus-ud-dev.conllu ru_syntagrus-ud-test.conllu > ru_syntagrus.conllu

rm ru_syntagrus-ud-train-a.conllu
rm ru_syntagrus-ud-train-b.conllu
rm ru_syntagrus-ud-train-c.conllu
rm ru_syntagrus-ud-dev.conllu
rm ru_syntagrus-ud-test.conllu

echo "ru_syntagrus.conllu is built"
