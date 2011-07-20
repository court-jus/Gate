#!/usr/bin/env ppython
# -*- coding: utf-8 -*-

from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3, VBase3, BitMask32, Vec3, Plane
from panda3d.core import CollisionTraverser,CollisionNode,CollisionSphere,CollisionPlane
from panda3d.core import CollisionHandlerQueue,CollisionRay
import sys

def degtorad(deg):
    return deg * (pi / 180)

class Mass(object):
    def __init__(self, m):
        self.mass = m
        self.pos = VBase3(0,0,2)
        self.vel = VBase3(0,0,0)
        self.force = VBase3(0,0,0)

    def applyForce(self, force):
        self.force += force

    def simulate(self, dt):
        self.vel += (self.force / self.mass) * dt
        self.pos += self.vel * dt

    def __str__(self):
        return "%s %s %s" % (self.pos, self.vel, self.force)

class PandaHW(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        self.environ = self.loader.loadModel("models/environment")
        self.environ.reparentTo(self.render)
        self.environ.setScale(0.25, 0.25, 0.25)
        self.environ.setPos(-8, 42, 0)

        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
        self.taskMgr.add(self.moveCameraTask, "MoveCameraTask")
        self.taskMgr.add(self.playerGravity, "PlayerGravity")

        #self.stuff = Actor("models/panda-model")
        #self.stuff.setScale(0.005, 0.005, 0.005)
        #self.stuff.setPos(-1.3, 19., 0.5)
        #self.stuff.reparentTo(self.render)

        self.pandaActor = Actor("models/panda-model",
                                {"walk": "models/panda-walk4"})
        self.pandaActor.setScale(0.005, 0.005, 0.005)
        self.pandaActor.reparentTo(self.render)

        cs = CollisionSphere(-1.3, 19, 0.5, 2.5)
        pl = CollisionPlane(Plane(Vec3(0,0,1), Point3(0,0,0.2)))
        ray = CollisionRay(self.pandaActor.getPos(), Vec3(0,0,-1))
        cnodePath = self.render.attachNewNode(CollisionNode('cnode'))
        cnodePath.node().addSolid(cs)
        cnodePath.node().addSolid(pl)
        cnodePath.node().addSolid(ray)
        cnodePath.show()

        self.camera.reparentTo(self.pandaActor)
        self.camera.setPos(0., -450., 400.)

        self.camAlpha = 180
        self.camBeta = 0
        self.moving = []
        self.playerAltitude = 0
        self.jumping = False
        self.inJump = False
        self.playerFallingSpeed = 0
        self.player = Mass(80)
        self.cTrav = CollisionTraverser()
        self.ralphGroundRay = CollisionRay()
        self.ralphGroundRay.setOrigin(0,0,1000)
        self.ralphGroundRay.setDirection(0,0,-1)
        self.ralphGroundCol = CollisionNode('ralphRay')
        self.ralphGroundCol.addSolid(self.ralphGroundRay)
        self.ralphGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.ralphGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.ralphGroundColNp = self.camera.attachNewNode(self.ralphGroundCol)
        self.ralphGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.ralphGroundColNp, self.ralphGroundHandler)
        self.ralphGroundColNp.show()

        base.disableMouse( ) # disable the default camera controls that are created for us
        self.keyBoardSetup()
    # A task is a procedure that is called every frame
    def spinCameraTask(self, task):
        rotation_speed = 20
        invert_camY = True
        w, h = self.getSize()
        if base.mouseWatcherNode.hasMouse():
            cx = base.mouseWatcherNode.getMouseX()
            cy = base.mouseWatcherNode.getMouseY()
            self.camAlpha -= cx * rotation_speed
            self.camBeta  -= (cy * rotation_speed) * (-1 if invert_camY else 1)
        for win in self.winList:
            if win.hasPointer(0):
                win.movePointer(0,w/2,h/2)
        self.pandaActor.setHpr(self.camAlpha, 0., 0.)
        self.camera.setHpr(180., self.camBeta, 0.)
        return Task.cont
    def moveCameraTask(self, task):
        walk_speed = -1
        newX = self.pandaActor.getX()
        newY = self.pandaActor.getY()
        newZ = self.pandaActor.getZ()
        if self.moving:
            self.pandaActor.loop("walk")
        else:
            self.pandaActor.stop()
        if 1 in self.moving: # Forward
            newX -= sin(degtorad(self.camAlpha)) * walk_speed
            newY += cos(degtorad(self.camAlpha)) * walk_speed
            #newZ += sin(degtorad(self.camBeta))  * walk_speed
        if 2 in self.moving: # Backward
            newX += sin(degtorad(self.camAlpha)) * walk_speed
            newY -= cos(degtorad(self.camAlpha)) * walk_speed
            #newZ -= sin(degtorad(self.camBeta))  * walk_speed
        if 3 in self.moving: # left
            newX -= cos(degtorad(self.camAlpha)) * walk_speed
            newY -= sin(degtorad(self.camAlpha)) * walk_speed
        if 4 in self.moving: # right
            newX += cos(degtorad(self.camAlpha)) * walk_speed
            newY += sin(degtorad(self.camAlpha)) * walk_speed
        newZ -= self.playerFallingSpeed
        #if newZ >= (self.playerAltitude - 0.1) and newZ <= (self.playerAltitude + 0.1) and not self.jumping: # Tolerance
        #    newZ = self.playerAltitude
        self.pandaActor.setPos(newX, newY, newZ)
        self.player.pos = VBase3(newX, newY, newZ)
        return Task.cont
    def move(self, direction):
        if direction < 0 and -direction in self.moving:
            self.moving.remove(-direction)
        else:
            self.moving.append(direction)
    def playerGravity(self, task):
        self.player.simulate(task.time)
        self.pandaActor.setPos(self.player.pos)
        z = self.player.pos.getZ()
        pa = self.playerAltitude
        if self.jumping and z >= (pa - 0.1) and z <= (pa + 0.1): # Tolerance
            self.inJump = True
            self.player.vel = VBase3(0, 0, 0.05)
            self.player.force = VBase3(0, 0, 0)
        if z > pa:
            if z > pa + 0.1: # Fall
                self.player.applyForce(VBase3(0, 0, -0.0005))
            elif not self.jumping: # Come back quickly to 0
                self.player.pos.setZ(pa)
                self.player.force.setZ(0.)
                self.player.vel.setZ(0.)
        elif z < pa:
            # Come back quickly to 0
            self.player.pos.setZ(pa)
            self.player.force.setZ(0.)
            self.player.vel.setZ(0.)
            self.inJump = False
            self.playerAltitude = self.player.pos.getZ()
        return Task.cont
        if self.jumping and z >= (self.playerAltitude - 0.1) and z <= (self.playerAltitude + 0.1): # Tolerance
            self.player.applyForce(VBase3(0, 0, 1))
        return Task.cont
        gravityCoef = 9.81 * 0.0001
        if self.camera.getZ() > self.playerAltitude:
            self.playerFallingSpeed += gravityCoef
        elif self.camera.getZ() < self.playerAltitude:
            self.playerFallingSpeed = 0
        else:
            #self.jumping = False
            self.playerFallingSpeed = 0
        if self.jumping and self.camera.getZ() >= (self.playerAltitude - 0.1) and self.camera.getZ() <= (self.playerAltitude + 0.1): # Tolerance
            self.playerFallingSpeed -= 9.81 * 0.01
        return Task.cont
    def jump(self, jumping = True):
        self.jumping = jumping
    def keyBoardSetup( self ):
        self.accept("escape", sys.exit )
        key_directions = {
            "arrow_up": 1, "z" : 1,
            "arrow_down": 2, "s" : 2,
            "arrow_left": 3, "q" : 3,
            "arrow_right": 4, "d" : 4,
            }
        for key_name, direction in key_directions.items():
            self.accept(key_name, self.move, [direction])
            self.accept("%s-up" % (key_name,), self.move, [-direction])
        self.accept("space", self.jump, [True])
        self.accept("space-up", self.jump, [False])


if __name__ == "__main__":
    app = PandaHW()
    app.run()
