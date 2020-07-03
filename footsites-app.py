from random import choice
import string, json, sys, copy, os
from shutil import copyfile
from zipfile import ZipFile
from pathlib import Path

profile_file = "billing.db"

profilesdict = []

sites = {
    'footlocker-us': {
    },
    'kids-footlocker': {
    },
    'footaction': {
    },
    'eastbay': {
    },
    'champs-sports': {
    },
}

with open(profile_file) as thefile:
    for line in thefile:
        profilesdict.append(json.loads(line))

prodsGen = input("How many sites are you making groups for? ")

for eachProd in range(int(prodsGen)):

    print("== Sites currently supported ==\n *{}\n".format("\n *".join(list(sites))))

    siteselected = input("What site would you like to run? ").lower()

    keywords = input("What Product ID would you like to run? ")

    billingused = input(
        "How many billing profiles do you want used? You currently have {} profiles available: ".format(
            len(profilesdict)))

    if billingused == "":
        billingused = len(profilesdict)

    if int(billingused) > len(profilesdict):

        print("FYI - We will be duplicating some profiles....")

        while len(profilesdict) < int(billingused):
            for i in copy.deepcopy(profilesdict):
                profilesdict.append(i)
                if int(billingused) == len(profilesdict):
                    break

    numgroups = int(input("How many groups would you like your tasks split between? "))

    ranrange = str(input(
        "Input your random range (Hit Enter for all sizes)\n**Remember to use WhatBot random size format! Like 9.0,9.5,10.0: "))

    if ranrange == "":
        ranrange = "3.5,4.0,4.5,5.0,5.5,6.0,6.5,7.0,7.5,8.0,8.5,9.0,9.5,10.0,10.5,11.0,11.5,12.0,12.5,13.0,14.0,15.0"
        taskstyle = 1
    else:
        taskstyle = int(input(
            "\n1 - Random\n2 - Single (Each task only tries for one size, not random range)\nSelect task sizing option: "))

    groupsadded = []

    with open("groups.db", 'a') as groups:
        for i in range(numgroups):
            ranstr = ''.join(choice(string.ascii_letters + string.digits) for k in range(16))

            linetowrite = {"advanced": False, "customScrapers": [], "keywordsLink": "", "name": "",
                           "oneCheckoutPerProfile": False, "preloadHeadstart": "10", "restockMode": "BRUTE",
                           "scrapers": [],
                           "siteId": "",
                           "useCaptcha": False,
                           "proxySetId": "none"}
            linetowrite['_id'] = ranstr

            if taskstyle == 1:
                linetowrite['randomRange'] = ranrange

            if taskstyle == 2:
                linetowrite['randomRange'] = ""

            for i in sites[siteselected]:
                # sites[siteselected][i]
                linetowrite['scrapers'].append(sites[siteselected][i])
            if "http" not in str(keywords):
                linetowrite['keywordsLink'] = "{}".format(",".join(keywords.split(" ")))
            else:
                linetowrite['keywordsLink'] = keywords

            linetowrite['negatives'] = ""

            linetowrite['name'] = "{}-{}-{}".format(siteselected, eachProd, i)
            linetowrite['siteId'] = siteselected
            groups.write(json.dumps(linetowrite) + "\n")
            groupsadded.append(linetowrite)

    import math

    amtper = math.ceil(int(billingused) / numgroups)

    print("Adding {} profiles per group".format(amtper))
    l = 0

    with open("tasks.db", 'a') as tasks:
        for j in enumerate(groupsadded):
            for i in profilesdict[j[0] * amtper:(j[0] + 1) * amtper]:

                try:
                    flavor = "base"
                except:
                    flavor = None

                ranstr = ''.join(choice(string.ascii_letters + string.digits) for m in range(16))

                tasktemplate = {"_id": ranstr, "groupId": j[1]['_id'],
                                "billing": i['_id'],
                                "username": "", "password": "", "flavor": flavor, "preload": True,
                                "enabled": True}

                if taskstyle == 1:
                    tasktemplate["size"] = "random"

                if taskstyle == 2:
                    tasktemplate["size"] = choice(ranrange.split(",")).replace(".0","")


                tasks.write(json.dumps(tasktemplate) + "\n")

    # copyfile(profile_file, "billing.db")

    print("Done! Files generated. Copy to your WhatBot root folder and restart the bot.")

zipObj = ZipFile('wb-files.zip', 'w')

for eachFile in ['tasks.db', 'groups.db', 'billing.db']:
    zipObj.write(eachFile)
zipObj.close()

for eachFile in ['tasks.db', 'groups.db']:
    os.remove(eachFile)
