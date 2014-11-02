#coding=utf-8
def addlinkkey(filename):
    f = open(filename)
    lines = f.readlines()
    i=0
    result=[]
    for line in lines:
        if(line.find('题解') == -1):
            result.append(line)
            continue
        s = line.find('[')   
        e = line.find('题解')
        title='-'.join(line[s+1:e].split(' '))
        title = title[:-1]+'.html'
        newline = line[:-2]+title+')\n'
        result.append(newline)
    f.close()
    #print result
    output = open(filename+'.out.md', 'w')
    output.writelines(result)
    output.close()

addlinkkey('leetcode-summary.md')
