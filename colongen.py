#!/usr/bin/env python
import urllib2, json, re, sys

STORY_ID=25966

FIMF_API="https://www.fimfiction.net/api/story.php?story={0}"
FIMF_CHAPTERDL="https://www.fimfiction.net/download_chapter.php?chapter={0}"
USER_AGENT="Mozilla/5.0"

TEX_PREAMBLE=\
"""\\documentclass[a4paper,12pt,oneside]{book}
\\usepackage[USenglish]{babel}
\\usepackage[top=1in, bottom=1in, left=1in, right=1in]{geometry}

\\usepackage[T1]{fontenc}
\\usepackage[ansinew,utf8]{inputenc}
\\usepackage{lmodern}

\\usepackage{titletoc}

% Account for > 100 chapters and add ............ in the TOC
\\titlecontents{chapter}[1.5em]{\\addvspace{1pc}\\bfseries}{\contentslabel{2em}}{}
    {\\titlerule*[0.3pc]{.}\contentspage}

"""

def main():

    story_url=FIMF_API.format(STORY_ID)
    story = json.loads(urllib2.urlopen(urllib2.Request(story_url, headers={"User-Agent": USER_AGENT})).read())["story"]

    print "Story URL: {0}".format(story["url"])
    print "Story: {0} - {1}".format(story["title"], story["author"]["name"])

    chapterIncludes=[]
    chapters = story["chapters"]
    for i in range(0, len(chapters)):
        chap = chapters[i]

        sys.stdout.write("  Chapter {0}: {1}...".format(i+1, chap["title"]))
        fileName=write_chapter(i+1, chap)
        sys.stdout.write("{0}\n".format(fileName))

        chapterIncludes.append(fileName)

    fileName = write_latex(story, chapterIncludes)
    print "Output written to {0}".format(fileName)

def write_latex(story, chapterIncludes):
    safeTitle=re.sub("[^0-9a-zA-Z]+", "_", story["title"].lower())

    fileName = "{0}.tex".format(safeTitle)
    with open(fileName, "wb") as f:
        f.write(TEX_PREAMBLE)

        f.write("\\newcommand{{\\fimfTitle}}{{{0}}}\n".format(story["title"]))
        f.write("\\newcommand{{\\fimfAuthor}}{{{0}}}\n".format(story["author"]["name"]))
        f.write("\\newcommand{{\\fimfUrl}}{{{0}}}\n".format(story["url"]))

        f.write("\n\\begin{document}\n\n")

        for chap in chapterIncludes:
            f.write("\\include{{{0}}}\n".format(chap))

        f.write("\n\\end{document}\n")

    return fileName

def tex_escape(line):
    return line.replace("&", "\\&").replace("_", "\_")

def write_chapter(num, chapter):
    safeTitle=re.sub("[^0-9a-zA-Z]+", "_", chapter["title"].lower())
    fileName = "{0:03d}-{1}.tex".format(num, safeTitle)

    chapter_url=FIMF_CHAPTERDL.format(chapter["id"])

    #print chapter_url
    chapterTxt = urllib2.urlopen(urllib2.Request(chapter_url, headers={"User-Agent": USER_AGENT})).read()
    with open(fileName, "wb") as f:

        f.write("\\chapter{{{0}}}\n\n".format(tex_escape(chapter["title"])))
        prevLine = ""
        i = 0
        for line in chapterTxt.split('\n'):
            line = line.strip()
            if(line.startswith("//")):
                continue

            kek = 0
            #print "Line = \"{0}\", prevLine = \"{1}\"".format(line, prevLine)
            if(line == ""):
                if(prevLine == ""):
                    continue

                line = "\\\\\n"
                kek = 1

            line = tex_escape(line)
            if(kek == 1):
                prevLine = ""
            else:
                prevLine = line

            f.write(line)
            f.write('\n')

            i += 1

    return fileName[:-4]

if(__name__ == "__main__"):
    exit(main())