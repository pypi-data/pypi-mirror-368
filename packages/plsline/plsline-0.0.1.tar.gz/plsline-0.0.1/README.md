# plsline

![Python 3.8|3.9|3.10|3.11|3.12](https://img.shields.io/badge/python-3.8%7C3.9%7C3.10%7C3.11%7C3.12-blue?style=flat-square)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)<br><br>
**PlsLine is a Python library that allows you to add the file you printed, the position of which line it is written, the function name, and the function type.**

```python
--directory\file_name.py-line_number---type------var_name----------------------var
```


## Usage notes
The contents of the print are output, but the contents can be up to three. If it exceeds that, an error will occur. Please note that you may need to divide it into multiple copies and output it. <br>
The first one is used to obtain type, etc.

```python
from plsline import printsimple as prints
#You can also use plsline
prints("one")
prints("one","two")
prints("one","two","three")

#You can do it with print, but if you do the same thing with plsline, you'll get an error
prints("one","two","three", "four")　　#error

#Please split it into two
prints("one","two","three")
prints("four")
```

## Compatibility

Plsline only checks its operation on Windows. <br>
Color does not work properly in the old terminal, in that case, please use plssimple or plsmonochrome. <br>
We have only checked the operation in Japanese environments, and the acquisition of var_name etc. should be performed by encoding='utf-8'
I'm using it. <br>
Python versions 3.8 or later are required to use plsline. <br>

## Requirements
Only the standard library is used.

```python
#List of imports used
from inspect import (
                    currentframe, 
                    getfile,
                    )
import re
import os
from time import sleep

```


<br>


# Installation method
```
python -m pip install plsline
```
<br>

You can test the output of plsline in the terminal by running the following command:


```
python -m plsline
```


# Usage
Examples of using printsimple
<br>
simple does not search for files, outputs lines and types.





```python
##import to make printsimple usable <as> and you can change it to your favorite name, this time it's sinple so I'm going to prints
from plsline import printsimple as prints


##Price setting
view_material = True
price_apple = 500
prints(price_apple,view_print=view_material)

price_orange = 600
prints(price_orange,view_print=view_material) 


#Calculate total price
buy = price_apple + price_orange

#confirmation print
prints(buy)


```
```python
#Output Result
--0008---int--500
--0011---int--600
--0018---int--1100

```

It shows it in lines 8, 11, and 18,




```python
##import to make printcolor available <as>and then you can change it to your favorite name, this time it's color so I'm going to printc
from plsline import printcolor as printc


##Price setting
view_material = True
price_apple = 500
printc(price_apple,view_print=view_material)

price_orange = 600
printc(price_orange,view_print=view_material) 


#Calculate total price
buy = price_apple + price_orange

#confirmation print
printc(buy,color="red")



```



```python

#{directory} {file_name} {type} {line_number} {var_name} {var}
#Output Result
--admake\printcolor.py-0008---int------price_apple----------------------500
--admake\printcolor.py-0011---int------price_orange---------------------600
--admake\printcolor.py-0018---int------buy------------------------------1100

```







#### Argument List
|Argment Name|Type|Default Value|Content|
|---|---|---|---|
|print_normal_content|-||This is the first content of print|
|print_normal_content_sub|-||This is the second content of print|
|print_normal_content_three|-||This is the third content of print|
|view_print |bool|True|print if True|
|line_fast_int|int|2|I put - at the beginning to make it easier to distinguish it from regular print|
|line_end_int|int|0|You can make it stand out by adding - at the end|
|line_int|int|3|The number of - after the filename|
|max_file_int|int|20|Set the maximum number of characters for folders and file names, |
|max_var_name_int|int|30|Set the maximum number of characters for a variable name|
|max_type_int|int|9|Set the maximum number of characters for type|
|sleep_time|int|0|Sets the time to pause when output, in units of seconds|



#### Color arguments Please use name or abbreviation
|Name|Abbreviated name|Default value|Content|
|---|---|---|---|
|color|str|"white"|Change the text color, a list of the compatibility is written separately below. |
|color_back|str|"black"|Change the color of the text background, a list of the corresponding items has been written separately below. |
|colorreset|str|"\033[0m"|Reset color|
|help|bool|False|If the contents is empty and the content is empty, the corresponding color list will be output. printc(help=Ture)|


| Name | Abbreviation | Value | Content Sample |
|--------|----|------------|--------------|
| black     | b    | "\033[30m" | <span style="color:black">black</span> |
| red       | r    | "\033[31m" | <span style="color:red">red</span> |
| green     | g    | "\033[32m" | <span style="color:green">green</span> |
| yellow    | y    | "\033[33m" | <span style="color:gold">yellow</span> |
| blue      | bl   | "\033[34m" | <span style="color:blue">blue</span> |
| magenta   | m    | "\033[35m" | <span style="color:magenta">magenta</span> |
| cyan      | c    | "\033[36m" | <span style="color:cyan">cyan</span> |
| white     | w    | "\033[37m" | <span style="color:gray;background-color:white">white</span> |
| reset     | r    | "\033[0m"  | <span style="color:inherit">reset</span> |

<br>


| Name (Background) | Abbreviation | Value | Content Sample |
|-------------|------|------------|--------------|
| black    | b   | "\033[40m" | <span style="background-color:black;color:white"> black background </span> |
| red     | r   | "\033[41m" | <span style="background-color:red;color:white"> red background </span> |
| green   | g   | "\033[42m" | <span style="background-color:green;color:black"> green background </span> |
| yellow   | y   | "\033[43m" | <span style="background-color:gold;color:black"> yellow background </span> |
| blue     | bl  | "\033[44m" | <span style="background-color:blue;color:white"> blue background </span> |
| magenta  | m   | "\033[45m" | <span style="background-color:magenta;color:white"> magenta background </span> |
| cyan     | c   | "\033[46m" | <span style="background-color:cyan;color:black"> cyan background </span> |
| white    | w   | "\033[47m" | <span style="background-color:white;color:black"> white background </span> |
| reset       | r    | "\033[0m"  | <span style="color:inherit;background-color:inherit">reset</span> |
<br>


## License MIT
Commercial use is fully permitted
Source code can be copied, modified, and distributed.
There is no obligation to publish the source code, so please use it as you like. <br>


