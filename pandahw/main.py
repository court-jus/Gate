#!/usr/bin/env ppython
# -*- coding: utf-8 -*-

from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBase import messenger
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3, VBase3, BitMask32, Vec3, Plane
from panda3d.core import CollisionTraverser,CollisionNode,CollisionSphere,CollisionPlane
from panda3d.core import CollisionHandlerQueue,CollisionRay,CollisionHandlerEvent, CollisionHandlerPusher
from panda3d.core import CollisionHandlerFloor
import sys

def degtorad(deg):
    return deg * (pi / 180)

class Mass(object):
    def __init__(self, m):
        self.mass = m
        self.pos = VBase3(0,0,2)
        self.vel = VBase3(0,0,0)
        self.force = VBase3(0,0,0)
        self.grav = VBase3(0,0,-0.00005)

    def applyForce(self, force):
        self.force += force

    def simulate(self, dt):
        self.vel += ((self.force + self.grav) / self.mass) * dt
        self.pos += self.vel * dt

    def __str__(self):
        return "%s %s %s" % (self.pos, self.vel, self.force)

class PandaHW(ShowBase):

    def __init__(self):
        messenger.toggleVerbose()

        ShowBase.__init__(self)

        self.environ = self.loader.loadModel("models/falcon")
        self.environ.reparentTo(self.render)
        self.environ.setScale(0.25, 0.25, 0.25)
        self.environ.setPos(-8, 42, 0)

        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
        self.taskMgr.add(self.moveCameraTask, "MoveCameraTask")
        self.taskMgr.add(self.playerGravity, "PlayerGravity")
        #self.taskMgr.add(self.collTask, "CollisionTask")


        self.pandaActor = Actor("models/panda-model",
                                {"walk": "models/panda-walk4"})
        self.pandaActor.setScale(0.005, 0.005, 0.005)
        self.pandaActor.setPos(0, 0, 10)
        self.pandaActor.reparentTo(self.render)

        # Initialize the collision traverser.
        self.cTrav = CollisionTraverser()
        self.cTrav.showCollisions(self.render)
         
        # Initialize the Pusher collision handler.
        pusher = CollisionHandlerPusher()
 
        # Create a collision node for this object.
        cNode = CollisionNode('panda')
        # Attach a collision sphere solid to the collision node.
        cNode.addSolid(CollisionSphere(0, 0, 0, 600))
        # Attach the collision node to the object's model.
        pandaC = self.pandaActor.attachNewNode(cNode)
        # Set the object's collision node to render as visible.
        pandaC.show()
 
        # Create a collsion node for this object.
        cNode = CollisionNode('environnement')
        # Attach a collision sphere solid to the collision node.
        cNode.addSolid(CollisionSphere(-1.3, 19, 0.5, 2.5))
        cNode.addSolid(CollisionPlane(Plane(Vec3(0,0,1), Point3(0,0,0.2))))
        # Attach the collision node to the object's model.
        environC = self.environ.attachNewNode(cNode)
        # Set the object's collision node to render as visible.
        environC.show()
 
        # Add the Pusher collision handler to the collision traverser.
        self.cTrav.addCollider(pandaC, pusher)
        # Add the 'frowney' collision node to the Pusher collision handler.
        pusher.addCollider(pandaC, self.environ, base.drive.node())
         
        fromObject = self.pandaActor.attachNewNode(CollisionNode('colNode'))
        fromObject.node().addSolid(CollisionRay(0, 0, 0, 0, 0, -1))
        lifter = CollisionHandlerFloor()
        lifter.addCollider(fromObject, self.pandaActor)
        self.cTrav.addCollider(pandaC, lifter)

        # Have the 'smiley' sphere moving to help show what is happening.
        #frowney.posInterval(5, Point3(5, 25, 0), startPos=Point3(-5, 25, 0), fluid=1).loop()
 
        #self.stuff = Actor("models/panda-model")
        #self.stuff.setScale(0.005, 0.005, 0.005)
        #self.stuff.setPos(-1.3, 19., 0.5)
        #self.stuff.reparentTo(self.render)

#        cTrav = CollisionTraverser()
#        ceh = CollisionHandlerQueue()
#        #ceh.addInPattern('%fn-into-%in')
#        #ceh.addAgainPattern('%fn-again-%in')
#        #ceh.addOutPattern('%fn-outof-%in')
#        self.pandaColl = self.pandaActor.attachNewNode(CollisionNode('cnode'))
#        self.pandaColl.node().addSolid(CollisionSphere(self.pandaActor.getChild( 0 ).getBounds( ).getCenter(), 400))
#        self.pandaColl.show()
#        cTrav.addCollider( self.pandaColl, ceh )
#        self.cTrav = cTrav
#        self.cTrav.showCollisions(self.render)
#        self.queue = ceh
#        cs = CollisionSphere(-1.3, 19, 0.5, 2.5)
#        pl = CollisionPlane(Plane(Vec3(0,0,1), Point3(0,0,0.2)))
#        # ray = CollisionRay(self.pandaActor.getPos(), Vec3(0,0,-1))
#        cnodePath = self.render.attachNewNode(CollisionNode('cnode'))
#        # rayNodePath = self.render.attachNewNode(CollisionNode('raynode'))
#        cnodePath.node().addSolid(cs)
#        cnodePath.node().addSolid(pl)
#        # rayNodePath.node().addSolid(ray)
#        cnodePath.show()
#        # rayNodePath.show()
#        #rayNodePath.reparentTo(self.pandaActor)
        #self.accept('car-into-rail', handleRailCollision)
        #cTrav.addCollider(cnodePath, ceh)

        self.camera.reparentTo(self.pandaActor)
        self.camera.setPos(0., 1050., 1000.)

        self.camAlpha = 180
        self.camBeta = 0
        self.moving = []
        self.playerAltitude = 0
        self.jumping = False
        self.inJump = False
        self.playerFallingSpeed = 0
        self.player = Mass(80)
        base.useDrive()
        #base.disableMouse( ) # disable the default camera controls that are created for us
        self.keyBoardSetup()
    def collEvent(self, entry):
        print "Collide event", entry
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
        self.pandaActor.setHpr(self.camAlpha, self.camBeta, 0.)
        self.camera.setHpr(180., -self.camBeta, 0.)
        return Task.cont
    def moveCameraTask(self, task):
        walk_speed = 1
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
            newZ += sin(degtorad(self.camBeta))  * walk_speed
        if 2 in self.moving: # Backward
            newX += sin(degtorad(self.camAlpha)) * walk_speed
            newY -= cos(degtorad(self.camAlpha)) * walk_speed
            newZ -= sin(degtorad(self.camBeta))  * walk_speed
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
