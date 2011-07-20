# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------#
#                                                                            #
# File: room.py                                                              #
#                                                                            #
# Description: This module encapsulates a character in a room.               #
#                                                                            #
# Needed: Panda 1.3.2,                                                       #
#         assets\models\tiny.x,                                              #
#         assets\models\floor.x,                                             #
#         assets\models\wall.x,                                              #
#         assets\models\cement_floor.png,                                    #
#         assets\models\steel_floor.png,                                     #
#         assets\models\Tiny_Skin.bmp                                        #                                                               #
#                                                                            #
# Floor/wall artwork most portions of code by David Lettier.                 #
#                                                                            #
# You may use the following code and floor/wall artwork for whatever purpose #
# you need.                                                                  #
#                                                                            #
# 'tiny.x' and 'Tiny_Skin.bmp' taken from the Microsoft DirectX SDK.         #
#                                                                            #
# Special thanks to the writers of the BVW tutorial and the following        #
# community members: 'russ' and 'yellow'.                                    #
#                                                                            #
#                                                                            #
# All files provided "as is" without warranties expressed or implied.        #
#                                                                            #
# (C) 2006 David Lettier.                                                    #
#                                                                            #
#----------------------------------------------------------------------------#
#
try:
    import sys, os, math, random
    from pandac.PandaModules                 import AmbientLight, DirectionalLight, WindowProperties
    from pandac.PandaModules                 import LightAttrib
    from pandac.PandaModules                 import Vec3, Vec4
    from pandac.PandaModules                 import VBase4
    from pandac.PandaModules                 import AudioManager
    from direct.showbase                                import Audio3DManager
    from direct.actor.Actor                 import Actor
    from direct.gui.OnscreenText             import OnscreenText
    from direct.showbase.ShowBase                 import ShowBase
    from direct.interval.MetaInterval                 import Sequence, Parallel
    from direct.interval.FunctionInterval             import Wait, Func
    from direct.gui.DirectButton             import DirectButton
    from direct.task                                    import Task
    from direct.gui.OnscreenText                        import OnscreenText
    from direct.gui.DirectGui                           import *
    from pandac.PandaModules                            import *
    import direct.directbase.DirectStart
    # end try
except ImportError, err:
    # we have an import error
    print "ImportError: %s." % ( err ) # print the error
    sys.exit( 1 ) # exit the program
    # end except
#
class application( ShowBase ):
    # begin of '__init__' member function
    # this sets it all up for the scene
    def __init__( self ):
        # fog and background colors
        self.mRed = 0.2
        self.mGreen = 0.2
        self.mBlue = 0.2
        # the fog density 0 = none & 1 = full
        self.mDen = .01
        # setup the fog for the scene
        self.fogSetup( )
        # setup the background color for the scene
        self.backgroundSetup( )
        # setup the camera for the scene
        self.cameraSetup( )
        # setup the needed models for the scene
        self.loadModels( )
        # setup the needed light for the scene
        self.setupLights( )
        # setup the needed intervals for the scene
        self.setupIntervals( )
        # setup the needed states
        self.setupStates( )
        # setup the key events needed for the scene
        self.keyBoardSetup( )
        # begin collision code
        # here we create the collision traverser
        base.cTrav = CollisionTraverser()
        # here we create the event collision handler
        self.collHandEvent = CollisionHandlerEvent()
        # now we add an 'in' pattern
        # this consists of a string of an 'into' object
        self.collHandEvent.addInPattern('into-%in')
        # now we add an 'in' again pattern
        self.collHandEvent.addAgainPattern('again-%in')
        # now we add an 'out' pattern
        # this consists of a string of an outof with an into object
        self.collHandEvent.addOutPattern('outof-%in')
        # set this variable to zero for start
        # this aids in naming are collision nodes
        self.collCount = 0
        # add a collision sphere around tiny
        # tiny is a 'from' object
        self.tinyColl = self.initCollisionSphere( self.tiny )
        # add this collision sphere to the colllision traverser
        base.cTrav.addCollider( self.tinyColl[0], self.collHandEvent )
        # create 4 planes used for collision solids
        # each point in the z up position from their respective local
        # space not the world space
        self.planes = [
                    Plane( Vec3(  0, 0, 1 ),  Point3( 0, 0, 0 ) ),
                    Plane( Vec3(  0, 0, 1 ),  Point3( 0, 0, 0 ) ),
                    Plane( Vec3(  0, 0, 1 ),  Point3( 0, 0, 0 ) ),
                    Plane( Vec3(  0, 0, 1 ),  Point3( 0, 0, 0 ) )
        ]
        # create four infinite collision planes in front of the wall models
        # each uses the corresponding planes up above
        self.wallColl = [
                    self.initCollisionPlane( self.walls[0], self.planes[0] ),
                    self.initCollisionPlane( self.walls[1], self.planes[1] ),
                    self.initCollisionPlane( self.walls[2], self.planes[2] ),
                    self.initCollisionPlane( self.walls[3], self.planes[3] )
        ]
        # set up the events needed for the messenger
        # each passes the second element in the tuple in the list
        # also passes the needed functions for each into, again, and outof event
        self.accept( 'into-'  + self.wallColl[0][2], self.colliding)
        self.accept( 'again-' + self.wallColl[0][2], self.colliding)
        self.accept( 'outof-' + self.wallColl[0][2], self.notColliding)
        #
        self.accept( 'into-'  + self.wallColl[1][2], self.colliding)
        self.accept( 'again-' + self.wallColl[1][2], self.colliding)
        self.accept( 'outof-' + self.wallColl[1][2], self.notColliding)
        #
        self.accept( 'into-'  + self.wallColl[2][2], self.colliding)
        self.accept( 'again-' + self.wallColl[2][2], self.colliding)
        self.accept( 'outof-' + self.wallColl[2][2], self.notColliding)
        #
        self.accept( 'into-'  + self.wallColl[3][2], self.colliding)
        self.accept( 'again-' + self.wallColl[3][2], self.colliding)
        self.accept( 'outof-' + self.wallColl[3][2], self.notColliding)
        ShowBase.__init__(self)
        #self.props = WindowProperties()
        #self.props.setSize(1024,768)
        # end __init__
    # begin the colliding member function
    # this function is called when a 'from' object collides with an 'into' object
    def colliding( self, collEntry ): # accept a collision entry argument
        self.isColliding = 1 # we are colliding
        self.pauseWalk( ) # pause all walking animation and movement
        # here we calculate the displacement of how far the collision entry is in
        # in other words we are finding out how far the tiny collision sphere
        # is into the wall collision plane
        disp = ( collEntry.getSurfacePoint( render ) - collEntry.getInteriorPoint( render ) )
        # ok we now know how much tiny is into the wall
        # so we add this number to tiny's current position
        # making tiny sit right in front of the wall and not into it
        newPos = self.tiny.getPos( ) + disp # get new position
        self.tiny.setPos( newPos ) # and set it to tiny's position
        # end colliding
    # begin the notColliding member function
    # this function is called when tiny is no longer colliding with the wall
    def notColliding( self, collEntry ): # accept a collision entry argument
        self.isColliding = 0 # not colliding any more
        # end notColliding
    # begin the initCollisionSphere member function
    # this function creates a sphere used for collision
    # around the object passed to it as a argument
    def initCollisionSphere( self, obj, show = False ): # accept an object and  a defaulted to false
                                                        # show variable as an argument
        bounds = obj.getChild( 0 ).getBounds( ) # get the boundries of the passed object
        center = bounds.getCenter( ) # get the center of these boundries
        radius = bounds.getRadius( ) # get the radius of these boundries
        # here we construct a string based on the current collision count and the object name
        collSphereStr = 'CollisionHull' + str( self.collCount ) + "_" + obj.getName( )
        # increase the collision count to one more for the next call of this function
        self.collCount += 1
        # create a collision node with a the name or string created above
        cNode=CollisionNode( collSphereStr )
        # add a solid to this newly created node
        # we pass it a collision sphere with the center and radius of the boundries of the passed object
        cNode.addSolid( CollisionSphere( center, radius ) )
        # now we attach this collision node to the object node we were passed
        cNodepath = obj.attachNewNode(cNode) # here we save the collision node path for easy reference
        if show: # if show is true
            cNodepath.show() # render or show the collision node
        # now we return a tuple that contains the collision node and it's label
        return ( cNodepath, cNode, collSphereStr )
        # end initCollisionSphere
    # begin the initCollisionPlane member function
    # this code creates a collision plane in front of the object passed to it
    def initCollisionPlane( self, obj, plane, show=False ): # accept an object, plane, and a defaulted
                                                            # to false show variable as an argument
        # here we construct a string based on the current collision count and the object name
        collPlaneStr = 'CollisionPlane' + str( self.collCount ) + "_" + obj.getName( )
        # increase the collision count for the next call
        self.collCount += 1
        # here we create a collision node and assign the string or name to the node
        cNode = CollisionNode( collPlaneStr )
        # here we a add a solid or geometry to the node
        # we pass the collision plane function the plane we were passed
        cNode.addSolid( CollisionPlane( plane ) )
        # now we attach the newly created collision node the the object node we were passed
        cNodepath = obj.attachNewNode( cNode ) # here we save the collison node path for easy reference
        if show: # if show equals true
            cNodepath.show( ) # show the collision geometry or render it to screen
        # here we return a tuple which contains the collision node and it's label
        return ( cNodepath, cNode, collPlaneStr )
        # end initCollisionPlane
    # begin the fogSetup member function
    # this function creates the fog, sets its color, density and makes it affect
    # all in the scene
    def fogSetup( self ):
        self.mFog = Fog( "fog" ) # create
        self.mFog.setColor( self.mRed, self.mGreen, self.mBlue ) # set color
        self.mFog.setExpDensity( self.mDen )  #set density
        render.setFog( self.mFog ) # set to affect all in scene graph
        # end fogSetup
    # begin backgroundSetup member function
    # this sets the color to match that of the fog
    def backgroundSetup( self ):
        base.setBackgroundColor( self.mRed, self.mGreen, self.mBlue ) # set the color
        # end backgroundSetup
    # begin the cameraSetup member function
    def cameraSetup( self ):
        base.disableMouse( ) # disable the default camera controls that are created for us
        # set the position (x, y, and z), heading (cardinal direction), pitch (tilt foward backward), roll (rotation left or right)
        # here we set it a hundred units back from center on the y axis and 30 units up the z axis
        # then we pitch (tilt) the camera foward 15 units in degree
        camera.setPosHpr( Vec3( 0, -100, 30 ), Vec3( 0, -15, 0 ) )
        # ok now tell the task manager to add our camera following task
        taskMgr.add( self.cameraFollowTask, 'cameraFollowTask', sort=30 )
        # end cameraSetup
    # begin the loadModels member function
    # here we load all the models needed for our scene
    def loadModels( self ):
        # load the tiny actor
        # we use actor instead of model because we need to use animations
        self.tiny = Actor( "models/tiny", { "walk" : "models/tiny" } ) # dictionary that defines the walk animation
        self.tiny.reparentTo( render ) # parent 'tiny' to the renderer
        self.tiny.setH( -180 ) # here we change it's heading to face away from the camera
                               # a hundred and eighty degrees
                               # remember this later
        # now we scale tiny down a lot for it is a big mesh
        self.tiny.setScale( .1 ) # number achieved through trial and error
        # now we load the floor for tiny to walk on
        self.floor = loader.loadModel( "models/floor" ) # load static model (no animations)
        self.floor.reparentTo( render ) # parent to renderer
        self.floor.setScale( 5 ) # scale it up to match with tiny
        self.floor.setPos( 0, 0, -26 ) # set it's position down 26 units on the z axis
        # now we create the foor walls we need for tiny to walk into
        # this is a list similiar to an array in other languages
        self.walls = [
                      loader.loadModel( "models/wall" ),
                      loader.loadModel( "models/wall" ),
                      loader.loadModel( "models/wall" ),
                      loader.loadModel( "models/wall" )
        ]
        # ok now we parent to renderer, scale, and position
        self.walls[0].reparentTo( render ) # parent to renderer
        self.walls[0].setScale( 9 ) # scale up to match with others
        self.walls[0].setPos( 0, 900, 64 ) # 90 units y axis (into scene)
        self.walls[0].setP( 90 ) # pitch it up 90 degrees otherwise it would be laying down
        #
        self.walls[1].reparentTo( render ) # same
        self.walls[1].setScale( 9 ) # same
        self.walls[1].setPos( 900, 0, 64 ) # now we position 90 units along the positive x axis
                                          # and 64 units up the positive z axis
        self.walls[1].setH( -90 ) # then we turn it to face us from the left
        self.walls[1].setP( 90 ) # same
        #
        self.walls[2].reparentTo( render ) # same
        self.walls[2].setScale( 9 ) # same
        self.walls[2].setPos( 0, -900, 64 ) # the same but put it in the back of us down the
                                           # the negative y axis
        self.walls[2].setH( 0 ) # turn it around to face the back of us
        self.walls[2].setP( -90 ) # same
        #
        self.walls[3].reparentTo( render ) # same
        self.walls[3].setScale( 9 ) # same
        self.walls[3].setPos( -900, 0, 64 ) # down neg x axis 90 units same for z axis
        self.walls[3].setH( 90 ) # make it face us from the right
        self.walls[3].setP( 90 ) # same
        # ok four walls are up lets move on
        #end loadModels
    # begin the setupLights member function
    # this function creates a signle point light for our scene
    def setupLights( self ):
        # create a point light
        plight = PointLight('plight')
        # set its color
        plight.setColor(VBase4( 0.2, 0.2, 0.2, 1 ) )
        # attach it to the render as a new node
        # 'upcast' to a node otherwise Panda will crash
        # heard this will change in version 1.1.?
        plnp = render.attachNewNode( plight )
        # set the position of the node
        plnp.setPos( 0, 0, 0 )
        # set the light or 'turn' it on
        render.setLight( plnp )
        # the following code makes the 'shadows' less black or dark
        # same as above but we create a ambient light that affects all faces
        alight = AmbientLight( 'alight' ) # light
        alight.setColor( VBase4( 0.2, 0.2, 0.2, 1 ) ) # color
        alnp = render.attachNewNode( alight ) # attach
        render.setLight( alnp ) # turn on
        # end setupLights
    # begin the setupIntervals member function
    # this function setups up the needed intervals for the scene
    def setupIntervals( self ):
        # create a actor interval that calls the member function walk
        # to handle the grunt work
        self.tinyWalk = self.tiny.actorInterval( "walk" )
        # loop then pause to create a more fluid animation start and stop
        # later on (thanks russ)
        self.tinyWalk.loop( )
        self.tinyWalk.pause( )
        # end setupIntervals
    #begin the setupStates member function
    # this creates and sets the states for the scene
    def setupStates( self ):
        self.tinyWalking = 0 # is tiny walking, no
        self.turning = 0 # is tiny turning, no
        self.isColliding = 0 # is tiny colliding, no
        # end setupStates
    # begin the walk member function
    # this function is called in an actor interval each frame
    def walk( self ):
        if self.tinyWalking == 0: # if tiny is not walking
            taskMgr.add( self.walkTask,'walkTask' ) # add the walk task look below
            if self.turning == 0: # if tiny is not turning
                self.tinyWalk.resume( ) # pick up where we last left off in
                                        # in the walk animation
            self.tinyWalking = 1 # flag that tiny is walking now
    # begin the walkTask member function
    # this function is called each frame by the task manager
    def walkTask( self, task ): # accept a task as an argument
        # ok now for some math particulary trigonometry
        dist = 1.0 # the hypotenuse defined by r = sqrt( a^2 + b^2 )
        # here we get the current heading of tiny and convert that degree measurement
        # to radians because the math.sin/cos function needs it to be radians
        angle = self.tiny.getH( ) * math.pi / 180.0 # convert degrees to radians
        correction = math.pi / 2 # ninety degrees in radians
                                 # this is needed for the cofunction formulas
        # in trigonometry x is defined as x = r * cos( angle )
        #                 y is defined as y = r * sin( angle )
        # remember that tiny was turned 180 degrees? And would now be facing
        # 270 degrees (3pi/2 for radians) on the unit circle
        # so we need to use the cofuntion formulas defined as:
        # sin(pi/2 - angle) = cos(angle)
        # cos(pi/2 - angle) = sin(angle)
        # now knowing these we substitute
        # x = r * sin( angle )
        # y = r * cos( angle)
        # however I left it un-substituted for clearity
        dx = dist * math.cos( correction - angle )
        # one more thing, because we want tiny to walk into the scene we
        # make it negative to walk into the scene
        # remove the negative and she walks backwards
        # remember this if you want to make your avatar walk backwards
        dy = dist * -math.sin( correction - angle )
        # now that we know x and y we just add it to the current values since last frame
        self.tiny.setPos( Vec3( self.tiny.getX( ) + dx, self.tiny.getY( ) + dy, 0 ) )
        # on a side note, if you had trouble with the math I recommend
        # "Trigonometry the Easy Way" third edition by Douglas Downing
        # easy read and you should be up and running with trig in no time
        # and we continue on to the next frame
        return Task.cont
        # end walkTask
    # begin the pauseWalk member function
    # this function stops tiny from walking any further
    def pauseWalk( self ):
        if self.tinyWalking == 1: # if tiny is walking
            taskMgr.remove( 'walkTask' ) # remove the walk task now tiny stops moving
            if self.turning == 0: # if tiny is not turning
                self.tinyWalk.pause( ) # now walking animation stops
            self.tinyWalking = 0 # set flag to not walking
            # accept only once to listen for the up arrow pressed
            # if it is call the walk member function
            self.acceptOnce( "arrow_up", self.walk )
        # end pauseWalk
    # begin the turn member function
    # this function sets up the turn task and walk animation
    def turn( self, dir ): # accept a direction as an argument
        if self.turning == 0: # if tiny is not turning
            # add the turn task and pass the direction to the
            # turnTask member function
            taskMgr.add( self.turnTask, 'turnTask', extraArgs = [ dir ] )
            # tiny is now turning
            self.turning = 1
            if self.tinyWalking == 0: # if tiny is not walking
                                      # we check this because we
                                      # don't want to loop it because
                                      # it's already looping by the walk function
                self.tinyWalk.resume( )  # pick up where we left off in the animation
            self.ignore( "arrow_left" )  # ignore the left arrow being pressed
            self.ignore( "arrow_right" ) # ignore the right arrow being pressed
        # end turn
    # begin the turnTask member function
    # this function turns makes tiny walk in a circle if tiny isn't
    # already walking or colliding in a wall
    def turnTask( self, dir ): # accept direction (+/-) as an argument
        speed = 50.0 # degrees/s
        # here we get the time since the beginning of the application
        # not sure about this however
        dt = globalClock.getDt( )
        # here we create the angle of rotation based on the direction,
        # speed or rate, and time
        angle = dir * speed * dt
        # now we subtract this angle from tiny's current heading or angle
        self.tiny.setH( self.tiny.getH( ) - angle )
        if self.tinyWalking == 0: # if tiny is not already walking
                                  # below allows us to make tiny walk
                                  # in a circle instead of turning
                                  # in place
                                  # however we don't want to do this if
                                  # tiny is colliding with a wall
                                  # because then tiny could penetrate the
                                  # wall which we don't want
                                  # and we don't want to do this if tiny's
                                  # position is already being updated by
                                  # walkTask
            if self.isColliding == 0: # if tiny is not colliding
                # the following is the same math as before
                # please see 'walkTask' for details
                dist = .0
                angle = self.tiny.getH( ) * math.pi / 180.0
                correction = math.pi / 2
                dx = dist * math.cos( correction - angle )
                dy = dist * -math.sin( correction - angle )
                self.tiny.setPos( Vec3( self.tiny.getX( ) + dx, self.tiny.getY( ) + dy, 0 ) )
        # continue on to next frame
        return Task.cont
        # end turnTask
    # begin the turnPause member function
    # this function stops tiny from turning in place or in a circle
    def turnPause( self ):
        if self.turning == 1: # if tiny is turning
            taskMgr.remove( 'turnTask' ) # remove task
            self.turning = 0 # set flag, not turning
            if self.tinyWalking == 0: # if tiny is not already walking
                self.tinyWalk.pause( ) # pause the walk animation
            # accept only once the left and right arrow buttons corresponding
            # to each direction respecitively
            self.acceptOnce(  "arrow_left", self.turn, [ -1 ] )
            self.acceptOnce( "arrow_right", self.turn, [ 1 ] )
    # begin the cameraFollowTask member function
    # this function creates a third person view of the avatar at all times
    def cameraFollowTask( self, task ):
        print self.getSize()
        print self.winList
        #if base.mouseWatcherNode.hasMouse() and self.props.hasSize():
        #    x=(base.mouseWatcherNode.getMouseX() - (self.props.getXSize()/2)) * 0.05
        #    y=(base.mouseWatcherNode.getMouseY() - (self.props.getYSize()/2)) * 0.05
#        cx = getpointerx - halfwindowsize * 0.05
#        cy = getpointery - halfwindowsize * 0.05
        #    camera.setHpr(x, y, 0)
#        window.movepointer(0,0)
        return Task.cont
        speed = 100.0 # the speed at which the camera reaches its
                     # desired position
        offset = Vec3( 0, 0, 40 ) # the offset between the camera and tiny
        dt = globalClock.getDt( ) # time since beginning of application
        currPos = camera.getPos( ) # current position of camera
        # this calculates the desired position that camera should be at
        # there we get the current position of tiny and add that to the
        # x axis Quaternion rotation passing the desired offset
        # thus if tiny is able to face the camera, the camera will rotate to the
        # back of tiny
        # Quat is short for "Quaternion." This is a mathematical concept that
        # allows rotations on an arbitrary axis avoiding what is called "gimbal
        # lock."
        desiredPos = self.tiny.getPos( ) + self.tiny.getQuat( ).xform( offset )
        # now that we have the desired position vector we create a new direction vector
        # by subtracting the current position from the desired position
        # for example say our desired position is Vec3( 0, -100, 0) and we are at
        # Vec3(0, -20, 0) so we need to move in a foward direction down the
        # negative y axis eighty units
        direction = Vec3( desiredPos - currPos )
        if ( direction.length( ) > speed * dt ): # if the direction's length
                                                 # is greater than the speed
                                                 # times the time
            direction.normalize( ) # here we normalize the vector
                                   # which means we get a unit vector (magnitude of 1)
                                   # in the same direction as before normalization
            # here we update the camera's position (getting ever closer to the desired position)
            # by getting the current pos + the normlized (magnitude or length of 1 in the same direction)
            # * the speed or rate at which the camera catches up * the time
            camera.setPos( camera.getPos( ) + direction * speed * dt )
        else: # the directions length is less than speed * the time
              # we do this because the length is so close to the desired position
              # that if we just updated the camera's position like in the conditional
              # statement above then we would over shoot the desired position
              # come next frame of rendering which we do not want
            camera.setPos( desiredPos ) # set to desired position because we are so close to it
        camera.setHpr( 90., 0., 0. ) # always be 'looking' at the model tiny
        # continue this task on to next frame
        return Task.cont
        # end cameraFollowTask
    # begin the keyBoardSetup member function
    # this function sets up the keys we need to control tiny
    # and application it self
    def keyBoardSetup( self ):
        # set escape key to exit the application
        self.accept( "escape", sys.exit )
        # set the up arrow key to call the walk member function
        self.acceptOnce(    "arrow_up", self.walk )
        # set the left arrow key to call the turn member function with a left direction
        self.acceptOnce(  "arrow_left", self.turn, [ -1 ] )
        # set the right arrow key to call the turn member function with a right direction
        self.acceptOnce( "arrow_right", self.turn, [ 1 ] )
        # when the player lets up on the arrow keys call their respective pause functions
        self.accept(    "arrow_up-up", self.pauseWalk )
        self.accept(  "arrow_left-up", self.turnPause )
        self.accept( "arrow_right-up", self.turnPause )
        # I believe the 'acceptOnce' call is needed because we are dealing with
        # un-buffered input
        # end keyBoardSetup
    #end application
app = application( ) # create an instance of our application class
#run the simulation
if __name__ == '__main__':
    run( ) # if this module is not being imported run the game
