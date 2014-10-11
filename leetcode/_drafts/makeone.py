#coding=utf-8

def parsefile(filename):
    f = open(filename)
    lines = f.readlines()
    result=[]
    needchange = False
    for i in range(10, len(lines)):
        line = lines[i]
        if (line.startswith("###")):
            line = '#'+line[:3]+' '+line[4:]
        if (line.startswith('```cpp')) and (len(lines[i-1]) > 2):
            needchange = True
            result.append('\n')
        result.append(line)
    result.append('\n')
    f.close()
    if(needchange):
        output = open(filename, 'w')
        output.writelines(lines[:10])
        output.writelines(result)
        output.close()
    return result

def parseAll(filename):
    f = open(filename)
    lines = f.readlines()
    result=[]
    i = 0
    for line in lines[9:]:
        if(line.startswith('###')):
            line = line[1:]
        if(line.find('题解') == -1):
            result.append(line)
            continue
        s = line.find('(./')   
        e = line.find('.html')
        title = line[s+3:e]
        onefile = title +'.md'
        title = ' '.join(title.split('-'))
        #print title, onefile; exit();    
        if (onefile == 'Pow(x,-n).md'):
            onefile = 'powx-n.md'
        elif (onefile == 'Sqrt(x).md'):
            onefile = 'sqrtx.md'
        elif (onefile == 'String-to-Integer-(atoi).md'):
            onefile = 'string-to-integer-atoi.md'
        elif (onefile == 'Implement-strStr().md'):
            onefile = 'implement-strstr.md'
        elif (onefile == "Pascal's-Triangle.md"):
            onefile = 'pascals-triangle.md'
        elif (onefile == "Pascal's-Triangle-II.md"):
            onefile = 'pascals-triangle-ii.md'
        onefilecontent = parsefile(onefile)
        result.append('### ' + title + '\n\n')
        result += onefilecontent
        i += 1
        #if(i == 5):
        #    break
    output = open('makeone.out.md', 'w')
    output.writelines(result)
    output.close()

parseAll('leetcode-summary.md')
#parsefile('decode-ways.md')
