
"""
 a filter search for jobs -> filtering out 'vr' and 'ifd' jobs
    Using an if statement to acheive this -> probably better to use built-in filter


"""

import farm_watch


theNotif = {'msg':'temp', 'toPrint':'temp', 'dict':'temp'}
previousList = None


def main(i, isDone):

    global previousList

    # numJobs not used
    listOne, numJobs = farm_watch.getRenderInfo()
    currentList = initList_1(listOne)
    i = i + 1 #loop counter

    # Just Shell stuff (Verbose output, can remove)
    print ('Iteration: %s -----------------------------------' % i)

    # Getting Second List to compare
    if previousList is None:
        previousList = currentList
        return i

    checkNodes(previousList, currentList, isDone)
    previousList = currentList

    return i


# Creating a list of dictionaries, each dict is one job
def initList_1(oldList):

    returnList = [] 

    for item in oldList:
        temp = initList_2(item)
        returnList.append(temp)

    return returnList


def initList_2(string):

    newDict             = {}
    newList             = string.split()

    newDict["job"]      = newList[1]
    newDict['owner']    = newList[3]
    newDict["id"]       = newList[5]
    newDict["state"]    = newList[7]

    # Since they mean the same thing
    if newDict["state"] == 'Rendered':
        newDict["state"] = 'Done'

    newDict["crashed"]  = newList[9]
    newDict["show"]     = newList[11]
    newDict["shot"]     = newList[13]
    try:
        newDict["software"] = newList[15]
    except:
        pass

    return newDict


# Needed to check done jobs as they disappear on the script
# Checking intersection between 2 lists, which is the job that is done 
# Check Boolean is needed so that both Job Completed and Child Completed 
#   Notif is not printed 
def checkNodes(firstList, secondList, isDone):

    check = 0

    # Filter check for 'ifd' jobs and 'vrscene' jobs
    for firstJob, secondJob in zip(firstList, secondList):
        if ('ifd' not in firstJob['job'] and 'vrscene' not in firstJob['job']):

            if firstJob['id'] == secondJob['id']:
                if firstJob != None or secondJob != None:

                    # Just Shell stuff (Debugging, can remove)
                    print (firstJob['id'] + " "), firstJob['owner'],
                    print firstJob['state'], firstJob['crashed']
                    print (secondJob['id'] + " "),
                    print secondJob['state'], secondJob['crashed']


                    # All dict values are labeled as 'fresh' when the job is freshly submit
                    # Preventing invalid int errors with this if statement
                    if "Fresh" not in firstJob['state'] and "Fresh" not in secondJob['state']:

                        if firstJob['state'] != secondJob['state']:
                            check = checkStateChange(firstJob, secondJob)
                        checkCrashNode(firstJob, secondJob, check)
        

def checkCrashNode(firstJob, secondJob, check):

    if check == 0:
        try:
            if int(firstJob['crashed']) < int(secondJob['crashed']):
                msg = 'Child Crashed!'
                printNotif(msg, secondJob)
        except:
            pass


def checkStateChange(firstJob, secondJob):

    if secondJob['state'] == 'Idle':
        msg = 'Job Idle!'
        printNotif(msg, secondJob)
        return 1

    if secondJob['state'] == 'Done' and int(secondJob['crashed']) > 0:
        msg = 'Job Crashed!'
        printNotif(msg, secondJob)
        return 1

    return 0


def printNotif(msg, secondJob):

    format_str = """*JobID*: {0}  *Show*: {1}  *Shot*: {2}  *Owner*: {3}  *Job Name*: {4}  *Frames Crashed*: {5}"""
  
    toPrint = format_str.format(secondJob['id'], secondJob['show'], 
        secondJob['shot'], secondJob['owner'], secondJob['job'], secondJob['crashed'])

    
    if secondJob.get('software') is not None:
        toPrint = toPrint + '  *Software*: %s' % secondJob['software']


    global theNotif
    theNotif['msg'] = msg
    theNotif['toPrint'] = toPrint
    theNotif['dict'] = secondJob


def initMain(i, isDone):

    global theNotif
    theNotif['msg'] = 'temp'

    # print 'BEFORE:', theNotif['msg']
    i = main(i, isDone)
    # print 'AFTER:', theNotif['msg']

    return theNotif, i, isDone


