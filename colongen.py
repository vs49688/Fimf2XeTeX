#!/usr/bin/env python
import urllib2
import json
import re
import sys
import os
import inspect
import codecs
import unicodedata

from sys import stderr as stderr, stdout as stdout

# realpath() will make your script run, even if you symlink it :)
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

# use this if you want to include modules from a subfolder
cmd_subfolder = os.path.realpath(
    os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "libs")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

FIMF_API = "https://www.fimfiction.net/api/story.php?story={0}"
FIMF_CHAPTERDL = "https://www.fimfiction.net/download_chapter.php?chapter={0}"
FIMF_CHAPTERDL_HTML = "https://www.fimfiction.net/download_chapter.php?chapter={0}&html"

USER_AGENT = "Mozilla/5.0"

TEX_PREAMBLE_1 = \
    u"""\\documentclass[a4paper,12pt]{memoir}
\\usepackage{ifxetex}
\\RequireXeTeX

\\usepackage[top=1in, bottom=1in, left=1in, right=1in]{geometry}
\\usepackage[USenglish]{babel}

\\usepackage{fontspec}
\\setmainfont{Garamond}

% Convert non-breaking spaces into normal spaces
\\usepackage{newunicodechar}
\\newunicodechar{\u00a0}{ }

\\PassOptionsToPackage{hyphens}{url}
\\usepackage[linktoc=all]{hyperref}
\\hypersetup{
    colorlinks,
    citecolor=black,
    filecolor=black,
    linkcolor=black,
    urlcolor=black
}

\\usepackage[autostyle]{csquotes}

\\chapterstyle{dash}

% Account for > 100 chapters and add ............ in the TOC
\\renewcommand*{\\cftchapterdotsep}{\\cftdotsep}
\\cftsetindents{chapter}{1em}{3em}
"""

TEX_PREAMBLE_2 = \
    u"""\\makeevenhead{headings}{\\thepage}{\\MakeUppercase{\\fimfAuthor}}{}
\\makeoddhead{headings}{}{\\MakeUppercase{\\fimfTitle}}{\\thepage}

\\makeevenfoot{plain}{}{}{}
\\makeoddfoot{plain}{}{}{}

\\title{\\fimfTitle}
\\author{\\fimfAuthor}
\\date{}
"""

TEX_BACKTITLE = \
    u"""{\\setlength{\\parindent}{0cm}

This is a work of fiction. All of the characters, organisation, and events portrayed in this work are either products of the author's imagination or are used fictitiously.
\\\\

\MakeUppercase{\\fimfTitle}, by \MakeUppercase{\\fimfAuthor}
\\\\

My Little Pony: Friendship is Magic\\textsuperscript{\\textregistered} is a registered trademark of Hasbro, Inc.
\\\\

The author is not affiliated with Hasbro.
\\\\

Original Story URL:
\\\\
\\url{\\fimfUrl}

}
"""


def usage():
    stderr.write("Usage: {0} <storyID>\n".format(os.path.basename(__file__)))


def main():
    if len(sys.argv) != 2:
        usage()
        return 1

    try:
        story_id = int(sys.argv[1])
    except ValueError:
        usage()
        return 1

    story_url = FIMF_API.format(story_id)

    story = json.loads(urllib2.urlopen(urllib2.Request(story_url, headers={"User-Agent": USER_AGENT})).read())["story"]

    print "Story URL: {0}".format(story["url"])
    print "Story: {0} - {1}".format(story["title"], story["author"]["name"])

    chapter_includes = []
    chapters = story["chapters"]
    for i in range(0, len(chapters)):
        chap = chapters[i]

        chapName = ''.join((c for c in unicodedata.normalize('NFD', chap["title"]) if unicodedata.category(c) != 'Mn'))
        stdout.write("  Chapter {0}: {1}...".format(i + 1, chapName))
        file_name = write_chapter_html(i + 1, chap)
        # file_name = write_chapter_txt(i + 1, chap)
        stdout.write("{0}\n".format(file_name))

        chapter_includes.append(file_name)

    file_name = write_latex(story, chapter_includes)
    print "Output written to {0}".format(file_name)


def write_latex(story, chapter_includes):
    safe_title = re.sub("[^0-9a-zA-Z]+", "_", story["title"].lower())

    with codecs.open("backtitle.tex", "wb", encoding="utf-8") as f:
        f.write(TEX_BACKTITLE)

    file_name = "{0}.tex".format(safe_title)
    with codecs.open(file_name, "wb", encoding="utf-8") as f:
        f.write(TEX_PREAMBLE_1)
        f.write("\n")

        f.write("\\newcommand{{\\fimfTitle}}{{{0}}}\n".format(story["title"]))
        f.write("\\newcommand{{\\fimfAuthor}}{{{0}}}\n".format(story["author"]["name"]))
        f.write("\\newcommand{{\\fimfUrl}}{{{0}}}\n".format(story["url"]))
        f.write("\\newcommand{{\\fimfStoryID}}{{{0}}}\n".format(story["id"]))
        f.write("\n")

        f.write(TEX_PREAMBLE_2)
        f.write("\n")

        f.write("\n\\begin{document}\n\n")
        f.write("\t\\pagestyle{empty}\n\n")

        f.write("\t\\frontmatter\n\n")

        f.write("\t\\maketitle\n")
        f.write("\t\\clearpage\n\n")

        f.write("\t\\include{backtitle}\n")
        f.write("\t\\clearpage\n\n")

        f.write("\t\\tableofcontents*\n")
        f.write("\t\\clearpage\n\n")

        f.write("\t\\pagestyle{headings}\n")
        f.write("\t\\mainmatter\n\n")

        for chap in chapter_includes:
            f.write("\t\\include{{{0}}}\n".format(chap))

        f.write("\n\\end{document}\n")

    return file_name


def tex_escape(line):
    # For the love of all things holy, do the \\ excape first...
    line = line.replace("\\", "\\textbackslash ")
    line = line.replace("&", "\\&")
    line = line.replace("_", "\_")
    line = line.replace("#", "\\#")
    line = line.replace("$", "\\$")
    line = line.replace("%", "\\%")
    line = line.replace("{", "\\{")
    line = line.replace("}", "\\}")
    line = line.replace(u"~", u"\\textasciitilde ")
    line = line.replace(u"^", u"\\textasciicircum ")

    return line


def write_tag(f, tag):
    from libs.bs4 import NavigableString as NavigableString

    if type(tag) == NavigableString:
        f.write(tex_escape(tag))
        return

    if tag.name in [u'b', u'strong']:
        # f.write("\\textbf{")
        f.write("{\\bfseries ")
    elif tag.name in [u'i', u'em']:
        # f.write("\\textit{")
        f.write("{\\itshape ")
    elif tag.name in [u"center"]:
        f.write("\n\\begin{center}\n")
    elif tag.name in [u"blockquote"]:
        f.write("\n\\blockquote{")

    for text in tag.contents:
        write_tag(f, text)

    if tag.name in [u'b', u'strong']:
        f.write("}")
    elif tag.name in [u'i', u'em']:
        f.write("}")
    elif tag.name in [u"center"]:
        f.write("\n\\end{center}\n")
    elif tag.name in [u"blockquote"]:
        f.write("}\n")
    elif tag.name in [u'p']:
        f.write("\n\n")


def write_chapter_html(num, chapter):
    from libs.bs4 import BeautifulSoup as BeautifulSoup
    from libs.bs4.builder import _html5lib as html5lib

    safe_title = re.sub("[^0-9a-zA-Z]+", "_", chapter["title"].lower())
    file_name = "{0:03d}-{1}.tex".format(num, safe_title)

    chapter_url = FIMF_CHAPTERDL_HTML.format(chapter["id"])

    chapter_html = urllib2.urlopen(urllib2.Request(chapter_url, headers={"User-Agent": USER_AGENT})).read()

    # Use BeautifulSoup to parse it. html5lib is used because we want valid HTML
    bs = BeautifulSoup(chapter_html, ["html5lib"], html5lib.HTML5TreeBuilder())

    with codecs.open(file_name, "wb", encoding="utf-8") as f:
        f.write(u"\\chapter{{{0}}}\n\n".format(tex_escape(chapter["title"])))

        current_tag = bs.find("p")

        while current_tag:
            write_tag(f, current_tag)
            current_tag = current_tag.next_sibling

    return file_name[:-4]


def write_chapter_txt(num, chapter):
    safe_title = re.sub("[^0-9a-zA-Z]+", "_", chapter["title"].lower())
    file_name = "{0:03d}-{1}.tex".format(num, safe_title)

    chapter_url = FIMF_CHAPTERDL.format(chapter["id"])

    chapter_txt = urllib2.urlopen(urllib2.Request(chapter_url, headers={"User-Agent": USER_AGENT})).read()
    with open(file_name, "wb") as f:

        f.write("\\chapter{{{0}}}\n\n".format(tex_escape(chapter["title"])))
        prev_line = ""
        i = 0
        for line in chapter_txt.split('\n'):
            line = line.strip()
            if line.startswith("//"):
                continue

            kek = 0
            if line == "":
                if prev_line == "":
                    continue

                line = "\n"
                kek = 1

            line = tex_escape(line)
            if kek == 1:
                prev_line = ""
            else:
                prev_line = line

            f.write(line)
            f.write('\n')

            i += 1

    return file_name[:-4]


if __name__ == "__main__":
    exit(main())
