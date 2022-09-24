# metafolder
Tool for handling files, folders, zips and custom actions

### Quick Tutorial:
`help` - prints all available commands  

`get file.txt as myFile` - saves file path with name  
`put myFile in /usr/folder` - puts file with name in path

`get /usr/folder1 as myFolder1` - saves folder path with name  
`get /usr/folder2 as myFolder2`  
`put myFile in myFolder1`  
`put myFile in myFolder2`  

### config.json
Contains configuration properties which changes program's default behaviour

### cache.json
Contains all current files, dirs and zips mapping

### entrypoints to run the program:
* `bin/metafolder.bat` (windows)
* `bin/metafolder.sh` (linux)

### features list:
- paths' saving with aliases
- shorthands support for commands: help, list, map, get, put