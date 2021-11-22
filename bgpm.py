#!/usr/bin/env python

from collections import defaultdict

import pybgpstream
from matplotlib import pyplot as plt

import datetime

"""Code file for CS 6250 BGPM Project

Edit this file according to docstrings. 
Do not change the existing function name or arguments in any way.

"""
# Task 1 Part A.
def calculateUniqueIPAddresses(cache_files):
    """Retrieve the number of unique IP prefixes from input BGP data.

    Args:
        cache_files: A list of absolute file paths.
          File paths may not be in order but will end with a timestamp that can be used for sorting.
          For example: ["/rib_files_final/1357027200.120.cache", "/rib_files_final/1483257600.120.cache"]

    Returns:
        A list containing the number of unique IP prefixes for each input cache file.
          For example: [2, 5]
    """
    res = []
    for filepath in cache_files:
        #set stream interface
        stream = pybgpstream.BGPStream(data_interface = "singlefile")
        stream.set_data_interface_option("singlefile", "rib-file", filepath)
        
        # loop through the element in stream and add prefix to set
        curSet = set()
        for elem in stream:
            curSet.add(elem._maybe_field("prefix"))
        
        res.append(len(curSet))
        
    return res

def plot(cache_files):
    prefArr = [957590, 608259, 736904, 500091, 542359, 451279, 818578, 674803, 889780]
    prefDict = {}
    for i in range(0, len(cache_files)):
        time = cache_files[i].split("/")[5][15:25]
        prefDict[time] = prefArr[i]
    
    dev_x = []
    dev_y = []
    for i in sorted (prefDict.keys()):
        dev_x.append(i)
        dev_y.append(prefDict[i])
    print(dev_x)
    print(dev_y)
    plt.plot(dev_x, dev_y)
    plt.show()

# Task 1 Part B.
def calculateUniqueAses(cache_files):
    """Retrieve the number of unique ASes from input BGP data.

    Args:
        cache_files: A list of absolute file paths.
          File paths may not be in order but will end with a timestamp that can be used for sorting.
          For example: ["/rib_files_final/1357027200.120.cache", "/rib_files_final/1483257600.120.cache"]

    Returns:
        A list containing the number of the number of unique AS for each input file.
          For example: [2, 5]
    """
    res = []
    for filepath in cache_files:
        #set stream interface
        stream = pybgpstream.BGPStream(data_interface = "singlefile")
        stream.set_data_interface_option("singlefile", "rib-file", filepath)
        
        # loop through the element in stream and add ASes to set
        curSet = set()

        for elem in stream:
            curSet.add(elem._maybe_field("as-path").split(" ")[-1])        
        
        res.append(len(curSet))
        
    return res


# Task 1 Part C.
def examinePrefixes(cache_files):
    """
    Args:
        cache_files: A list of absolute file paths.
          File paths may not be in order but will end with a timestamp that can be used for sorting.
          For example: ["/rib_files_final/1357027200.120.cache", "/rib_files_final/1483257600.120.cache"]

    Returns:
        A list of the top 10 origin ASes according to percentage increase of the advertised prefixes.
        See assignment description for details.
    """
    # key = AS  val = [start, end]
    myDict = {}
    cache_files.sort()

    for filepath in cache_files:
        # set stream interface
        stream = pybgpstream.BGPStream(data_interface = "singlefile")
        stream.set_data_interface_option("singlefile", "rib-file", filepath)
        
        # loop through the element in stream and add prefix to 
        curDict = {}
        for elem in stream:
            key = elem._maybe_field("as-path").split(" ")[-1]
            if key in curDict:
                curDict[key] += 1
            else:
                curDict[key] = 1

        # add curSet to dict
        for key in curDict:
            if key in myDict:
                if len(myDict[key]) == 1:
                    myDict[key].append(curDict[key])
                else:
                    myDict[key][1] = curDict[key]
            else:
                myDict[key] = []
                myDict[key].append(curDict[key])

    increases = []
    for key in myDict:
        if len(myDict[key]) == 2:
            start = myDict[key][0]
            end = myDict[key][1]
            increases.append([key, (end - start)/(start * 1.0)])

    asten = sorted(increases, key = lambda x:x[1])
    res = []
    print(asten[-10:])
    for curAS in asten[-10:]:
        res.append(curAS[0])
    return res
    

# Task 2 Part A.
def calculateShortestPath(cache_files):
    """Compute the shortest AS path length for every origin AS from input BGP data.

    Retrieves the shortest AS path length for every origin AS for every input cache file.
    Your code should return a dictionary where every key is the AS string and every value associated with the key is
    a list of shortest path lengths for that AS. See project description for details on how to do this.

    Note: For any AS that is not present in every input file, fill the corresponding entry in its list with a zero.
    Every value in the dictionary should have the same length.

    Args:
        cache_files: A list of absolute file paths.
          File paths may not be in order but will end with a timestamp that can be used for sorting.
          For example: ["/rib_files/ris.rrc06.ribs.1357027200.120.cache", "/rib_files/ris.rrc06.ribs.1483257600.120.cache]

    Returns:
        A dictionary where every key is the AS and every value associated with the key is
          a list of shortest path lengths for that AS, for every input file, sorted by date (earliest first).
          For example: {"455": [4, 0, 3], "533": [0, 1, 2]}
          corresponds to the AS "455" with shortest path lengths 4, 0 and 3 and the AS "533" with shortest paths 0, 1 and 2.
    """
    # Initialize
    # key = AS, val = [] * 9
    res = {}
    cache_files.sort()
    for i in range(len(cache_files)):
        filepath = cache_files[i]
        stream = pybgpstream.BGPStream(data_interface = "singlefile")
        stream.set_data_interface_option("singlefile", "rib-file", filepath)
        
        for elem in stream:
            # split path into string array
            pathStr = elem._maybe_field("as-path")
            if len(pathStr) == 0:
                continue
            
            uniqAS = set()
            dupPathArr = pathStr.split(" ")
            # iterate the array, add element to set
            for path in dupPathArr:
                uniqAS.add(path)
            # add to res if count is less or key not exist
            count = len(uniqAS)
            AS = dupPathArr[-1]
            if AS not in res:
                res[AS] = [0] * len(cache_files)
            res[AS][i] = count if res[AS][i] == 0 else min(res[AS][i], count)
    return res


# Task 3 Part A.
def calculateRTBHDurations(cache_files):
    """Identify blackholing events and compute the duration of all RTBH events from input BGP data.

    Identify events where the IPV4 prefixes are tagged with at least one Remote Triggered Blackholing (RTBH) community.
    See project description for details on how to do this.

    Args:
        cache_files: A list of absolute file paths.
          File paths may not be in order but will end with a timestamp that can be used for sorting.
          For example: ["/update_files_blackholing/ris.rrc06.ribs.1357027200.120.cache", "/update_files_blackholing/ris.rrc06.ribs.1483257600.120.cache]

    Returns:
        A dictionary where each key is a peerIP and each value is another dictionary with key equal to a
            prefix and each value equal to a list of explicit RTBH event durations.
            For example: {"455": {"123": [4, 1, 3]}}
            The above example corresponds to the peerIP "455", the prefix "123" and event durations of 4, 1 and 3.
    """

    return {}


# Task 4.
def calculateAWDurations(cache_files):
    """Identify Announcement and Withdrawal events and compute the duration of all explicit AW events in the input data.

    Identify explicit AW events.
    See project description for details on how to do this.

    Args:
        cache_files: A list of absolute file paths.
          File paths may not be in order but will end with a timestamp that can be used for sorting.
          For example: ["/update_files/ris.rrc06.ribs.1357027200.120.cache", "/update_files/ris.rrc06.ribs.1483257600.120.cache]

    Returns:
        A dictionary where each key is a peerIP and each value is another dictionary with key equal to a
            prefix and each value equal to a list of explicit AW event durations.
            For example: {"455": {"123": [4, 1, 3]}}
            The above example corresponds to the peerIP "455", the prefix "123" and event durations of 4, 1 and 3.
    """

    return {}
