"""
Common functions for representing structural sections.
Sections are design agnostic - they only store information about a sections
geometry and the material used.

These objects are archetypes that have their details filled in later.
For example, a csao86 CLT section will store it's information.

"""

import collections
import numpy as np

from abc import ABC
from .section import SectionMonolithic
from ..material import MaterialElastic
from ..read import DBConfig, _loadSectionDBDict
from ...units import ConverterLength


__all__ = ['Rebar', 'RebarGroup', 'RebarCollection', 'RebarFactory']

class Rebar(SectionMonolithic):
    def __init__(self, mat:MaterialElastic, name:str, d:float, dnet:float,  
                 A:float, xy:tuple = None, rcurve:float = None, 
                 rhook:float = None, lUnit = 'mm'):
        self.mat = mat
        self.name = name
        self.A = A
        self.d = d
        self.dnet = dnet
        self.xy = xy
        self.rcurve = rcurve
        self.rhook  = rhook
        self.lenght:None
        
        self._initUnits(lUnit)
               
    def _initUnits(self, lUnit):
        """Initiates the length unit used for the layer"""
        self.lUnit = lUnit
        self.lConverter = ConverterLength()   

    
    def setxy(self, xy:tuple):
        self.xy = xy
        
    def getA(self, lUnit:str = ''):
        lfactor = self.lConvert(self._validateLunit(lUnit))
        return self.A * lfactor**2

    def getd(self, lUnit:str = ''):
        lfactor = self.lConvert(self._validateLunit(lUnit))        
        return self.d * lfactor**2

    #TODO: test
    def convertUnits(self, lUnit:str):
        """
        Converts the rebar length units from one set of units to another.

        Parameters
        ----------
        lUnit : string
            Converts the section units.

        """
        cfactor = self.lConvert(lUnit)
        self.lUnit = lUnit
        self.A = self.A*cfactor**2
        self.d = self.d*cfactor
        self.dnet = self.dnet*cfactor
        self.xy = (self.xy[0]*cfactor,self.xy[1]*cfactor)

class RebarGroup(collections.UserList):
    
    @property
    def mat(self):
        return self[0].mat
    
    @property
    def coords(self):
        return self.getAttr('coords')
    
    def listAttrs(self):
        """        Lists the rebar attributes.        """
        return self[0].__dict__.keys()
    
    def getAttr(self, attribute):
        """  Gets outputs from the rebar attributes. """        
        attrs = []
        for bar in self:
            attrs.append(bar.__dict__[attribute])
        return np.array(attrs)    
    
    def getCoords(self, lUnit = ''):
        """ Returns an array of the rebar coordinants. """
        lUnit = self[0]._validateLunit(lUnit)
        lfactor = self[0].lConvert(lUnit)
        return self.getAttr('xy') * lfactor
    
    
    def getyCoords(self, lUnit = ''):
        """ Returns an array of the rebar coordinants. """
        return self.getCoords(lUnit)[:,1]
        
    def getxCoords(self, lUnit = ''):
        """ Returns an array of the rebar coordinants. """
        return self.getCoords(lUnit)[:,0]
    
    def getdeff(self, direction:str = 'y', lUnit:str = ''):
        """
        Calcualtes the effective depth of a rebar group, which
        is the average position of the rebar.

        Parameters
        ----------
        direction : str, optional
            The direction to calculate deff in. The default is 'y'.

        Returns
        -------
        float
            The average depth of the rebar within the group.

        """

        if direction == 'y':
            return np.average(self.getyCoords(lUnit))
        elif direction == 'x':
            return np.average(self.getxCoords(lUnit))
        
    def getNetArea(self, lUnit = ''):
        lUnit = self[0]._validateLunit(lUnit)
        lfactor = self[0].lConvert(lUnit)        
        return np.sum(self.getAttr('A')) * lfactor**2
            
    def getAreas(self, lUnit = ''):
        lUnit = self[0]._validateLunit(lUnit)
        lfactor = self[0].lConvert(lUnit)        
        return self.getAttr('A') * lfactor**2
    
    
    def convertUnits(self, lUnit:str):
        """
        Converts the section units from one set of units to another.

        Parameters
        ----------
        lUnit : string
            Converts the section units.

        """
        for bar in self:
            bar.convertUnits(lUnit)

class RebarLayer(RebarGroup):
    

    def getdeff(self, direction = 'y', lUnit = ''):
        """
        Returns the depth of a rebar layer in the input direction.

        Parameters
        ----------
        direction : str, optional
            The direction to calculate deff in. The default is 'y'.

        Returns
        -------
        float
            The average depth of the rebar within the group.

        """
        
        bar = self[0]
        lUnit = bar._validateLunit(lUnit)
        lfactor = bar.lConvert(lUnit)     
        
        if direction == 'y':
            return bar.xy[1] * lfactor
        elif direction == 'x':
            return bar.xy[0] * lfactor

class RebarCollection:
    
    def __init__(self, groups:list[RebarGroup]):
        self.groups = groups
        self.Nbars = sum([len(group) for group in self.groups])
    
    # TODO: DOCUMENT
    def addBars(self, groups:list[RebarGroup]):
        if not self.groups:
            self.groups = groups
        else:
            self.groups += groups
        self.Nbars = sum([len(group) for group in self.groups])
        
    
    def __len__(self):
        return len(self.groups)
    
    @property
    def mat(self):
        return self.groups[0].mat
    
    @property
    def coords(self):
        coordsTmp = []
        for group in self.groups:
            coordsTmp.append(group.getAttr('xy'))
        return coordsTmp
        # return np.array(coordsTmp)
    
    @property
    def coordsFlat(self):
        return np.concatenate(self.coords)
        
    def listAttrs(self):
        """        Lists the rebar attributes.        """
        return self.group[0].listAttrs()
        
    def getAttr(self, attribute:str, flatten=False):
        """  For each group, return a list of the input attribute. """        
        attrs = []
        if flatten:
            for group in self.groups:
                attrs += list(group.getAttr(attribute))            
        else:
            for group in self.groups:
                attrs.append(group.getAttr(attribute))

        return attrs  
    
    def getCoords(self, lUnit = '', flatten=False):
        """ Returns an array of the rebar coordinants. """
        coords = []        
        for group in self.groups:
            coords.append(group.getCoords(lUnit))
        
        if flatten:
            return np.concatenate(coords)
        else:
            return np.array(coords)
            
    
    def _getDirCoords(self, ind,  lUnit = '', flatten=False):
        """ Returns an array of the rebar coordinants. """
        if flatten:
            return self.getCoords(lUnit, flatten)[:,ind]
        else:
            return self.getCoords(lUnit, flatten)[:,:,ind]
    
    def getyCoords(self,  lUnit = '', flatten=False):
        """ Returns an array of the rebar coordinants. """
        return self._getDirCoords(1, lUnit, flatten)
        
    def getxCoords(self, lUnit = '', flatten=False):
        """ Returns an array of the rebar coordinants. """
        return self._getDirCoords(0, lUnit, flatten)



        # if flatten:
        #     return np.concatenate(coords)
        # else:
        #     return coords
    # TODO: FIX THE DIRECTION
    def getdeff(self, direction = 'y', lUnit = ''):
        """
        Calcualtes the effective depth of a rebar group, which
        is the average position of the rebar.

        Parameters
        ----------
        direction : str, optional
            The direction to calculate deff in. The default is 'y'.

        Returns
        -------
        float
            The average depth of the rebar within the group.

        """
        
        dA = 0
        A = 0
        for group in self.groups:
            Atemp = group.getNetArea(lUnit)
            dA += group.getdeff(direction, lUnit) * Atemp
            A  += Atemp
            
        return dA / A
        # if direction == 'y':
        #     return np.average(self.getyCoords())
        # elif direction == 'x':
        #     return np.average(self.getxCoords())
            
    def getAreas(self, lUnit = ''):  
        areas = []
        for group in self.groups:
            areas.append(group.getAreas(lUnit))
            
        return areas

        
    def getNetArea(self, lUnit = ''):
        
        areaGroups = self.getAreas(lUnit)
        area = 0
        for aGroup in areaGroups:
            area += sum(aGroup)
        return area

class RebarFactory:
    
    def __init__(self, mat: MaterialElastic, dbConfig: DBConfig, lUnit: str):
        self.mat = mat
        self._loadDB(dbConfig)
        self._initUnits(lUnit)
        
        self.dbcFactor = 1
        
    def _initUnits(self, lUnit: str = None):
        """
        Initiates units of the cross sections. Cross sections have length units
        only.

        Parameters
        ----------
        lUnit : str, optional
            The length unit to use. The default is 'mm'.
        """
        if not lUnit:
            lUnit = 'mm'
        self.lUnit      = lUnit
        self.lConverter = ConverterLength()
    
    def lConvert(self, outputUnit:str):
        """
        Get the conversion factor from the current unit to the output unit
        for length units
        
        Parameters
        ----------
        outputUnit : str
            The unit to get the conversion factor to.

        Returns
        -------
        float
            The conversion factor between the current length unit and the
            target output length unit.

        """

        return self.lConverter.getConversionFactor(self.lUnit, outputUnit)
        
    def _loadDB(self, config:DBConfig):
            
        matdb = _loadSectionDBDict(config)   
        tmpDict = matdb.to_dict(orient='index')
        self.dbDict = {tmpDict[key]['name']:tmpDict[key] for key in tmpDict}
        self.barTypes = [tmpDict[key]['name'] for key in tmpDict]

    def getRebar(self, barType:str, xy:tuple = None, lUnit = None) -> Rebar:
        """
        Gets a rebar of the input bar type, with propreties from the rebar
        database.
        Units in the database will be overwritten by the specified unit if 
        they are different.

        Parameters
        ----------
        barType : str
            The bar type to create.
        xy : tuple, optional
            The location of the rebar from the bottom left point in the secton. 
            The default is None.
        lUnit : TYPE, optional
            The output units desired for the rebar. The default is None.
            Units in the database will be overwritten by the specified unit
            if they are different.


        Returns
        -------
        Rebar
            DESCRIPTION.

        """
        
        try:
            barParams = self.dbDict[barType]
        except:
            raise Exception(f'{barType} not found in database')
        
        cFactor = self.dbcFactor
        if lUnit and self.lUnit != lUnit:
            cFactor *= self.lConverter.getConversionFactor(self.lUnit, lUnit)
            # cFactor *= self.cFactor
            
        rebar = Rebar(self.mat, 
                        barParams['name'], 
                        barParams['d'] * cFactor, 
                        barParams['dnet'] * cFactor, 
                        barParams['A'] * cFactor**2,
                        rcurve = barParams['rcurve'] * cFactor,
                        # barParams['A'] * cFactor**2,
                        lUnit = self.lUnit)
     
        if xy:
            rebar.setxy(xy)
        return rebar
        
    def setMaterial(self, mat:MaterialElastic):
        self.mat = mat
        
    def setLunit(self, lUnit):
        self.dbcFactor = self.lConverter.getConversionFactor(self.lUnit, lUnit)
        self.lUnit = lUnit


class StirrupGroup:
    rebar:Rebar
    rStirrup:float
    dstirrup:float
    lUnit:str

    def __init__(self, rebar:Rebar):
        self.rebar = rebar
        


