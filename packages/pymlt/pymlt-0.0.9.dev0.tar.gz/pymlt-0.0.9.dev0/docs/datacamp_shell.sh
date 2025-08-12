# https://www.datacamp.com/courses/introduction-to-shell-for-data-science

# print working dir
pwd

# create folders
mkdir folder1
mkdir folder2
mkdir folder3

# remove recursive
rm -r folder3

# create files
touch folder1/file1.txt
touch folder1/file2.txt

# copy both files to folder
cp folder1/file1.txt folder1/file2.txt folder2

# rename
mv folder1/file2.txt folder1/file3.txt

# move and rename
mv folder1/file3.txt folder2/

# list
ls -l folder2

# list w/ wildcard
ls -l folder2/*.txt

# list all recursive
ls -R -F folder2

# echo
echo hello world

# echo global var
echo $USER

# echo shell var
FILE=folder1/file1.txt
echo $FILE

# see history
# history

# clear history
# history -c

# write to file
echo line 1 > $FILE

# append to file
echo line 2 >> $FILE
echo line 3 >> $FILE
echo line 4 >> $FILE

# cat (concat) content of both files and print
cat folder1/file1.txt folder2/file1.txt

# print content, space bar = next page; q = quit
# less folder1/file1.txt

# select rows: head, tail
head -n 1 $FILE
tail -n 1 $FILE

# select columns
# -f(ields); -d(elimiter)
# cut -f 2-5,8 -d , values.csv = show columns -fiels 2 till 5 and 8, -delimiter is comma

# manual
# man head

# set = see list of environmenet variables
# set | grep HISTFILESIZE

# print lines containing
grep 1 $FILE
# print line not containing
grep 1 -v $FILE
# print count of lines containing
grep 1 -c $FILE

# word count, -l(ines)
wc -l $FILE

# word count, -w(ords)
wc -w $FILE

# word count, -c(haracters)
wc -c $FILE

# | = pipe
grep line $FILE | grep 3 -v | sort | tail -n 2
less folder1/file1.txt | grep -c "line"

# wilcard
rm folder1/*.txt
# wildcard one character
rm folder2/file?.txt
# wildcard list
rmdir folder[12]

# ctrl-c = end execution
