# it is time to place some ore

from __future__ import division
from pymclevel import materials
from random import randint
from multiprocessing import Value
from time import clock
from scipy.special import cbrt
from math import pi
from mcmap import getBlockAt, getBlocksAt, setBlocksAt, arrayBlocks

# http://www.minecraftwiki.net/wiki/Ore
oreType = {
    0: 'Dirt',
    1: 'Gravel',
    2: 'Coal',
    3: 'Iron',
    4: 'Gold', 
    5: 'Diamond',
    6: 'Redstone',
    7: 'Lapis Lazuli'
}
oreDepth = [7, 7, 7, 6, 5, 4, 4, 4]
oreValue = [3, 13, 16, 15, 14, 56, 73, 21]
# http://www.minecraftforum.net/viewtopic.php?f=35&t=28299
# "rounds" is how many times per chunk a deposit is generated
# "size" is the rough max size of a deposit
# user guide says (size/4)*(size/4)*(2+size/8)
# I am insane. I model an ideal ellipsoid.  Yay!
# BTW: LL round value of 3 a guess.
oreRounds = [20, 10, 20, 20, 2, 1, 8, 3]
oreSize = [32, 32, 16, 8, 8, 7, 7, 7]
# statistics tracks nodes and veins
oreNodeCount = {}
oreVeinCount = {}
for key in oreType.keys():
    oreNodeCount[key] = Value('i', 0)
    oreVeinCount[key] = Value('i', 0)
# any ore that tries to replace these blocks is hereby disqualified
# air, water, lava
# FIXME: this is not working!
oreDQ = [0, 8, 9, 10, 11]

# whole-world approach
def placeOre(minX, minZ, maxX, maxZ):
    placestart = clock()
    numChunks = len(arrayBlocks.keys())
    for ore in oreType.keys():
        print "Adding %s now..." % (oreType[ore])
        # everything starts on the bottom
        # only doing common pass here
        minY = 0
        maxY = pow(2,oreDepth[ore])
        maxExtent = cbrt(oreSize[ore])/2
        numRounds = int(oreRounds[ore]*numChunks)
        for round in xrange(numRounds):
            clumpX = randint(int(maxExtent*100),int(maxExtent*900))/1000
            clumpY = randint(int(maxExtent*100),int(maxExtent*900))/1000
            clumpZ = randint(int(maxExtent*100),int(maxExtent*900))/1000
            clumpScale = ((4/3)*pi*clumpX*clumpY*clumpZ)/oreSize[ore]
            # dunno about these boundaries
            clumpX = min(max(0.5, (clumpX/clumpScale)), maxExtent)
            clumpY = min(max(0.5, (clumpY/clumpScale)), maxExtent)
            clumpZ = min(max(0.5, (clumpZ/clumpScale)), maxExtent)
            oreX = randint(int(minX+clumpX),int(maxX-clumpX))
            oreY = randint(int(minY+clumpY),int(maxY-clumpY))
            oreZ = randint(int(minZ+clumpZ),int(maxZ-clumpZ))
            oXrange = xrange(int(0-clumpX), int(clumpX+1))
            oYrange = xrange(int(0-clumpX), int(clumpX+1))
            oZrange = xrange(int(0-clumpX), int(clumpX+1))
            # consider air/water/lava exemption here!
            oreCoords = [[oreX+x, oreY+y, oreZ+z] for x in oXrange for y in oYrange for z in oZrange if ((((x*x)/(clumpX*clumpX))+((y*y)/(clumpY*clumpY))+((z*z)/(clumpZ*clumpZ)))<=1) and getBlockAt(oreX+x, oreY+y, oreZ+z) not in ['Air', 'Water', 'Stationary Water', 'Lava', 'Stationary Lava']]
            oreBlocks = getBlocksAt(oreCoords)
            # FIXME: this does not exclude air/water/lava
            if ('Stone' in oreBlocks and len(set(oreBlocks).intersection(set(oreDQ))) == 0 and len(set(oreBlocks).intersection(set(oreType.values()))) == 0):
                #print "    success!"
                oreNodeCount[ore].value += len(oreCoords)
                oreVeinCount[ore].value += 1
                setBlocksAt([x, y, z, materials.names[oreValue[ore]]] for x, y, z in oreCoords)
        print "... %d veins totalling %d units placed." % (oreVeinCount[ore].value, oreNodeCount[ore].value)
    print "finished in %.2f seconds." % (clock()-placestart)

def printOreStatistics():
    oreTuples = [(oreType[index], oreNodeCount[index].value, oreVeinCount[index].value) for index in oreNodeCount if oreNodeCount[index].value > 0]
    oreNodeTotal = sum([oreTuple[1] for oreTuple in oreTuples])
    oreVeinTotal = sum([oreTuple[2] for oreTuple in oreTuples])
    print 'Ore statistics (%d total nodes, %d total veins):' % (oreNodeTotal, oreVeinTotal)
    for key, value, value2 in sorted(oreTuples, key=lambda ore: ore[1], reverse=True):

        print '  %d (%d veins): %s' % (value, value2, key)
