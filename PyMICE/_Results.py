#!/usr/bin/env python
# encoding: utf-8
"""
ggg
"""

import os 
import csv
import warnings

class ResultsCSV(object):
  def __init__(self, filename, fields=(), force=False):
    self.__fields = set(fields)
    self.__rows = {}
    self.__currentID = None
    self.__nextID = 0
    if os.path.exists(filename) and not force:
      raise ValueError("File %s already exists." % filename)

    self.__fh = open(filename, 'wb')

  def __enter__(self):
    pass

  def __exit__(self, type, value, traceback):
    self.close()

  def __del__(self):
    self.close()

  def close(self):
    if self.__fh is None:
      return

    fields = sorted(self.__fields)
    writer = csv.writer(self.__fh)

    writer.writerow([f.encode('utf-8') for f in fields])
    for row in self.__rows.values():
      line = [unicode(row.get(f, '')).encode('utf-8') for f in fields]
      writer.writerow(line)

    self.__fh.close()

  def addRow(self, id=None):
    if id is None:
      while True:
        id = self.__nextID
        self.__nextID += 1
        if id not in self.__rows:
          break

    elif id in self.__rows:
      raise ValueError('Row of ID %s already exists.' % id)

    self.__current = {}
    self.__rows[id] = self.__current
    self.__currentID = id
    return id

  def setRow(self, id):
    self.__current = self.__rows[id]
    self.__currentID = id
    return id

  def getRow(self):
    return self.__currentID

  def addField(self, field, value='', id=None):
    if id is None:
      id = self.__currentID
      if id is None:
        raise ValueError('Row ID must be given if no row has been chosen yet.')

    self.__fields.add(field)

    try:
      row = self.__rows[id]

    except KeyError:
      warnings.warn('Row of ID %s not found, creating a new row.' % id)
      row = self.__rows[self.addRow(id)]

    if field in row:
      warnings.warn('Field %s already set for row of ID %s, overwriting.' % (field, id))
      
    row[field] = value
