import sys, string, re
def run_content_analysis(review_text):
    dictfile = "content_analysis_review_dict.txt"
    text = string.split(review_text)
    a = open(dictfile)
    lines = a.readlines()
    a.close()
    dic = {}
    scores = {}

    # a default category for simple word lists
    current_category = "Default"
    scores[current_category] = 0

    # inhale the dictionary
    for line in lines:
        if line[0:2] == '>>':
            current_category = string.strip( line[2:] )
            scores[current_category] = 0
        else:
            line = line.strip()
            if len(line) > 0:
                pattern = re.compile(line, re.IGNORECASE)
                dic[pattern] = current_category
    # examine the text
    for token in text:
        for pattern in dic.keys():
            if pattern.match( token ):
                categ = dic[pattern]
                scores[categ] = scores[categ] + 1
    x=[]
    for key in sorted(scores.keys()):
        print key, ":", scores[key]
        x.append(scores[key])
    print len(text)
    x.append(len(text))
    print(x[1:])
    return(x[1:])

    
if __name__ == '__main__':
    blah = run_content_analysis('clean. dirty. ugly. broken. flat tire. messy. shiny.')
