from random import randint, random
from time import sleep
from aclib.winlib import winapi


__all__ = [
    'screen'
]


def random_divide(number: float, bynum: int, returnfloat: bool=True):
    nodes = []
    for i in range(bynum-1):
        node = random()*number
        if not returnfloat: node = int(node)
        nodes.append(node)
    nodes.append(number)
    nodes.sort(key=lambda _node:abs(_node))
    results = []
    for i in range(bynum):
        if i==0: results.append(nodes[i])
        else: results.append(nodes[i] - nodes[i-1])
    return results

class Screen(object):
    @property
    def size(self):
        return winapi.GetScreenSize()

    @property
    def mousepos(self):
        return winapi.GetCursorPos()

    def movemouse(self, topos: tuple[int,int]):
        winapi.SetCursorPos(topos)

    def movemouse_likehuman(self, topos: tuple[int,int], minduration: float=0.1, maxduration=0.7):
        startx, starty = self.mousepos
        endx, endy = topos
        xdistance = abs(startx-endx)
        ydistance = abs(starty-endy)
        nmove = randint(int(min(xdistance, ydistance)/2), max(xdistance, ydistance))
        dxlist = random_divide(endx-startx, nmove, returnfloat=False)
        dylist = random_divide(endy-starty, nmove, returnfloat=False)
        dtlist = random_divide(minduration + random() * (maxduration - minduration), nmove, returnfloat=True)
        for dx, dy, dt in zip(dxlist, dylist, dtlist):
            sleep(dt)
            nextpos = startx + dx, starty + dy
            self.movemouse(nextpos)
            startx, starty = nextpos

screen = Screen()
