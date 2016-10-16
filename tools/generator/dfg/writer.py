# -*- coding: utf-8 -*-
# Copyright (c) 2013-2016, Niklas Hauser
# Copyright (c)      2016, Fabian Greif
# All rights reserved.

import os
import logging

from lxml import etree

LOGGER = logging.getLogger('dfg.writer')

class XMLDeviceWriter:
    """ DeviceWriter
    Base class for all writers for handling the opening and writing of XML files etc...
    """

    def __init__(self, device):
        self.file = None
        self.device = device

        self.tree = XMLElement('rca')
        self.tree.setAttribute('version', '1.0')
        self.tree.addComment(' WARNING: This file is generated automatically, do not edit!\n \
        Please modify the modm-devices/tools/generator code instead and rebuild this file.\n \
        Be aware, that regenerated files might have a different composition due to technical reasons. ')

        props = self.device.ids.union.properties
        props = {p : props[p] for p in props if props[p] != None}
        self.root = self.tree.addChild('device')
        # Force an order onto a dictionary in the most stupid way I could think of
        for name in ['platform', 'family', 'name', 'pin_id', 'size_id', 'type']:
            if name in props:
                self.root.setAttribute(name, props[name])

    def addInstancesToDriver(self, driver, instances, attributes):
        for instance in instances:
            child = driver.addChild('instance')
            child.setAttributes(attributes)
            child.setValue(instance)

    def writeToFile(self, file):
        if os.path.exists(file):
            LOGGER.warning("Overwriting file '" + os.path.basename(file) + "'")
        else:
            LOGGER.info("New XML file: '" + os.path.basename(file) + "'")
        self.file = file

        with open(self.file, 'w') as device_file:
            device_file.write(self.toString())

    def writeToFolder(self, folder, name):
        abspath = os.path.abspath(folder)
        if os.path.isdir(abspath):
            filename = os.path.join(folder, name)
            self.writeToFile(filename)
        else:
            LOGGER.error("Path is not a folder! " + folder)

    def toString(self):
        return etree.tostring(self.tree.root,
                            encoding="UTF-8",
                            pretty_print=True,
                            xml_declaration=True,
                            doctype='<!DOCTYPE rca SYSTEM "../devicefile.dtd">')

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "XMLDeviceWriter(" + os.path.basename(self.file) + ")"


class XMLElement:
    """ XMLElement
    Helper class to wrap and extend the methods of etree.Element and etree.SubElement
    """

    def __init__(self, tag=None):
        self.root = None
        if tag != None:
            self.root = etree.Element(tag)

    def setAttributes(self, device_dict):
        for key in device_dict:
            self.setAttribute(key, device_dict[key])

    def setAttribute(self, key, value):
        self.root.set(key, str(value))

    def removeAttribute(self, key):
        try:
            del self.root.attrib[key]
        except KeyError:
            pass

    def addChild(self, name):
        element = XMLElement()
        element.root = etree.SubElement(self.root, name)
        return element

    def prependChild(self, name):
        element = XMLElement()
        element.root = etree.Element(name)
        self.root.insert(0, element.root)
        return element

    def addComment(self, comment):
        self.root.append(etree.Comment(str(comment)))

    def setValue(self, value):
        self.root.text = str(value)

    def sort(self, key=None):
        if key == None:
            self.root[:] = sorted(self.root)
        else:
            self.root[:] = sorted(self.root, key=key)

    def toString(self):
        return etree.tostring(self.root, pretty_print=True)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "XMLElement(\n" + self.toString() + ")"
