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

    def Arch(self, world, xpos, ypos, width, depth, material):
        xpos = int(xpos)
        ypos = int(ypos)
        i = depth * depth
        iWidth = i * width
        denominator = 0.25 * width * width
        for x in range(width):
            x2 = x + 0.5
            for y in range(depth - int(math.sqrt((iWidth * x2 - i * x2 * x2) / denominator))):
                if (world.worldData[xpos + x][ypos - y] != 1):
                    world.worldData[xpos + x][ypos - y] = material

    def Pillar(self, world, x1, y1, width, material):
        for x in range(width):
            bottom = False
            y = 0
            while not bottom:
                if(world.worldData[x1 + x][y1 + y] == 0):
                    world.worldData[x1 + x][y1 + y] = material
                else:
                    bottom = True
                y -= 1

    def Floor(self, world, x1, y1, width, depth, material):
        for x in range(width):
            for y in range(depth):
                world.worldData[x1 + x][y1 - y] = material

    def GenerateBridge(self, world, Height, Width, FloorDepth, SpawnHeight):
        self.Floor(world, self.XPos + int(self.width / 2) + 1, SpawnHeight, Width, FloorDepth, 5)
        self.Arch(world, self.XPos + int(self.width / 2) + 1, SpawnHeight, Width, Height, 4)

    def GeneratePillarBridge(self, world, Height, Width, FloorDepth, SpawnHeight):
        MaxDist = random.randint(30,100)

        PillarWidth = random.randint(5, 10)
        # Sometimes when the width ends with .5 it doesn't round the correct direction so this stretches it across the remaining gap
        if(world.worldData[self.XPos + math.ceil(self.width / 2) + Width][SpawnHeight] == 0):
            Width += 1
        # Generate Floor of Bridge
        print(math.ceil(self.width / 2), round(self.width / 2), self.width / 2)
        self.Floor(world, self.XPos + math.ceil(self.width / 2), SpawnHeight, Width, FloorDepth, 5)
        if(Width > MaxDist):
            # Generate Arches
            PillarCeil = math.ceil(Width / (MaxDist + PillarWidth) - 1)
            PillarMult = int(PillarWidth * (PillarCeil))
            if(PillarCeil <= 1):
                PillarMult = PillarWidth
                PillarCeil = 1
            ArchWidths = split(Width - PillarMult, PillarCeil + 1)
            ArchSum = 0
            ArchOffset = 0
            for ArchSize in ArchWidths:
                self.Arch(world, self.XPos + math.ceil(self.width / 2) + ArchSum + ArchOffset, SpawnHeight - FloorDepth, ArchSize, Height, 4)
                ArchSum += ArchSize
                ArchOffset += PillarWidth
            # Generate Pillars
            ArchSum = 0
            ArchOffset = 0
            for i in range(len(ArchWidths) - 1):
                ArchSum += ArchWidths[i]
                self.Pillar(world, self.XPos + math.ceil(self.width / 2) + ArchSum + ArchOffset, SpawnHeight - FloorDepth, PillarWidth, 6)
                ArchOffset += PillarWidth
        else:
            self.Arch(world, self.XPos + math.ceil(self.width / 2), SpawnHeight - FloorDepth, Width, Height, 4)

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

    def CreateDungeon(self,towerDistanceFromEdge, XEdgeTolerance, YEdgeTolerance):
        self.dungeons.append(Dungeon(self,towerDistanceFromEdge, XEdgeTolerance, YEdgeTolerance))

class Dungeon:
    def __init__(self, world, towerSpacing = 30, XEdgeTolerance = 50, YEdgeTolerance = 30):
        # Tower
        self.numTowers = 3#random.randint(3,4)
        self.towerDistFromEdge = towerSpacing # How far away they can be from each other
        self.minTowerWidth = 31
        self.maxTowerWidth = 61
        self.towers = []
        # Bridge
        self.walkwayHeight = 5
        self.minBridgeArchHeight = 15
        self.maxBridgeArchHeight = 45
        # Tolerance between Dungeon and World edges
        self.XEdgeTolerance = XEdgeTolerance
        self.YEdgeTolerance = YEdgeTolerance
        # Check if Pillar Properties even make sense. Raise error and quit if they don't.
        try:
            if (self.numTowers * towerSpacing + self.numTowers * self.maxTowerWidth + XEdgeTolerance * 2 > world.width):
                raise ValueError
            else:
                print("\tTotal Requested Width =",
                      self.numTowers * towerSpacing + self.numTowers * self.maxTowerWidth + XEdgeTolerance * 2)
                print("\tWorld Width =", world.width)
        except:
            print("\nInvalid Pillar Properties:")
            print("\tTotal Requested Width =",
                  self.numTowers * towerSpacing + self.numTowers * self.maxTowerWidth + XEdgeTolerance * 2)
            print("\tWorld Width =", world.width)
            print("\tAmount Exceeding Width =",
                  self.numTowers * towerSpacing + self.numTowers * self.maxTowerWidth + XEdgeTolerance * 2 - world.width)
            quit()

        for i in range(self.numTowers):
            # Generate Tower Locations in valid spots
            position = 0
            isValid = False
            attempts = 0 # if the tower fails to generate 100 times, stop attempting to generate it
            towerWidth = random.randint(self.minTowerWidth, self.maxTowerWidth)
            while (not isValid and attempts < 100):
                attempts += 1
                position = random.randint(XEdgeTolerance - 1, world.width - XEdgeTolerance - 1)
                isValid = True
                for twr in self.towers:
                    if (math.fabs(twr.XPos - position) - towerWidth < towerSpacing):
                        isValid = False
                        break
            else:
                if(attempts == 100):
                    self.numTowers -= 1
                else:
                    self.towers.append(Tower(position, towerWidth, random.randint(90,260)))

                    # Generate the Tower itself
                    self.towers[i].GenerateTower(world, self.YEdgeTolerance)

        self.towers.sort(key=lambda x: x.XPos)
        if(len(self.towers) > 1):
            self.GenTowerPillarBridge(world, 1, 0)
        if(len(self.towers) > 2):
            self.GenTowerPillarBridge(world, 1, 2)
        if(len(self.towers) > 3):
            self.GenTowerPillarBridge(world, 2, 3)
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
                    return (-1000000,-1000000)
            else:
                print("INVALID BRIDGE HEIGHT")
                return (-1000000,-1000000)

        bSpawnHeight = random.randint(minSpawnHeight + bridgeHeight, maxSpawnHeight)
        return (bridgeHeight, bSpawnHeight)

    def GenTowerBridge(self, world, t1i, t2i):
        if(t1i == t2i): return
        flip = 1
        bridgeHeight, bSpawnHeight = self.__GenTowerHeightAndSpawn(t1i, t2i)
        if(bridgeHeight == -1000000):
            return
        if(self.towers[t1i].XPos < self.towers[t2i].XPos):
            bridgeWidth = int(math.fabs((self.towers[t2i].XPos - self.towers[t2i].width / 2) - (self.towers[t1i].XPos + self.towers[t1i].width / 2)))
            # Verify that this is a valid location for the walkway of the bridge to spawn
            for x in range(bridgeWidth):
                for y in range(self.walkwayHeight):
                    if(world.worldData[flip * x + self.towers[t1i].XPos + flip * int(self.towers[t1i].width / 2) + flip][bSpawnHeight - y] == 1):
                        return # Returns if Land will intersect walkway
            self.towers[t1i].GenerateBridge(world, bridgeHeight, bridgeWidth, self.walkwayHeight, bSpawnHeight)
        else:
            bridgeWidth = int(math.fabs((self.towers[t1i].XPos - self.towers[t1i].width / 2) - (self.towers[t2i].XPos + self.towers[t2i].width / 2)))
            # Verify that this is a valid location for the walkway of the bridge to spawn
            for x in range(bridgeWidth):
                for y in range(self.walkwayHeight):
                    if(world.worldData[flip * x + self.towers[t2i].XPos + flip * int(self.towers[t2i].width / 2) + flip][bSpawnHeight - y] == 1):
                        return # Returns if Land will intersect walkway
            self.towers[t2i].GenerateBridge(world, bridgeHeight, bridgeWidth, self.walkwayHeight, bSpawnHeight)

    def GenTowerPillarBridge(self, world, t1i, t2i):
        if(t1i == t2i): return
        flip = 1
        bridgeHeight, bSpawnHeight = self.__GenTowerHeightAndSpawn(t1i, t2i)
        if(bridgeHeight == -1000000):
            return
        if(self.towers[t1i].XPos < self.towers[t2i].XPos):
            bridgeWidth = round(math.fabs((self.towers[t2i].XPos - self.towers[t2i].width / 2) - (self.towers[t1i].XPos + self.towers[t1i].width / 2)))
            # Verify that this is a valid location for the walkway of the bridge to spawn
            for x in range(bridgeWidth):
                for y in range(self.walkwayHeight):
                    if(world.worldData[flip * x + self.towers[t1i].XPos + flip * int(self.towers[t1i].width / 2) + flip][bSpawnHeight - y] == 1):
                        return # Returns if Land will intersect walkway
            self.towers[t1i].GeneratePillarBridge(world, bridgeHeight, bridgeWidth, self.walkwayHeight, bSpawnHeight)
        else:
            bridgeWidth = round(math.fabs((self.towers[t1i].XPos - self.towers[t1i].width / 2) - (self.towers[t2i].XPos + self.towers[t2i].width / 2)))
            # Verify that this is a valid location for the walkway of the bridge to spawn
            for x in range(bridgeWidth):
                for y in range(self.walkwayHeight):
                    if(world.worldData[flip * x + self.towers[t2i].XPos + flip * int(self.towers[t2i].width / 2) + flip][bSpawnHeight - y] == 1):
                        return # Returns if Land will intersect walkway
            self.towers[t2i].GeneratePillarBridge(world, bridgeHeight, bridgeWidth, self.walkwayHeight, bSpawnHeight)
