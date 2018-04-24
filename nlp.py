import sys, string, re
def run_content_analysis(review_text,numbers):
    # The input order is [average,num_reviews,clean,cosmetic,reliable]
    text = string.split(review_text)
    dictionaryfile = "content_analysis_review_dict.txt"

    a = open(dictionaryfile)
    lines = a.readlines()
    a.close()

    dict = {}
    score = {}

    curr = "Default"
    score[curr] = 0

    for line in lines:
        if line[0:2] == '>>':
            curr= string.strip(line[2:])
            score[curr] = 0
        else:
            line = line.strip()
            print(line)
            if len(line) > 0:
                pat = re.compile(line, re.IGNORECASE)
                dict[pat] = curr

    for tokens in text:
        for patterns in dict.keys():
            if patterns.match(tokens):
                cat = dict[patterns]
                score[cat] = score[cat] + 1
    x=[]
    for key in sorted(score.keys()):
        print key, ":", score[key]
        x.append(score[key])
    print(len(text))

    x[0]=numbers[1]+1
    sum_of_blah=x[1]+x[2]+x[3]
    x[1]=float(x[0]-1)/float(x[0])*(float(x[1])/float(3*sum_of_blah+0.1*len(text)))
    print x[1]
    if x[1]>=0.02:
        x[1]=numbers[2]-1
    elif x[1]==0.0:
        x[1]=numbers[2]+1
    else:
        x[1]=numbers[2]

    x[2]=float(x[0]-1)/float(x[0])*(float(x[2])/float(3*sum_of_blah+0.1*len(text)))
    if x[2]>=0.02:
        x[2]=numbers[3]+1
    elif x[2]==0.0:
        x[2]=numbers[3]

    x[3]=float(x[0]-1)/float(x[0])* (float(x[3])/float(3*sum_of_blah+0.1*len(text)))
    if x[3]>=0.01:
        x[3]=numbers[4]-1
    elif x[3]==0.0:
        x[3]=numbers[4]+1
    else:
        x[3]=numbers[4]

    new_aggregate=float(x[1]+x[2]+x[3])/float(3)
    print(new_aggregate)
    x.insert(0,new_aggregate)
    print(x)
    # The return order is [average,num_reviews,clean,cosmetic,reliable]
    return(x)


if __name__ == '__main__':
    blah = run_content_analysis('This was a terrible car. It broke down all the time, and was dirty and smelly',[7,12,5,5,5])
