#!/usr/bin/env python
# encoding: utf-8
###############################################################################
#                                                                             #
#    PyMICE library                                                           #
#                                                                             #
#    Copyright (C) 2015 Jakub M. Kowalski, S. Łęski (Laboratory of            #
#    Neuroinformatics; Nencki Institute of Experimental Biology)              #
#                                                                             #
#    This software is free software: you can redistribute it and/or modify    #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This software is distributed in the hope that it will be useful,         #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this software.  If not, see http://www.gnu.org/licenses/.     #
#                                                                             #
###############################################################################

import unittest
from ICNodes import Animal, Visit
from datetime import datetime, timedelta
import pytz

def allInstances(instances, cls):
  return all(isinstance(x, cls) for x in instances)

class BaseTest(unittest.TestCase):
  def checkReadOnly(self, obj):
    for attr in self.attributes:
      try:
        self.assertRaises(AttributeError, lambda: setattr(obj, attr, attr))

      except AssertionError:
        print attr
        raise

class TestAnimal(BaseTest):
  attributes = ['Name', 'Tag', 'Sex', 'Notes']

  def setUp(self):
    self.mickey = Animal('Mickey', '2', 'male', 'bla')

  def testCreate(self):
    mouse = Animal('Jerry', 1)
    self.assertEqual(mouse.Name, 'Jerry')
    self.assertIsInstance(mouse.Name, unicode)
    self.assertEqual(mouse.Tag, {1})
    self.assertTrue(allInstances(mouse.Tag, long))
    self.assertIsInstance(mouse.Tag, frozenset)
    self.assertEqual(mouse.Sex, None)
    self.assertEqual(mouse.Notes, frozenset())
    self.assertIsInstance(mouse.Notes, frozenset)

    self.assertEqual(self.mickey.Tag, {2})
    self.assertEqual(self.mickey.Sex, 'male')
    self.assertIsInstance(self.mickey.Sex, unicode)
    self.assertEqual(self.mickey.Notes, {'bla'})
    self.assertTrue(allInstances(self.mickey.Notes, unicode))

  def testEq(self):
    self.assertTrue(self.mickey == Animal('Mickey', '2'))
    self.assertTrue(Animal('Mickey', '2') == self.mickey)
    self.assertFalse(self.mickey == Animal('Jerry', '2'))
    self.assertFalse(self.mickey == Animal('Mickey', '2', Sex='female'))

    animal = Animal(u'b\xf3br', 1)
    self.assertTrue(animal == 'b\xc3\xb3br')
    self.assertFalse(animal == 'bobr')

    self.assertTrue(animal == u'b\xf3br')
    self.assertFalse(animal == u'b\xc3\xb3br')

  def testNeq(self):
    self.assertTrue(self.mickey != Animal('Jerry', '2'))
    self.assertTrue(self.mickey != Animal('Mickey', '2', Sex='female'))
    self.assertFalse(self.mickey != Animal('Mickey', '2'))

    animal = Animal(u'b\xf3br', 1)
    self.assertFalse(animal != 'b\xc3\xb3br')
    self.assertTrue(animal != 'bobr')
    self.assertFalse(animal != u'b\xf3br')
    self.assertTrue(animal != u'b\xc3\xb3br')

  def testHash(self):
    self.assertEqual(hash(self.mickey), hash('Mickey'))

  def testStr(self):
    animal = Animal(u'b\xf3br', 1)
    self.assertEqual(str(animal), 'b\xc3\xb3br')
    self.assertIsInstance(str(animal), str)

  def testUnicode(self):
    animal = Animal(u'b\xf3br', 1)
    self.assertEqual(unicode(animal), u'b\xf3br')
    self.assertIsInstance(unicode(animal), unicode)


  def testMerge(self):
    mouse = Animal('Mickey', 1)
    mouse.merge(self.mickey)
    self.assertEqual(mouse.Sex, 'male')
    self.assertEqual(mouse.Notes, {'bla'})
    self.assertEqual(mouse.Tag, {1, 2})
    self.assertIsInstance(mouse.Tag, frozenset)

    mouse.merge(Animal('Mickey', 1))
    self.assertEqual(mouse.Sex, 'male')


    self.assertRaises(Animal.DifferentMouse,
                      lambda: Animal('Minnie', 1).merge(self.mickey))
    self.assertRaises(Animal.DifferentMouse,
                      lambda: Animal('Mickey', 1, 'female').merge(self.mickey))

    mouse = Animal('Mickey', 1, Notes='ble')
    mouse.merge(self.mickey)
    self.assertEqual(mouse.Notes, {'ble', 'bla'})
    mouse.merge(self.mickey)
    #self.assertEqual(mouse.Notes, ('ble', 'bla'))

  def testRepr(self):
    self.assertEqual(repr(self.mickey), u'< Animal Mickey (male; Tag: 2) >')
    mouse = Animal('Jerry', 1)
    self.assertEqual(repr(mouse), u'< Animal Jerry (Tag: 1) >')
    mouse.merge(Animal('Jerry', 2))
    self.assertEqual(repr(mouse), u'< Animal Jerry (Tags: 1, 2) >')

  def testReadOnly(self):
    self.checkReadOnly(self.mickey)


class Mock(object):
  def __init__(self):
    self.sequence = []


class MockCageManager(Mock):
  def getCage(self, cage):
    self.sequence.append(('getCage', cage))
    return int(cage)

  def getCageCorner(self, cage, corner):
    self.sequence.append(('getCorner', cage, corner))
    return int(cage), int(corner)


class MockNosepoke(Mock):
  def _bindToVisit(self, visit):
    self.sequence.append(('_bindToVisit', visit))

  def _del_(self):
    self.sequence.append('_del_')


class TestVisit(BaseTest):
  attributes = ('Start', 'Corner', 'End', 'Module', 'Cage',
                'CornerCondition', 'PlaceError',
                'AntennaNumber', 'AntennaDuration',
                'PresenceNumber', 'PresenceDuration',
                'VisitSolution',
                '_source', '_line',
                'Nosepokes')

  def checkAttribute(self, obj, name, value=None, cls=None):
    try:
      attr = getattr(obj, name)
      if value is None:
        self.assertIs(attr, None,)

      else:
        self.assertEqual(attr, value)
        if cls is not None:
          self.assertIsInstance(attr, cls)

    except AssertionError:
      print name
      raise

  def checkAttributes(self, obj, testList):
    for test in testList:
      if isinstance(test, basestring):
        self.checkAttribute(obj, test)

      else:
        self.checkAttribute(obj, *test)

  def setUp(self):
    self.start = datetime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
    self.end = datetime(1970, 1, 1, 0, 5, 15, tzinfo=pytz.utc)
    self.nosepokes = tuple(MockNosepoke() for _ in xrange(4))
    self.visit = Visit(self.start, 2, self.end, 'mod', 4,
                       1, 0,
                       2, 12.125,
                       7, 8.5,
                       0,
                       'source', 1,
                       self.nosepokes,
                       )

  def testCreate(self):
    #_vid
    visit = Visit(self.start, 2)
    self.checkAttributes(visit, [('Start', self.start),
                                 ('Corner', 2),
                                 'End', 'Module', 'Cage',
                                 'CornerCondition', 'PlaceError',
                                 'AntennaNumber', 'AntennaDuration',
                                 'PresenceNumber', 'PresenceDuration',
                                 'VisitSolution',
                                 '_source', '_line',
                                 'Nosepokes',
                                 ])

    self.checkAttributes(self.visit, [('Start', self.start),
                                      ('Corner', 2),
                                      ('End', self.end),
                                      ('Module', 'mod'),
                                      ('Cage', 4),
                                      ('CornerCondition', 1),
                                      ('PlaceError', 0),
                                      ('AntennaNumber', 2),
                                      ('AntennaDuration', 12.125),
                                      ('PresenceNumber', 7),
                                      ('PresenceDuration', 8.5),
                                      ('VisitSolution', 0),
                                      ('_source', 'source'),
                                      ('_line', 1),
                                      ('Nosepokes', self.nosepokes),
                                      ])

  def testReadOnly(self):
    self.checkReadOnly(self.visit)


  def testNosepokes(self):
    for nosepoke in self.nosepokes:
      self.assertEqual(nosepoke.sequence, [('_bindToVisit', self.visit)])
      self.assertIs(nosepoke.sequence[0][1], self.visit)

  def testDel(self):
    self.visit._del_()
    for nosepoke in self.nosepokes:
      self.assertEqual(nosepoke.sequence[-1], '_del_')

    for attr in self.visit.__slots__:
      self.assertRaises(AttributeError,
                        lambda: getattr(self.visit, '_Visit' + attr))

  def testDuration(self):
    self.assertEqual(self.visit.Duration, timedelta(seconds=315))


if __name__ == '__main__':
  unittest.main()