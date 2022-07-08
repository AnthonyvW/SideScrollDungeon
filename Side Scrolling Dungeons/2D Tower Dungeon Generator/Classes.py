from opensimplex import OpenSimplex
import math
import random

def split(x, n):
    #splits x into n numbers as close to each other as possible
    # Gotten from here https://www.geeksforgeeks.org/split-the-number-into-n-parts-such-that-difference-between-the-smallest-and-the-largest-part-is-minimum/
    result = []
    if (x < n):
        return [-1]
    elif (x % n == 0):
        for i in range(n):
            result.append(x // n)
    else:
        zp = n - (x % n)
        pp = x // n
        for i in range(n):
            if (i >= zp):
                result.append(pp + 1)
            else:
                result.append(pp)
    return result

class Tower:
    def __init__(self, xpos, width, height):
        # Tower Initial Position
        self.XPos = xpos
        self.width = width
        self.height = height
        # Tower Data
        self.minLandHeight = 0
        self.maxLandHeight = 0

    def GenerateTower(self, world, YEdgeTolerance):
        # Generate Central Tower Pillar
        self.minLandHeight = world.height
        y = world.height - YEdgeTolerance - 1
        atBottom = False
        atTop = False
        while ((not atBottom or not atTop) and YEdgeTolerance < y):
            offset = int(self.width / 2)
            tally = 0
            for XCol in range(self.width):
                if (world.worldData[self.XPos - offset][y] != 0):
                    tally += 1
                    if (tally == self.width):
                        atBottom = True
                    if (self.minLandHeight > y):
                        self.minLandHeight = y
                    if (self.maxLandHeight < y):
                        self.maxLandHeight = y
                        if(self.maxLandHeight + self.height > world.height - YEdgeTolerance):
                            self.height = int(math.fabs(self.maxLandHeight - (world.height - YEdgeTolerance)))
                elif (atBottom):
                    if (y == self.maxLandHeight + self.height):
                        atTop = True
                    if (y > self.maxLandHeight):
                        world.worldData[self.XPos - offset][y] = 2
                    else:
                        world.worldData[self.XPos - offset][y] = 3

                offset -= 1

            if (not atBottom):
                y -= 1
            else:
                y += 1

    def GenerateBridge(self, world, bHeight, bWidth, bFloorDepth, isRightSide, spawnHeight):
        i = bHeight - bFloorDepth
        i2 = i * i
        flip = 1
        if not isRightSide:
            flip = -1
        for x in range(bWidth):
            x2 = x + 0.5
            for y in range(bHeight - int(math.sqrt((i2*bWidth*x2 - i2*x2*x2)/(0.25*bWidth*bWidth)))):
                if(world.worldData[flip * x + self.XPos + flip * int(self.width / 2) + flip][spawnHeight - y] != 1):
                    world.worldData[flip * x + self.XPos + flip * int(self.width / 2) + flip][spawnHeight - y] = 4

    def GeneratePillarBridge(self, world, bHeight, bWidth, bFloorDepth, isRightSide, spawnHeight, maxDist):

        self.GenerateBridge(world, bHeight, bWidth, bFloorDepth, isRightSide, spawnHeight)

class World:
    def __init__(self, worldWidth, worldHeight, Seed = 0):
        self.width = worldWidth
        self.height = worldHeight
        self.simplex = OpenSimplex(Seed)

        self.dungeons = []
        self.worldData = []
        for x in range(self.width):
            self.worldData.append([])
            for y in range(self.height):
                self.worldData[x].append(0)

    def GenerateTerrain(self, defAmplitude = 128, defScale = 1):
        # Create Land
        for x in range(self.width):
            Output = 0
            amplitude = defAmplitude
            scale = defScale
            for i in range(5):
                Output += self.simplex.noise2d(x / amplitude, 0) / scale
                scale *= 2
                amplitude /= 2

            Output = int(Output * 64 + 128)
            for y in range(Output):
                self.worldData[x][y] = 1

    def CreateDungeon(self, numTowers,towerWidth ,towerDistanceFromEdge, XEdgeTolerance, YEdgeTolerance):
        self.dungeons.append(Dungeon(self,numTowers,towerWidth ,towerDistanceFromEdge, XEdgeTolerance, YEdgeTolerance))

class Dungeon:
    def __init__(self, world, numTowers = 3,towerWidth = 31,towerDistanceFromEdge = 30, XEdgeTolerance = 50, YEdgeTolerance = 30):
        self.towerDistFromEdge = towerDistanceFromEdge
        self.towers = []
        self.walkwayHeight = 5
        self.minBridgeArchHeight = 15
        self.maxBridgeArchHeight = 45
        # Tolerance between Dungeon and World edges
        self.XEdgeTolerance = XEdgeTolerance
        self.YEdgeTolerance = YEdgeTolerance
        # Check if Pillar Properties even make sense. Raise error and quit if they don't.
        try:
            if (numTowers * towerDistanceFromEdge + numTowers * towerWidth + XEdgeTolerance * 2 > world.width):
                raise ValueError
            else:
                print("\tTotal Requested Width =",
                      numTowers * towerDistanceFromEdge + numTowers * towerWidth + XEdgeTolerance * 2)
                print("\tWorld Width =", world.width)
        except:
            print("\nInvalid Pillar Properties:")
            print("\tTotal Requested Width =",
                  numTowers * towerDistanceFromEdge + numTowers * towerWidth + XEdgeTolerance * 2)
            print("\tWorld Width =", world.width)
            print("\tAmount Exceeding Width =",
                  numTowers * towerDistanceFromEdge + numTowers * towerWidth + XEdgeTolerance * 2 - world.width)
            quit()

        for i in range(numTowers):
            # Generate Tower Locations in valid spots
            position = 0
            isValid = False
            while (not isValid):
                position = random.randint(XEdgeTolerance - 1, world.width - XEdgeTolerance - 1)
                isValid = True
                for twr in self.towers:
                    if (math.fabs(twr.XPos - position) - towerWidth < towerDistanceFromEdge):
                        isValid = False
                        break
            else:
                self.towers.append(Tower(position, towerWidth, random.randint(90,260)))

            # Generate the Tower itself
            self.towers[i].GenerateTower(world, self.YEdgeTolerance)

        self.towers.sort(key=lambda x: x.XPos)
        self.GenTowerBridge(world, 1, 0)
        self.GenTowerBridge(world, 1, 2)
        self.GenTowerBridge(world, 2, 3)
    def __GenTowerHeightAndSpawn(self, t1i, t2i):
        maxSpawnHeight = 0
        minSpawnHeight = 0
        bridgeHeight = random.randint(self.minBridgeArchHeight + self.walkwayHeight,
                                      self.maxBridgeArchHeight + self.walkwayHeight)
        if (self.towers[t1i].height + self.towers[t1i].maxLandHeight < self.towers[t2i].height + self.towers[
            t2i].maxLandHeight):
            maxSpawnHeight = self.towers[t1i].height + self.towers[t1i].maxLandHeight
        else:
            maxSpawnHeight = self.towers[t2i].height + self.towers[t2i].maxLandHeight
        if (self.towers[t1i].maxLandHeight > self.towers[t2i].maxLandHeight):
            minSpawnHeight = self.towers[t1i].maxLandHeight
        else:
            minSpawnHeight = self.towers[t2i].maxLandHeight
        if (minSpawnHeight + bridgeHeight > maxSpawnHeight):
            if (not minSpawnHeight + self.walkwayHeight > maxSpawnHeight):
                bridgeHeight = int(math.fabs(minSpawnHeight + self.walkwayHeight - maxSpawnHeight))
                if (bridgeHeight > self.maxBridgeArchHeight):
                    bridgeHeight = self.maxBridgeArchHeight
                elif (bridgeHeight < self.minBridgeArchHeight):
                    print("INVALID BRIDGE HEIGHT")
                    return
            else:
                print("INVALID BRIDGE HEIGHT")
                return

        bSpawnHeight = random.randint(minSpawnHeight + bridgeHeight, maxSpawnHeight)
        return (bridgeHeight, bSpawnHeight)
    def GenTowerBridge(self, world, t1i, t2i):
        if(t1i == t2i): return
        bridgeHeight, bSpawnHeight = self.__GenTowerHeightAndSpawn(t1i, t2i)
        if(self.towers[t1i].XPos < self.towers[t2i].XPos):
            self.towers[t1i].GenerateBridge(world,
                                            bridgeHeight,
                                            int(math.fabs((self.towers[t2i].XPos - self.towers[t2i].width / 2) - (self.towers[t1i].XPos + self.towers[t1i].width / 2))),
                                            self.walkwayHeight,
                                            True,
                                            bSpawnHeight
                                            )
        else:
            self.towers[t2i].GenerateBridge(world,
                                            bridgeHeight,
                                            int(math.fabs((self.towers[t1i].XPos - self.towers[t1i].width / 2) - (self.towers[t2i].XPos + self.towers[t2i].width / 2))),
                                            self.walkwayHeight,
                                            True,
                                            bSpawnHeight
                                            )