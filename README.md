# FIMF2XeTeX

FIMF2XeTeX is a story scraper www.fimfiction.net, which will output stories in valid XeTeX code for later typesetting.

Due to the seemingly infinite amount of formatting styles used on FIMFiction, FIMF2XeTeX will not always output perfect code, but it will provide an extremely solid foundation, which can then be built upon and modified.

### Usage
```
$ /path/to/fimf2xetex.py <storyID>
```
FIMF2XeTeX will output a bunch of _*.tex_ filex in the current working directory and display the name of the master build file.
```
$ xelatex master_build_file.tex
```

* ```<storyID>``` may be extracted from URLs of the following form: ```https://www.fimfiction.net/story/<storyID>/```
* The above ```xelatex``` command will have to be run up to three times, but you should already know that if you know TeX/LaTeX/XeTeX.


### Installation
Simply clone the repository to a folder:```git clone https://github.com/vs49688/Fimf2XeTeX```


### Requirements
Any Python 2.7 implementation should suffice, however this has only been tested with CPython


### Version
1.0-release

### License
[BSD 3-Clause License](https://opensource.org/licenses/BSD-3-Clause) (See the **LICENSE** file.)