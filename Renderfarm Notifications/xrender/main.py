
"""

Using a filter search for jobs -> filtering out 'vr' and 'ifd' jobs
    Using an if statement to acheive this -> probably better to use built-in filter


"""

import farm_watch

#Using global Dicts/Vars
newSettings = {'toggleDone':False, 'toggleKilled': False, 'toggleCrash': False,
    'toggleJobComplete':False, 'toggleJobIdle':False, 'popupTime': 20} 

theNotif = {'msg':'temp', 'toPrint':'temp', 'dict':'temp'}
previousList = None


def main(i, isDone, user):

    global previousList

    # numJobs not used
    listOne, numJobs = farm_watch.getRenderInfo(user)
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

    newDict = {}
    newList = string.split()

    newDict["job"] = newList[1]
    newDict["id"] = newList[3]
    newDict["state"] = newList[5]

    # Since they mean the same thing
    if newDict["state"] == 'Rendered':
        newDict["state"] = 'Done'

    newDict["crashed"] = newList[7]
    newDict["killed"] = newList[9]
    newDict["done"] = newList[11]
    newDict["show"] = newList[13]
    newDict["shot"] = newList[15]
    newDict["queued"] = newList[17]
    newDict["running"] = newList[19]

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
                    print (firstJob['id'] + " "),
                    print firstJob['state']
                    print (secondJob['id'] + " "),
                    print secondJob['state']

                    # All dict values are labeled as 'fresh' when the job is freshly submit
                    # Preventing invalid int errors with this if statement
                    if "Fresh" not in firstJob['state'] and "Fresh" not in secondJob['state']:

                        if firstJob['state'] != secondJob['state']:
                            check = checkStateChange(firstJob, secondJob)
                        if newSettings['toggleDone'] == False:
                            checkDoneNode(firstJob, secondJob, isDone, check)
                        if newSettings['toggleKilled'] == False:
                            checkKillNode(firstJob, secondJob)
                        if newSettings['toggleCrash'] == False:
                            checkCrashNode(firstJob, secondJob)
        

# Need the try and except blocks in each function because job states are 
# not listed as integers when they are freshly submitted
def checkDoneNode(firstJob, secondJob, isDone, check):

    # Only print the first time child pid is completed and shouldnt print
    # if the child pid is only one (since the job would be completed)
    if secondJob['id'] not in isDone and check != 1:

        try:
            if int(firstJob['done']) < int(secondJob['done']):
                msg = 'First Frame(s) Completed!'
                isDone.append(secondJob['id'])
                printNotif(msg, secondJob)
        except:
            pass


def checkKillNode(firstJob, secondJob):

    try:
        if int(firstJob['killed']) < int(secondJob['killed']):
            msg = 'Child Pid Killed!'
            printNotif(msg, secondJob)
    except:
        pass


def checkCrashNode(firstJob, secondJob):

    try:
        if int(firstJob['crashed']) < int(secondJob['crashed']):
            msg = 'Child Pid Crashed!'
            printNotif(msg, secondJob)
    except:
        pass


def checkStateChange(firstJob, secondJob):

    if secondJob['state'] == 'Done':
        if newSettings['toggleJobComplete'] == False:
            msg = 'Job Completed!'
            printNotif(msg, secondJob)
            return 1

    elif secondJob['state'] == 'Idle':
        if newSettings['toggleJobIdle'] == False:
            msg = 'Job now Idle!'
            printNotif(msg, secondJob)
            return 1

    return 0


def printNotif(msg, secondJob):

    format_str = """
Show: {0}
Shot: {1}
Job Name: {2}
    Frames Done: {3}/{4}
    Frames Killed: {5}
    Frames Crashed: {6}
    """

    toPrint = format_str.format(secondJob['show'], 
        secondJob['shot'], secondJob['job'], secondJob['done'], 
        getTotalFrames(secondJob), secondJob['killed'], secondJob['crashed'])

    global theNotif
    theNotif['msg'] = msg
    theNotif['toPrint'] = toPrint
    theNotif['dict'] = secondJob


def getTotalFrames(secondJob):

    return (int(secondJob['queued']) + int(secondJob['done']) + 
        int(secondJob['killed']) + int(secondJob['crashed']) +
        int(secondJob['running']))


def initMain(theSettings, i, isDone, user):

    global newSettings
    newSettings = theSettings

    global theNotif
    theNotif['msg'] = 'temp'

    # print 'BEFORE:', theNotif['msg']
    i = main(i, isDone, user)
    # print 'AFTER:', theNotif['msg']

    if theNotif['msg'] != 'temp':
        print theNotif['msg'],
        print theNotif['toPrint']

    return theNotif, i, isDone


