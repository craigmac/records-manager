#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
:title: records.py
:author: Craig MacEachern
:version: 1.10
:last revision: 2016-01-26
:release date: 2015-06-01

A records management module with functions for scanning a drive and find a set
of files that match against a certain threshold criteria. 

##### KNOWN BUGS/ISSUES ##########
* On Windows 7/8+ the Last Accessed Date property of files is not enabled by
default, so this property will always equal the Last Modified Date property.
Enable the Last Accessed Date property in the registry to receive accurate 
results.
"""
import os
import sys
from datetime import datetime, timedelta, date


def get_time(file_name, mod='m'):
    """
    Return a Datetime object representing last modified attribute of 
    file_name. 

    :param file_name: The file we want to get attribute of
    :param mod: Default 'm' means look at file last modified attribute
                Accepts 'a' for last accessed attribute
    :returns: A Datetime object representing time found on file_name
    :raises OSError: if the file name last accessed time could not be found
    :raises OSError: if the file name last modified time could not be found
    """
    if mod == 'a':
        try:
            t = os.path.getatime(file_name)
        except OSError:
            raise OSError('Could not get last accessed time from ' + file_name)
        return datetime.fromtimestamp(t)
    else:  # Ignore all other cases and just get modified time
        try:
            t = os.path.getmtime(file_name)
        except OSError:
            raise OSError('Could not get last modified time from ' + file_name)
        return datetime.fromtimestamp(t)


def get_blacklist(blacklist_path):
    """
    Return a list from given path of file contents.

    :returns: a list of folders/filenames
    """
    if not os.path.isfile(blacklist_path):
        raise IOError('Given blacklist_path file cannot be found.')

    # If empty, just return empty list.
    if not blacklist_path:
        return []
    try:
        with open(blacklist_path, 'r') as bl:
            content = bl.read()
        return content.split('\n')
    except IOError:
        raise IOError("Error reading from blacklist file.")


def get_file_paths(directory='.', blacklist=None, get_hidden=False):
    """
    Return a recursive list of normalized full path filenames. Exclude 
    hidden files and directories, starting from current path.

    :param directory: Optional path name of a directory. 
                      Defaults to current directory.
    :param blacklist: Optional list of file and/or directory names to exclude
                      in the search. Default is None.
    :param get_hidden: Optional. Default is False. If True include hidden files 
                       and/or directories in the search.
    :returns: a list of full path filenames. 
    :raises IOError: if can not access the filesystem.
    :raises IOError: if given directory parameter does not exist.
    :raises Except: with stack trace on an undefined error and exits. This is
                    a precaution that should never happen.
    """
    if blacklist is None:
        blacklist = []

    # Expand any env vars and get absolute path before checking if dir exists
    if not os.path.isdir(os.path.abspath(os.path.expanduser(directory))):
        raise IOError("Path given does not exist.")

    fullpaths = []

    try:
        for root, dirnames, filenames in os.walk(directory):
            skip_current_path = False

            # on Windows split path using \ separator
            # e.g. ['path', 'to', 'foobar']
            if (sys.platform).find('win') >= 0:
                split_path = root.split('\\')
            else:
                split_path = root.split('/')

            # Skip if matching a pattern in blacklist (defaults to None)
            for pattern in blacklist:
                if pattern in split_path:
                    skip_current_path = True
                    break

            if skip_current_path:  # go to next folder, stop processing here
                print 'Skipping: {}'.format(root)
                break

            for name in filenames:
                if get_hidden:  # Get hidden files too
                    fullpaths.append(os.path.join(root, name))
                else:
                    if name.startswith('.'):
                        continue
                    else:
                        fullpaths.append(os.path.join(root, name))
    except IOError:
        print "Error accessing the filesystem."
        sys.exit()
    except:
        print "Unexpected error: ", sys.exc_info()[0]
        sys.exit()
    else:
        # Strip extra backslashes, etc. from paths.
        return [os.path.normpath(p) for p in fullpaths]


def get_cutoff_files(arr, days, flag='m'):
    """
    Return a list of filenames that meet the criteria of being last modified 
    greater than days. 

    :param arr: List of absolute path filenames.
    :param days: Threshold for the number of days.
    :param flag: Optional. Default 'm' means file attribute last modified.
                 Also accepts 'a' for file attribute last accessed.
    :returns: a list of filenames.
    """
    # Get Datetime object of now to calculate delta.
    now = datetime.now()
    # e.g. datetime.datetime(2015, 7, 7, 11, 56, 13, 137000)
    cutoff = now - timedelta(days)  # Datetime obj - delta

    cutoff_list = []

    if flag == 'a':
        for f in arr:
            a_time = get_time(f, 'a')
            if a_time < cutoff:
                cutoff_list.append(f)
    else:
        # Get modified date as Datetime object
        for f in arr:
            m_time = get_time(f)
            if m_time < cutoff:
                cutoff_list.append(f)
    del (arr)  # Don't wait for garbage collection, we don't need it
    return cutoff_list


def make_dates_strings(arr, flag='m'):
    """
    Return a list of formatted strings representing the last modified times 
    of each filename found in arr. 

    :param arr: List of files to filter.
    :param flag: Optional. Default 'm' is file last modified attribute.
                 Also accepts 'a' for file last accessed attribute.
    :returns: a list of formatted strings, e.g., "2010-05-20".
    """
    if flag == 'a':
        return [get_time(f, 'a').strftime("%Y-%m-%d") for f in arr]
    else:
        return [get_time(f).strftime("%Y-%m-%d") for f in arr]


def write_to_file(arr, name='scan_report', style='txt', flag='m'):
    """
    Return True if filenames in 'arr' succeeds in writing to 'name'. 
    
    :param arr: A list of filenames.
    :param name: Optional. Name of the file to write to.
    :param style: Optional. Write to file as plain text with tabs ('txt') or 
                  comma separated values ('csv')
    :param flag: Optional. Last modified file attribute.
                 Also accepts 'a' for last accessed file attribute.
    :returns: True if write to file succeeds.
    :raises IOError: if write to file fails. 
    """
    # Add .txt or .csv to end  of 'name' param and set proper separator
    if style == 'csv':
        name += '.csv'
        separator = ","
    else:
        name += '.txt'
        separator = '\t'

    # Get list of strings to write
    if flag == 'a':
        file_times = make_dates_strings(arr, 'a')
    else:
        file_times = make_dates_strings(arr)

    # Combine file_times with the full path to the file into a dictionary
    # e.g., files = {"my/path/to/foo": "2010-05-27", ... }
    files = {}
    for p, d in zip(arr, file_times):
        files[p] = d

    try:
        with open(name, 'w') as f_out:
            f_out.write("Year-Month-Date" + separator)  # Header
            f_out.write("Full file path \n")
            for f in files:
                f_out.write(files[f])
                f_out.write(separator)
                f_out.write(f)
                f_out.write('\n')
    except IOError:
        raise IOError('Error writing to file: {}'.format(name))
    else:  # Successfully wrote to the file.
        return True
