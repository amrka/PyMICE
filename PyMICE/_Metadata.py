#!/usr/bin/env python
# encoding: utf-8
"""
ggg
"""
# Marysia_ARC/main.py

import os 
import time
import datetime
import csv
import re
import collections

from ._Loader import convertTime



class MetadataNode(object):
  _labels = None
  _filename = None
  _nextClass = None

  @classmethod
  def fromMeta(cls, meta, **kwargs):
    _next = None if cls._nextClass is None else cls._nextClass.fromMeta(meta)
    filename = os.path.join(meta, cls._filename)
    return cls.fromCSV(filename, _next=_next, **kwargs)

  @classmethod
  def fromCSV(cls, filename, **kwargs):
    if not os.path.exists(filename):
      return

    result = {}
    with open(filename, 'rb') as fh:
      for row in csv.DictReader(fh):
        byLabel = [row.pop(x, '').strip() for x in cls._labels]
        for k, v in kwargs.items():
          assert k not in row
          row[k] = v

        instance = cls(*byLabel, **row)
        result[instance.Name] = instance

    return result

  def __repr__(self):
    return str(self)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return self.Name


class Substance(MetadataNode):
  _labels = ['name', 'molar mass', 'density']
  _filename = 'substances.csv'
  
  def __init__(self, Name, MolarMass, Density, _next=None):
    self.Name = Name.decode('utf-8').lower()
    self.MolarMass = float(MolarMass) if MolarMass != '' else None
    self.Density = float(Density) if Density != '' else None


class Concentration(object):
  def __init__(self, Substance, Amount=None, Unit=None, VolumeConcentration=None, MassFraction=None):
    self.Substance = Substance
    self.Amount = Amount
    self.Unit = Unit.decode('utf-8') if Amount is not None and Unit is not None else None
    self.VolumeConcentration = VolumeConcentration
    self.MassFraction = MassFraction

  def __repr__(self):
    return str(self)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    if self.Amount is None:
      return unicode(self.Substance)

    if self.Unit is None:
      return u'%s %f' % (self.Substance, self.Amount)

    return u'%s %f [%s]' % (self.Substance, self.Amount, self.Unit)


class Solutes(object):
  def __init__(self, solutes, density=None):
    self.__keys = set()

    for substance, amount, unit in solutes:
      massFraction = None
      volumeConcentration = None
      if unit == 'volume':
        volumeConcentration = amount
        try:
          massFraction = amount * substance.Density / density

        except:
          pass

      if unit == 'mass':
        massFraction = amount
        try:
          volumeConcentration = amount * density / substance.Density

        except:
          pass

      name = unicode(substance)
      self.__keys.add(name)
      setattr(self, name,
              Concentration(substance, amount, unit,
                        VolumeConcentration=volumeConcentration,
                        MassFraction=massFraction))

  def __bool__(self):
    return len(self.__keys) > 0

  def __len__(self):
    return len(self.__keys)

  def keys(self):
    return list(self.__keys)

  def __getitem__(self, key):
    return getattr(self, key)

  def __repr__(self):
    return str(self)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return u', '.join(unicode(getattr(self, k)) for k in sorted(self.__keys))

          


class Liquid(MetadataNode):
  _filename = 'liquids.csv'
  _labels = ['name', 'density']
  __parseSubstance = re.compile('^\s*(?P<substance>\S+)(?:\s+\[(?P<unit>\w+)\])?\s*$')
  _nextClass = Substance

  def __init__(self, Name, Density, _next=None, **solutes):
    self.Name = Name.decode('utf-8').lower()
    self.Density = float(Density) if Density != '' else None
    self.Solvent = None

    tmp = []
    for key, amount in solutes.items():
      match = self.__parseSubstance.match(key.lower())
      if not match:
        continue

      substance, unit = match.group('substance', 'unit')
      substance = substance.strip().lower()
      if unit is not None:
        unit = unit.strip().lower()

      amount = amount.strip().lower()
      if amount in ('medium', 'solvent'):
        assert self.Solvent is None
        self.Solvent  = _next.get(substance, substance) if _next else substance

      else:
        try:
          amount = float(amount)

        except:
          continue

        tmp.append((_next.get(substance, substance) if _next else substance,
                    amount,
                    unit))

    if len(tmp) == 1. and not self.Solvent:
      substance, amount, unit = tmp.pop()
      self.Solvent = Concentration(substance, amount, unit,
                                   MassFraction=1.,
                                   VolumeConcentration=1.)

    elif self.Solvent and not tmp:
      self.Solvent = Concentration(substance,
                                   MassFraction=1.,
                                   VolumeConcentration=1.)

    self.Solutes = Solutes(tmp, density=self.Density)

    if self.Solvent:
      massFraction = 1.
      volumeConcentration = None
      if self.Solutes:
        try:
          for solute in self.Solutes.keys():
            massFraction -= self.Solutes[solute].MassFraction

        except:
          massFraction = None

        try:
          volumeConcentration = massFraction * self.Density / self.Solvent.Density

        except:
          pass

        self.Solvent = Concentration(self.Solvent,
                                     VolumeConcentration=volumeConcentration,
                                     MassFraction=massFraction)

      if not self.Solutes and hasattr(self.Solvent.Substance, 'Density'):
        if self.Density is None:
          self.Density = self.Solvent.Substance.Density

        else:
          assert self.Density == self.Solvent.Substance.Density or self.Solvent.Substance.Density is None

#  @classmethod
#  def fromCSV(cls, filename, substances=None):
#    result = {}
#    with open(filename, 'rb') as fh:
#      #return dict((cls._key(row), cls(*map(row.get, cls._labels)))\
#      #            for row in csv.DictReader(fh))
#      for row in csv.DictReader(fh):
#        key = cls._key(row)
#        byLabel = map(row.pop, cls._labels)
#        result[key] = cls(*byLabel, substances=substances, **row)
#
#    return result
#
#  @classmethod
#  def fromMeta(cls, meta):
#    filename = os.path.join(meta, cls._filename)
#    return cls.fromCSV(filename, Substance.fromMeta(meta))

  def __repr__(self):
    result = str(self.Name)
    if self.Solutes:
      result += ': %s' % str(self.Solutes)

      if self.Solvent:
        result += ' in %s' % str(self.Solvent.Substance)

    else:
      result += ': %s' % str(self.Solvent.Substance)

    return result


class Bottles(MetadataNode):
  _filename = 'bottles.csv'
  _labels = ['name']
  _nextClass = Liquid
  __parseLocation = re.compile('^\s*(?P<kind>\S+)\s+(?P<number>\d+)\s*$')

  def __init__(self, Name, _next=None, **locations):
    self.Name = Name.decode('utf-8').lower()
    self.Corners = {}
    self.Sides = {}

    for key, liquid in locations.items():
      liquid = liquid.strip().lower()
      liquid = _next.get(liquid, liquid) if _next else liquid
      match = self.__parseLocation.match(key.lower())
      kind, number = match.group('kind', 'number')
      number = int(number)
      if kind == 'corner':
        self._addCorner(number, liquid)

      elif kind == 'side':
        self._addSide(number, liquid)

  def _addSide(self, side, liquid):
    assert side not in self.Sides
    self.Sides[side] = liquid

  def _addCorner(self, corner, liquid):
    assert corner not in self.Corners
    self._addSide(corner * 2 - 1, liquid)
    self._addSide(corner * 2, liquid)
    self.Corners[corner] = liquid


class Animal(MetadataNode):
  _filename = 'animals.csv'
  _labels = ['name', 'weight', 'deceased'] 

  def __init__(self, Name, Weight=None, Deceased=None, _next=None, _groups=None, _partitions=None, **kwargs):
    self.Name = Name.decode('utf-8')
    self.Weight = float(Weight) if Weight != '' else None
    self.Deceased = Deceased if Deceased != '' else False
    for key, value in kwargs.items():
      key = key.strip().lower()
      value = value.strip().lower()

      if key.startswith('group'):
        if _groups is not None:
          if key == 'group':
            group = value

          else:
            if value == '':
              continue

            group = key[5:].strip()

          try:
            _groups[group].append(self)

          except KeyError:
            _groups[group] = [self]

      elif key.startswith('partition'):
        if _partitions is not None:
          key = key[9:].strip()
          value = int(value)

          try:
            _partitions[key][value].append(self)

          except KeyError:
            try:
              _partitions[key][value] = [self]

            except KeyError:
              _partitions[key] = {value: [self]}


class Phase(MetadataNode):
  _filename = 'phases.csv'
  _labels = ['start', 'end', 'name', 'type', 'iteration', 'partition', 'comments']

  def __init__(self, Start, End, Name, Type, Iteration, Partition, Comments, _partitions, _bottles, **kwargs):
    self.Start = convertTime(Start)
    self.End = convertTime(End)
    self.Name = Name.decode('utf-8') if Name != '' else None
    self.Type = Type.decode('utf-8') if Type != '' else None
    self.Iteration = int(Iteration) if Iteration != '' else None
    self.Mice = _partitions[Partition]
    self.Comments = Comments.decode('utf-8') if Comments != '' else None
    self.Cages = {}
    for key, val in kwargs.items():
      key = key.strip().lower()
      val = val.strip().lower()
      if key.startswith('cage') and val in _bottles:
        cage = int(key[4:].strip())
        self.Cages[cage] = _bottles[val]
      
  @classmethod
  def fromCSV(cls, filename, **kwargs):
    if not os.path.exists(filename):
      return

    result = {}
    rows = {}
    with open(filename, 'rb') as fh:
      for i, row in enumerate(csv.DictReader(fh)):
        byLabel = [row.pop(x, '').strip().lower() for x in cls._labels]
        for k, v in kwargs.items():
          assert k not in row
          row[k] = v

        instance = cls(*byLabel, **row)
        if instance.Name is not None:
          result[instance.Name] = instance

        else:
          rows[i] = instance

    for i, instance in rows.items():
      if instance.Type is not None and instance.Iteration is not None:
        name = "%s %d" % (instance.Type, instance.Iteration)
        if name in result:
          j = 0
          while ("%s (%d)" % (name, j)) in result:
            j += 1

          name = "%s (%d)" % (name, j)

        instance.Name = name
        result[instance.Name] = instance
        del rows[i]

    for i, instance in rows.items():
      if instance.Type is not None:
        j = 0
        while ("%s (%d)" % (instance.Type, j)) in result:
          j += 1

        instance.Name = "%s (%d)" % (instance.Type, j)
        result[instance.Name] = instance
        del rows[i]

    for i, instance in rows.items():
      name = "Phase %d" % i
      if name in result:
        j = 0
        while ("%s (%d)" % (name, j)) in result:
          j += 1

        name = "%s (%d)" % (name, j)

      instance.Name = name
      result[instance.Name] = instance

    return result

  @classmethod
  def fromMeta(cls, meta, **kwargs):
    bottles = Bottles.fromMeta(meta)
    groups = {}
    partitions = {}
    animals = Animal.fromMeta(meta, _groups=groups, _partitions=partitions)
    phases = cls.fromCSV(os.path.join(meta, cls._filename),
                         _partitions=partitions,
                         _bottles=bottles)
    return phases, animals, groups
