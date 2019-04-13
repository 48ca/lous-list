# Lou's List CLI
I wrote this because I need to find a spot for STS 4500. I took some of the code I wrote for the GDQ member checker and put it here.

## Usage
### List groups
You can pull the list of valid groups (fields of study) by simply running the script with no arguments.
```shell
python lous.py
```
### List courses in a group
You can pull a list of courses and course details belonging to a group by passing `-g` with a valid group. For example,
```shell
python lous.py -g STS
python lous.py -g CompSci
```
Note: group "CS" stands for "Complete Schedule" (not "Computer Science") which will take a long time to parse.

To filter the output to a single course, you can pass `-c` with a valid course number. For example,
```shell
python lous.py -g STS -c "STS 4500"
```

### Enable notifications of change
If you want the script to notify you (currently via Facebook Messenger) of changes to any section of a particular course, simply pass `-n`. For example,
```shell
python lous.py -g STS -c "STS 4500" -n
```
