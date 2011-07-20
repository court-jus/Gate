# -*- coding: utf-8 -*-
import direct.directbase.DirectStart 
from direct.showbase.DirectObject import DirectObject 
from pandac.PandaModules import * 
from direct.interval.IntervalGlobal import LerpFunc 
import sys 

class FPS(object,DirectObject): 
    def __init__(self): 
        self.winXhalf = base.win.getXSize()/2 
        self.winYhalf = base.win.getYSize()/2 
        self.initCollision() 
        self.loadLevel() 
        self.initPlayer() 

    def initCollision(self): 
        #initialize traverser 
        base.cTrav = CollisionTraverser() 
        base.cTrav.setRespectPrevTransform(True) 
#         base.cTrav.showCollisions(render) 
        #initialize pusher 
        self.pusher = CollisionHandlerPusher() 
        # collision bits 
        self.groundCollBit = BitMask32.bit(0) 
        self.collBitOff = BitMask32.allOff() 

    def loadLevel(self): 

        #load level 
        # must have 
        #<Group> *something* { 
        #  <Collide> { Polyset keep descend } in the egg file 
        level = loader.loadModel("models/environment") 
        level.reparentTo(render) 
        level.setPos(0,0,0) 
        level.setColor(1,1,1,.5) 

    def initPlayer(self): 
        #load man 
        self.man = render.attachNewNode('man') # keep this node scaled to identity 
        self.man.setPos(0,0,0) 
        # should be avatar model 
#         model = loader.loadModel('teapot') 
#         model.reparentTo(self.man) 
#         model.setScale(.05) 
        # camera 
        base.camera.reparentTo(self.man) 
        base.camera.setPos(0,0,1.7) 
        base.camLens.setNearFar(.1,1000) 
        base.disableMouse() 
        #create a collsion solid around the man 
        manC = self.man.attachCollisionSphere('manSphere', 0,0,1, .4, self.groundCollBit,self.collBitOff) 
        self.pusher.addCollider(manC,self.man) 
        base.cTrav.addCollider(manC,self.pusher) 

        speed = 4 
        Forward = Vec3(0,speed*2,0) 
        Back = Vec3(0,-speed,0) 
        Left = Vec3(-speed,0,0) 
        Right = Vec3(speed,0,0) 
        Stop = Vec3(0) 
        self.walk = Stop 
        self.strife = Stop 
        self.jump = 0 
        taskMgr.add(self.move, 'move-task') 
        self.jumping = LerpFunc( Functor(self.__setattr__,"jump"), 
                                 duration=.25, fromData=.25, toData=0) 
        self.accept( "escape",sys.exit ) 
        self.accept( "space" , self.startJump) 
        self.accept( "s" , self.__setattr__,["walk",Back] ) 
        self.accept( "w" , self.__setattr__,["walk",Forward]) 
        self.accept( "s-up" , self.__setattr__,["walk",Stop] ) 
        self.accept( "w-up" , self.__setattr__,["walk",Stop] ) 
        self.accept( "a" , self.__setattr__,["strife",Left]) 
        self.accept( "d" , self.__setattr__,["strife",Right] ) 
        self.accept( "a-up" , self.__setattr__,["strife",Stop] ) 
        self.accept( "d-up" , self.__setattr__,["strife",Stop] ) 

        self.manGroundColNp = self.man.attachCollisionRay( 'manRay', 
                                                           0,0,.6, 0,0,-1, 
                                                           self.groundCollBit,self.collBitOff) 
        self.manGroundHandler = CollisionHandlerGravity() 
        self.manGroundHandler.addCollider(self.manGroundColNp,self.man) 
        base.cTrav.addCollider(self.manGroundColNp, self.manGroundHandler) 

    def startJump(self): 
        if self.manGroundHandler.isOnGround(): 
           self.jumping.start() 

    def move(self,task): 
        dt=globalClock.getDt() 
        # mouse 
        md = base.win.getPointer(0) 
        x = md.getX() 
        y = md.getY() 
        if base.win.movePointer(0, self.winXhalf, self.winYhalf): 
            self.man.setH(self.man, (x - self.winXhalf)*-0.1) 
            base.camera.setP( clampScalar(-90,90, base.camera.getP() - (y - self.winYhalf)*0.1) ) 
        # move where the keys set it 
        moveVec=(self.walk+self.strife)*dt # horisontal 
        moveVec.setZ( self.jump )          # vertical 
        self.man.setFluidPos(self.man,moveVec) 
        # jump damping 
        if self.jump>0: 
           self.jump = clampScalar( 0,1, self.jump*.9 ) 

        return task.cont 
FPS() 
render.setShaderAuto() 
run()

