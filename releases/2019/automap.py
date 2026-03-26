# Verified under Python 3.7.3 IDLE

# Encounter Map
# For the English Fate versionIndex 1.6 running under FS-UAE.exe.
# This is not appropriate to Fate memory maps across
# other emulators with differing memory configurations.


import os
import re
import sys
import pygame
from pygame import *
from pygame.locals import *
from subprocess import Popen, PIPE, check_output
from ctypes import *
from ctypes.wintypes import *

# Declare Color Variables

BLACK    = (   0,   0,   0)
RED      = ( 255,   0,   0)
ORANGE   = ( 255, 165,   0)
YELLOW   = ( 200, 185,   0)
GREEN    = (   0, 100,   0)
LTBLUE   = (   0, 255, 255)
BLUE     = (   0,   0, 255)
DKBLUE   = (   0,   0, 127)
INDIGO   = (  75,   0, 130)
VIOLET   = ( 148,   0, 211)
WHITE    = ( 255, 255, 255)

LEFT = 1

# location of "Winwood" varies by version
memPartyLoc=(int(0x80050E74),int(0x80050FFE))

# two byte big-endian hunger
memWinwoodHunger=(int(0x80050E92),int(0x8005101E))

# two byte big-endian thirst
memWinwoodThirst=(int(0x80050E94),int(0x80051020))

# four byte big-endian cash
memWinwoodCash=(int(0x80050EA0),int(0x8005102A))

# two-byte current health followed by two-byte maximum health
memWinwoodHealth=(int(0x80050EC0),int(0x8005104A))
                                        
# two-byte current mana followed by two-byte maximum mana
memWinwoodMana=(int(0x80050EC4),int(0x8005104E))

# x3 x2 x1 x0 y3 y2 y1 y0 h3 h2 h1 h0
memPartyFateCoordinates=(int(0x800545D0),int(0x8005475A))

# 99 Encounters of 24 bytes each
# 00 byte = x position
# 01 byte = y position
# 02 byte = # of groups (up to 5)
# 03 byte = class of group 1
# 04 byte = class of group 2
# 05 byte = class of group 3
# 06 byte = class of group 4
# 07 byte = class of group 5
# 08 byte = how many in group 1
# 09 byte = how many in group 2
# 10 byte = how many in group 3
# 11 byte = how many in group 4
# 12 byte = how many in group 5
# 13 byte = attitude:
#       bit 1 = hostile
#       bit 2 = friendly
#       bit 4 = willing to join party
memEncounters=(int(0x8005BED8),int(0x8005C062))

# 00-14 byte = class names in the area random encounter table
memEncounterTypes=(int(0x80002EFA),int(0x80002efa))

# three bytes = two characters plus null define map in use
memFateMapImageFilename=(int(0x8000B9ED),int(0x8000BA59))

# Windows flag to read another processes
PROCESS_ALL_ACCESS = 0x1F0FFF


# ----------- get the numerical process ID of imageName ---------------

def getProcessID(imageName):

    thePID = 0
    tasks = check_output(['tasklist']).decode('cp866', 'ignore').split("\r\n")
    for task in tasks:
        m = re.match(b'(.*?)\\s+(\\d+)\\s+(\\w+)\\s+(\\w+)\\s+(.*?)\\s.*', task.encode())
        if m is not None:
            if m.group(1).decode() == imageName:
                thePID=int(m.group(2).decode())
                break
            
    if(thePID==0):
        print()
        print()
        print("Python could not find a process named ", imageName)
        print("Please ensure that ", imageName, " is running.")
        print("Under windows, task manager shows running processes.")
        print("This program quits when ", imageName, " is not in that process list.") 
        sys.exit()

    return thePID

    
# ----------- read memory of process named fs-uae.exe ---------------

def getMemoryChunk(thePID, theMemoryAddress, theVariablePtr, theVariableSize):
    
    OpenProcess = windll.kernel32.OpenProcess
    ReadProcessMemory = windll.kernel32.ReadProcessMemory
    CloseHandle = windll.kernel32.CloseHandle

    bytesRead = c_ulong(0)
    
    processHandle = OpenProcess(PROCESS_ALL_ACCESS, False, thePID)
    if not ReadProcessMemory(processHandle, theMemoryAddress, theVariablePtr, theVariableSize, byref(bytesRead)):
        print("This attempt to read fs-uae memory failed. *shrug* I don't know why we're broke.")
        print(windll.kernel32.GetLastError())
        sys.exit()
    CloseHandle(processHandle)   

    return

# ----------- write memory of process named fs-uae.exe ---------------

def putMemoryChunk(thePID, theMemoryAddress, theVariablePtr, theVariableSize):

    OpenProcess = windll.kernel32.OpenProcess
    WriteProcessMemory = windll.kernel32.WriteProcessMemory
    CloseHandle = windll.kernel32.CloseHandle

    bytesWritten = c_ulong(0)
    
    processHandle = OpenProcess(PROCESS_ALL_ACCESS, False, thePID)
    if not WriteProcessMemory(processHandle, theMemoryAddress, theVariablePtr, theVariableSize, byref(bytesWritten)):
        print("This attempt to write memory returned a zero-length buffer. *shrug* I don't know why we're broke.")
        sys.exit()
    CloseHandle(processHandle)   

    return


# ------- convert Fate (x,y) coordinates -------
# ----- to automap window (x,y) coordinates ----

def fate2win(fateXY,blitXY):

    global windowScale
    global userZoom
    global xyOffset

    winXY =[0,0]

    # Must invert the y variable, because
    # in Fate,   (x,y)=(0,0) is in the lower left-hand corner of the map, but
    # on the PC, (x,y)=(0,0) is in the upper left-hand corner of the window.
    invertedFateXY = [fateXY[0],worldSize[1]-fateXY[1]-1]
    # (to explain the -1) worldSize is 640x400 or 56x56, but world indicees are (0-639)x(0-399) or (0-55)x(0-55).
    

    for xy in range(0,2,1):

        # Y-inverted-Fate-XY coordinates are scaled from Fate's world size to automap's window size: windowScale[xy]*invertedFateXY[xy]
        # The result is shifted from being at the edge of the tile, to the middle of the tile: +windowScale[xy]/2
        # That result is subjected to any user-defined zoom and user-defined x-y-offset: *userZoom[xy]+xyOffset[xy]
        # Finally, the symbol to be plotted is adjusted so that it's center, not it's left edge, is at the desired plot point: +blitXY[xy]/2

        winXY[xy]=int((windowScale[xy]*invertedFateXY[xy]+windowScale[xy]/2)*userZoom[xy]+xyOffset[xy]-blitXY[xy]/2)

        
    #print(int((windowScale[0]*(partyX)+windowScale[0]/2)*userZoom[0]+xyOffset[0]+partyBlitX/2),
    #    int((windowScale[1]*(worldSize[1]-partyY)+windowScale[1]/2)*userZoom[1]+xyOffset[1]+partyBlitY/2),
    #    "out",winXY,"in",fateXY,"inverted",invertedFateXY,"winscale/zoomscale/offset/blit",windowScale,userZoom,xyOffset,blitXY)

    return (winXY[0],winXY[1])


# --- convert automap window (x,y) coordinates ---
# ----------- to Fate (x,y) coordinates ----------
# ------ this is used to teleport the party ------
# ---- to mouse pointer in window coordinates ----

def win2fate(winXY):

    global windowScale
    global xyOffset
    global userZoom

    fateXY =[0,0]

    for xy in range(0,2,1):
        
        fateXY[xy]=int(((winXY[xy]-xyOffset[xy])/userZoom[xy])/windowScale[xy])


    # Must invert the y variable, because
    # on the PC, (x,y)=(0,0) is in the upper left-hand corner of the window, but
    # in Fate,   (x,y)=(0,0) is in the lower left-hand corner of the map.
    fateXY[1] = worldSize[1]-fateXY[1]-1
    # (to explain the -1) worldSize is 640x400 or 56x56, but world indicees are (0-639)x(0-399) or (0-55)x(0-55).

    return (fateXY[0],fateXY[1])



# ----------- begin program ---------------

if __name__ == '__main__':


    # ----------- given the name of the process, get the Windows process ID ---------------

    myPID=getProcessID("fs-uae.exe")

    '''
    Now that we have the PID for FS-UAE.EXE,
    which version of "Fate Gates of Dawn" is this one?
    '''
    # versionIndex, English V1.6=0, Deutsche V1.7=1
    versionIndex=0          # test for English V1.6
    
    partyLoc = bytearray('Winwood'.encode('ascii'))
    partyLocPtr = ctypes.c_char * len(partyLoc)
    partyLocPtr = partyLocPtr.from_buffer(partyLoc)
    partyLocSize = len(partyLoc)
    partyLocAddress = memPartyLoc[versionIndex]

    getMemoryChunk(myPID, partyLocAddress, partyLocPtr, partyLocSize)

    if (partyLoc == bytearray("Winwood",'ascii')):
        versionIndex=0          # found English V1.6    
    else:

        versionIndex=1          # test for German V1.7
        partyLocAddress = memPartyLoc[versionIndex]
        
        getMemoryChunk(myPID, partyLocAddress, partyLocPtr, partyLocSize)        

        if (partyLoc != bytearray('Winwood'.encode('ascii'))):
            print("Could not find either version 1.6 or version 1.7 in FS-UAE memory")
            sys.exit()          # both tests failed            
    
    

    '''
    (there follows some whining about my historical learning process)

    I found it challenging to understand how to attain my objectives in Python.
    The Windows function ReadProcessMemory wants a variable passed by reference.
    I used python bytearray type because it is mutable
    (i.e. its data can [and will] be changed by the function call).
    Ultimately the pointer (e.g. to pass by reference) was a ctypes pointer to a char type.
    The pointer was then set to the location of the bytearray.

    I couldn't use a character array with c_type_p,
    because even though the function read the entire memory,
    any subscript that was after the first null (0x00) in
    the data returned a subscript out of bounds error.

    Eventually I settled on the present approach, which aliases the reference.
    '''

    # set up variables for party coordinates

    partyFateCoordinates = bytearray('0123456789AB'.encode('ascii'))
    partyFateCoordinatesPtr = ctypes.c_char * len(partyFateCoordinates)
    partyFateCoordinatesPtr = partyFateCoordinatesPtr.from_buffer(partyFateCoordinates)
    partyFateCoordinatesSize = len(partyFateCoordinates)
    partyFateCoordinatesAddress = memPartyFateCoordinates[versionIndex]
       
    # set up variables for encounter coordinates

    Encounters = bytearray(24*100)
    EncountersPtr = ctypes.c_char * len(Encounters)
    EncountersPtr = EncountersPtr.from_buffer(Encounters)
    EncountersSize = len(Encounters)
    EncountersAddress = memEncounters[versionIndex]
    
    # get encounter table for the current map

    EncounterTypes = bytearray(64*100)
    EncounterTypesPtr = ctypes.c_char * len(EncounterTypes)
    EncounterTypesPtr = EncounterTypesPtr.from_buffer(EncounterTypes)
    EncounterTypesSize = len(EncounterTypes)
    EncounterTypesAddress = memEncounterTypes[versionIndex]

    # ----------- initialize a map window ---------------

    pygame.init()
    pygame.font.init()    

    # used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # default: do not print encounter information until user commands it
    printEncounter=False
    
    # set up a few variables that support background map determination
    FateMapImageFilename = bytearray(b'90\x00')         # default wilderness map = '90'
    FateMapPrevImageFilename = bytearray(b'99\x00')     # this is deliberately set to an
                                                        # invalid map string, to force the
                                                        # background map to initialize on
                                                        # the first pass through the loop.

    FateMapPrevImageFilenamePtr = ctypes.c_char * len(FateMapPrevImageFilename)
    FateMapPrevImageFilenamePtr = FateMapPrevImageFilenamePtr.from_buffer(FateMapPrevImageFilename)

    FateMapImageFilenamePtr = ctypes.c_char * len(FateMapImageFilename)
    FateMapImageFilenamePtr = FateMapImageFilenamePtr.from_buffer(FateMapImageFilename)
    FateMapImageFilenameSize = len(FateMapImageFilename)
    getMemoryChunk(myPID, memFateMapImageFilename[versionIndex], FateMapImageFilenamePtr, FateMapImageFilenameSize)

    
    # for the first time, fetch the image of the current Fate map

    FateMapImageFilenameString = str(FateMapImageFilename[0:2],'ascii')+'.bmp'
    originalFateMapImage = pygame.image.load(FateMapImageFilenameString)
    originalFateMapImageSize = originalFateMapImage.get_size()
    
    # Set up display parameters
    
    # Proportion the display window to the assumed background map size
    if FateMapImageFilename[0] == 57:
        worldSize = (640, 400)      # wilderness map is 640x400 game tiles
        windowPixels = (640, 400)   # make default window size 640x400 pixels
        zoomFont = int(9)           # default font size at the default zoom scale    
    else:
        worldSize = (56, 56)        # town, city, or dungeon map is 56x56 game tiles
        windowPixels = (560, 560)   # make default window size 560x560 pixels
        zoomFont = int(9)           # default font size at the default zoom scale    
    
    xyOffset = (0, 0)               # number of x,y pixels the upper left corner of the map
                                    # image will be offset from the
                                    # upper left corner of the window
    userZoom = (1.0, 1.0)           # user can zoom in or zoom out of map


    # This is the first place where we create the pygame surface (e.g. the automap window).
    # It will always be called "myWindowObject."
    # Each time it's updated, "myWindowObject" will be overwritten with the new surface.
    myWindowObject = pygame.display.set_mode(windowPixels,pygame.RESIZABLE)
    pygame.display.set_caption("(?=menu)(Flashing=Us)(Red=Hostile)(Black=Neutral)(Green=Available)")
    partyColor = LTBLUE
    
            
    # -------- Main Program Loop -----------
    done = False
    while not done:

        #---- Check if the current Fate map is the same map that was used
        #---- on the previous pass through this loop.
        #---- If it has changed, load new background image            
        #---- and calculate new scaling factors.
        getMemoryChunk(myPID, memFateMapImageFilename[versionIndex], FateMapImageFilenamePtr, FateMapImageFilenameSize)
        
        if FateMapPrevImageFilename != FateMapImageFilename:

            FateMapPrevImageFilename[:] = FateMapImageFilename

            '''
            Adding background image originald on memory address 0x8000B9ED
            (i.e. the two-character filename for the current map).
            I am hoping that it is OK to assume background file is in the
            same folder as this python executable.
            Not now, but maybe later, I may try to understand how to use Fate's map formats.
            '''
    
            # fetch the image of the current Fate map

            FateMapImageFilenameString = str(FateMapImageFilename[0:2],'ascii')+'.bmp'
            originalFateMapImage = pygame.image.load(FateMapImageFilenameString)
            originalFateMapImageSize = originalFateMapImage.get_size()
            
           
            '''
            With my limited knowledge of Fate, I'm going to assume that
            town, city, and dungeon spaces are 56x56 tiles, and that
            the wilderness space is 640x400 tiles.
            I will assume that map files have no borders around them.
            If the wilderness map file image size is 640x400 pixels, 
            that will set the scale to 1x, but if the image size is 1280x800 pixels,
            that will set the scale to 2x, etc.
            If a town, city, or dungeon map image size is 56x56 pixels,
            that will set the scale to 1x, but if the image size is 560x560 pixels,
            that will set the scale to 10x, etc.
            '''

            # on current map, decide if the native world size should be (640x400) or (56x56)
            if FateMapImageFilename[0] == 57:
                worldSize = (640, 400)
                zoomFont = int(9)           # default font size at the default zoom scale    
            else:                
                worldSize = (56, 56)
                zoomFont = int(9)           # default font size at the default zoom scale    

            # determine how many pixels per game tile
            windowScale = (windowPixels[0]/worldSize[0],windowPixels[1]/worldSize[1])

            # update encounter table for the current map
            getMemoryChunk(myPID, EncounterTypesAddress, EncounterTypesPtr, EncounterTypesSize)
    
            
        # clear the window
        myWindowObject.fill(BLACK)

        # scale the map to the automap window
        myMapImage = pygame.transform.scale(originalFateMapImage, (int(userZoom[0]*windowPixels[0]),int(userZoom[1]*windowPixels[1])))

        # draw the map within the automap window
        myWindowObject.blit(myMapImage, xyOffset)
 
        


        #--------------------------------------------------------            
        # --- Main event loop
        for event in pygame.event.get(): # User did something

            # check event type

            if event.type == pygame.QUIT: # If user clicked close
                done = True # Flag that we are done so we will exit this loop
                
            elif event.type == pygame.VIDEORESIZE: # the user has resized the window
                oldwindowPixels = windowPixels
                windowPixels = (event.w, event.h)
                windowScale = (windowPixels[0]/worldSize[0],windowPixels[1]/worldSize[1])
                myWindowObject = pygame.display.set_mode(windowPixels, pygame.RESIZABLE)                
                
            elif event.type == pygame.KEYDOWN:

                if event.key == K_PAGEUP or (event.key == K_KP9 and event.key != K_NUMLOCK):             # zoom in
                    if userZoom[0]<8 and userZoom[1]<8:

                        # zoom in
                        userZoom=(userZoom[0]*1.5,userZoom[1]*1.5)                        
                    
                elif event.key == K_PAGEDOWN or (event.key == K_KP3 and event.key != K_NUMLOCK):           # zoom out
                    if userZoom[0]>1/8 and userZoom[1]>1/8:
                        userZoom=(userZoom[0]/1.5, userZoom[1]/1.5)
                                                                    
                elif event.key == K_UP or (event.key == K_KP8 and event.key != K_NUMLOCK):              # move up
                    xyOffset = (xyOffset[0], int(xyOffset[1] + windowPixels[1]/25))
                                            
                elif event.key == K_DOWN or (event.key == K_KP2 and event.key != K_NUMLOCK):            # move down
                    xyOffset = (xyOffset[0], int(xyOffset[1] - windowPixels[1]/25))
                
                elif event.key == K_LEFT or (event.key == K_KP4 and event.key != K_NUMLOCK):            # move left
                    xyOffset = (int(xyOffset[0] + windowPixels[0]/25), xyOffset[1])
                
                elif event.key == K_RIGHT or (event.key == K_KP6 and event.key != K_NUMLOCK):           # move right
                    xyOffset = (int(xyOffset[0] - windowPixels[0]/25), xyOffset[1])
                
                elif event.key == K_RCTRL or event.key == K_LCTRL:                      # circle the party location

                    # draw a big circle around partyPlotXY
                    pygame.draw.circle(myWindowObject, RED, partyPlotXY, int(windowPixels[0]/10), int(windowPixels[0]/50))                    

                elif (event.unicode == 'c' or event.unicode == 'C'):                  # c = center the view on the mouse pointer

                    mouseXY = pygame.mouse.get_pos()
                    fateViewMin=win2fate((0,0))
                    fateViewMax=win2fate(windowPixels)
                    fateViewCenter=(int((fateViewMin[0]+fateViewMax[0])/2),int((fateViewMin[1]+fateViewMax[1])/2))
                    winViewCenter=fate2win(fateViewCenter,(0,0))
                    
                    xyOffset = (xyOffset[0]-(mouseXY[0]-winViewCenter[0]),xyOffset[1]-(mouseXY[1]-winViewCenter[1]))
                    
                elif (event.unicode == 'd' or event.unicode == 'D'):                  # d=drink to quench thirst
                    
                    drink = bytearray(b'\x00\x00')      # \x00 = well hydrated
                    drinkPtr = ctypes.c_char * len(drink)
                    drinkPtr = drinkPtr.from_buffer(drink)
                    drinkSize = len(drink)

                    for thirstMem in range(memWinwoodThirst[versionIndex],memWinwoodThirst[versionIndex]+28*500,500):
                        putMemoryChunk(myPID, thirstMem, drinkPtr, drinkSize)

                elif (event.unicode == 'f' or event.unicode == 'F'):                 # f=food to feed hunger
                    
                    food = bytearray(b'\x00\x00')       # \x00 = well fed
                    foodPtr = ctypes.c_char * len(food)
                    foodPtr = foodPtr.from_buffer(food)
                    foodSize = len(food)

                    for hungerMem in range(memWinwoodHunger[versionIndex],memWinwoodHunger[versionIndex]+28*500,500):
                        putMemoryChunk(myPID, hungerMem, foodPtr, foodSize)

                elif (event.unicode == 'h' or event.unicode == 'H'):                  # h=health/hit points
                    
                    health = bytearray(b'1234')      
                    healthPtr = ctypes.c_char * len(health)
                    healthPtr = healthPtr.from_buffer(health)
                    healthSize = len(health)

                    for healthMem in range(memWinwoodHealth[versionIndex],memWinwoodHealth[versionIndex]+28*500,500):
                        getMemoryChunk(myPID, healthMem, healthPtr, healthSize)
                        health[0]=health[2]             # current health gets replaced with max health
                        health[1]=health[3]
                        putMemoryChunk(myPID, healthMem, healthPtr, healthSize)

                elif (event.unicode == 'm' or event.unicode == 'M'):                  # m=mana/mage points
                    
                    mana = bytearray(b'1234')      
                    manaPtr = ctypes.c_char * len(mana)
                    manaPtr = manaPtr.from_buffer(mana)
                    manaSize = len(mana)

                    for manaMem in range(memWinwoodMana[versionIndex],memWinwoodMana[versionIndex]+28*500,500):
                        getMemoryChunk(myPID, manaMem, manaPtr, manaSize)
                        mana[0]=mana[2]                 # current mana gets replaced with max mana
                        mana[1]=mana[3]
                        putMemoryChunk(myPID, manaMem, manaPtr, manaSize)

                elif event.unicode == 'p' or event.unicode == 'P':  # print coordinates
                    printEncounter=not(printEncounter)


                elif (event.unicode == 't' or event.unicode == 'T'):    #(event.type == MOUSEBUTTONDOWN):    # and event.button == LEFT):

                    mouseXY = pygame.mouse.get_pos()
                    
                    # convert pixel locations into game coordinates

                    teleportXY = win2fate(mouseXY)
                    
                    # convert game coordinates to 4-byte integers
                    partyFateCoordinates[0] = int(teleportXY[0]/(256*256*256)) % 256
                    partyFateCoordinates[1] = int(teleportXY[0]/(256*256)) % 256
                    partyFateCoordinates[2] = int(teleportXY[0]/256) % 256
                    partyFateCoordinates[3] = int(teleportXY[0] % 256)
                    partyFateCoordinates[4] = int(teleportXY[1]/(256*256*256)) % 256
                    partyFateCoordinates[5] = int(teleportXY[1]/(256*256)) % 256
                    partyFateCoordinates[6] = int(teleportXY[1]/256) % 256
                    partyFateCoordinates[7] = int(teleportXY[1] % 256)
                    
                    putMemoryChunk(myPID, memPartyFateCoordinates[versionIndex], partyFateCoordinatesPtr, partyFateCoordinatesSize)       

                elif event.unicode == '$':           # $=Add funds in 1000 piaster increments
                    
                    cash = bytearray(b'1234')               # cash = 4 bytes
                    cashSize = len(cash)
                    cashPtrType = ctypes.c_char * cashSize
                    cashPtr = cashPtrType.from_buffer(cash)

                    cashInt = int()

                    for cashMem in range(memWinwoodCash[versionIndex],memWinwoodCash[versionIndex]+28*500,500):
                        getMemoryChunk(myPID, cashMem, cashPtr, cashSize)
                        cashInt=256*256*256*cash[0]+256*256*cash[1]+256*cash[2]+cash[3]
                        
                        if(cashInt<500000):            
                            cashInt=cashInt+1000                            
                        cash[0]=(cashInt>>24)&255
                        cash[1]=(cashInt>>16)&255
                        cash[2]=(cashInt>>8)&255
                        cash[3]=cashInt&255                        
                                                
                        putMemoryChunk(myPID, cashMem, cashPtr, cashSize)
                        
                elif event.unicode == '?':                          # ?=show menu

                    menuBackground = BLACK
                    myWindowObject.fill(menuBackground)             # clear the window
                    menuBlit = pygame.image.load("menu.bmp")
                    myBlit=pygame.transform.scale(menuBlit,(int(windowPixels[0]*0.8),int(windowPixels[1]*0.8)))
                    myWindowObject.blit(myBlit, (int(windowPixels[0]/10),int(windowPixels[1]/10)))
                                        
                    pygame.display.flip()

                    myWait = 'q'
                    while myWait!=K_SPACE:
                        for event in pygame.event.get():            # User did something

                            if event.type == pygame.QUIT:           # If user clicked close
                                myWait = K_SPACE                    # quit the immediate loop
                                done = True                         # quit the main game loop
                
                            elif event.type == pygame.VIDEORESIZE:  # the user has resized the window
                                oldwindowPixels = windowPixels
                                windowPixels = (event.w, event.h)
                                windowScale = (windowPixels[0]/worldSize[0],windowPixels[1]/worldSize[1])
                                myWindowObject = pygame.display.set_mode(windowPixels, pygame.RESIZABLE)
                            
                            elif event.type == pygame.KEYDOWN:
                                myWait = K_SPACE
                    
                    # clear the window
                    myWindowObject.fill(BLACK)

                    # scale the map to the automap window
                    myMapImage = pygame.transform.scale(originalFateMapImage, (int(userZoom[0]*windowPixels[0]),int(userZoom[1]*windowPixels[1])))

                    # draw the map within the automap window
                    myWindowObject.blit(myMapImage, xyOffset)
 


                elif event.key == K_ESCAPE or event.unicode == 'q' or event.unicode == 'Q':                  # q=quit
                    done = True


        # get party coordinates from within Fate

        getMemoryChunk(myPID, partyFateCoordinatesAddress, partyFateCoordinatesPtr, partyFateCoordinatesSize)
                
        # --- Plot party position
        
        font = pygame.font.SysFont('Courier New', int(1.5*zoomFont), True, False)
        if partyColor == LTBLUE:
            partyColor = BLUE
        elif partyColor == BLUE:
            partyColor = RED
        elif partyColor == RED:
            partyColor = BLACK
        elif partyColor == BLACK:
            partyColor = LTBLUE

        partyText=u'☺'
        if(partyFateCoordinates[11]==1):
            partyText=u'▲'
        elif (partyFateCoordinates[11]==2):
            partyText=u'◄'
        elif (partyFateCoordinates[11]==3):
            partyText=u'▼'
        elif (partyFateCoordinates[11]==4):
            partyText=u'►'

        font = pygame.font.SysFont('Courier New', zoomFont, True, False)

        # must now think about how to scale party coordinates against the scaled map
        partyBlit = font.render(partyText,True,partyColor)
        partyBlitX=partyBlit.get_width()
        partyBlitY=partyBlit.get_height()

        # get X and Y game coordinates:  four bytes each, converted to integers
        partyXhi = int(256*256*256*partyFateCoordinates[0]+256*256*partyFateCoordinates[1]+256*partyFateCoordinates[2])
        partyX128 = 128*int(partyFateCoordinates[3]/128)
        partyX64 = 64*int(partyFateCoordinates[3]/64)
        partyX32 = 32*int(partyFateCoordinates[3]/32)
        partyX = int(partyXhi + partyFateCoordinates[3])
        partyYhi = int(256*256*256*partyFateCoordinates[4]+256*256*partyFateCoordinates[5]+256*partyFateCoordinates[6])
        partyY128 = 128*int(partyFateCoordinates[7]/128)
        partyY64 = 64*int(partyFateCoordinates[7]/64)
        partyY32 = 32*int(partyFateCoordinates[7]/32)
        partyY=int(partyYhi+partyFateCoordinates[7])
        
        # Convert game coordinates into pixel locations.
        # party*windowScale converts from tiles to pixels (windowScale indicates how many pixels are in each tile).
        # In the Y axis, windowPixels[1]-(windowScale[1]*partyY)) inverts the Y axis, because
        # in Fate, lower left = 0,0, but in Pygame, upper left = 0,0.
        # Next, we must factor in any user zoom (when the user zoomed in/out of the map with PgUp/PgDn).  After that, 
        # we subtract partyBlitX/2 and partyBlitY/2 because we want to plot to the CENTER of the party icon,
        # not the top left edge of the party icon.  partyBlitX and partyBlitY are the X and Y width of partyBlit icon,
        # so the center of the icon is found by dividing the width in two.
        # The last step is to factor in any user-defined offset (when the user scrolled around the map with up/down/left/right)
        # by adding xyOffset to the total.
        # After these bits of maths, hopefully the party icon is blitted correctly on the automap window.

        # But no, there's one more thing that I've forgotton:
        # Each tile has a real extent.  If the pixel extent of each tile is greater than 1,
        # then we want to center the icon in the middle of the tile, not at the left edge.
        # So, before userZoom, but after windowScale, we need to make an adjustment equal to 1/2 a tile width, in pixels.
        # windowScale = pixels per tile.  windowScale/2 = 1/2 the width of a tile, in pixels.

        partyPlotXY=fate2win((partyX,partyY),(partyBlitX,partyBlitY))
        
        # blit the party symbol onto the automap window
        myWindowObject.blit(partyBlit,partyPlotXY)

        # print encounter information if appropriate
        if printEncounter == True:
            print("FateP=",partyX, partyY,"Window=",partyPlotXY,windowPixels,"xyOffset=",xyOffset,"userZoom=",userZoom,"windowScale=",windowScale)


        # ---------- Plot the 99 EncounterTypes ------------

        '''
        Each encounter (x,y) coordinate is 8 bits
        and can only enumerate 256 possible locations.
        That works in the towns, none of which are larger than 256x256.
        However, the wilderness (x,y) is (640,400).  
        Neither 8-bit integer can contain all excursions
        across 400 or 640 positions.

        I've tried to imagine, how does Fate store these EncounterTypes?

        Plotting these x,y values, I observe that they do not move as I move,
        so they are stable in relation to the world map.

        So, I hypothesize that Encounters are plotted on a max 256x256 window
        within the world map, and that somewhere are a few bytes that
        encapsulate the x,y address of that 256x256 window's anchor
        within the 640x400 world.

        Unsuccessfully, I spent a great deal of time trying to find such
        a memory address.

        Each entry in the Encounter type lookup table is 64 bytes
        Each entry in the 99 random EncounterTypes is 24 bytes
        Within random encounter entry, [0]=x,[1]=y,[2]=# groups(e.g. 1-5),[3]-[7]=encounter type

        -----------------------------------------------------------------
        After incorporating a teleport feature into the automap,
        I've learned something new that may be useful.
        It doesn't matter where you are on the 640x400 map.
        No matter where on the map your party is,
        the random encounters will be there also.
        This seems to suggest that fate relates the encounter 8 bit x,y values
        to the current position somehow.
        
        Facts behind this supposition:
        There are intervals when a set of random encounters are plotted
        and do not change composition, but do incrementally change position.
        No matter where the party is on the 640x400 wilderness map,
        it meets those random encounters.
        When the party teleports more than 256 tiles away,
        it still meets encounters of the same composition.

        Hypothesis: could the encounters use the higher order bytes of the party's position?
               
        '''

        # get encounters
        
        getMemoryChunk(myPID, EncountersAddress, EncountersPtr, EncountersSize)
                
        # Encounters = bytearray(24*99) = list of specific Encounters in an area
        # EncounterTypes = bytearray(64*99) = types of random Encounters unique to an area
        # thisEncounter steps through each of 99 Encounters (e.g. Encounters 0 to 98, each one using 24 bytes)
        
        minXY=(99999,99999)
        maxXY=(0,0)
        
        for thisEncounter in range(0,24*98,24):     # sequence through each of the 99 specific encounters in an area

            # this variable indicates if the encounter is
            # hostile, non hostile but would never join the party,
            # or can be convinced to join the party
            if Encounters[thisEncounter+13]==0x82:
                encounterColor=GREEN
            elif Encounters[thisEncounter+13]==2:
                encounterColor=BLACK                
            elif Encounters[thisEncounter+13]==1:
                encounterColor=RED
            
            # theseGroups = number of groups in this encounter (between 1 and 5 inclusive)
            theseGroups=int(Encounters[thisEncounter+2])
            encounterText=""

            # step through each group in this particular encounter
            for thisGroup in range(0,theseGroups,1):                

                # encounterIndex points to the group's encounter class, from the Larvin EncounterTypes array
                encounterIndex=int(Encounters[thisEncounter+thisGroup+3])
                
                # TRAP:if index is out of range, it means the game is transitioning between map states.
                # The biggest encounter table I have seen so far has 82 elements.
                # This may need to be updated as more encounter tables are discovered.
                # Alternative coding might be to rewrite the "thisEncounter" loop as a function,
                # so that a "return()" could break all the way back to that loop.
                # This current approach is less efficient, but more convenient (avoiding rewrite).
                if (encounterIndex > 82):
                    break               # breaks out of this group,
                                        # but not out of subsequent encounters,
                                        # so must check again in outer loops
                 
                myEncounterType=64*encounterIndex
                for myEncounterChar in range(myEncounterType,myEncounterType+14,1):
                    if EncounterTypes[myEncounterChar]>127:       
                        break      # non-ascii char flags the end of the string
                    
                # TRAP:break out of the loop if the length of thisGroupText is less than 1
                if (myEncounterChar-1 < myEncounterType):
                    break
                thisGroupText=EncounterTypes[myEncounterType:(myEncounterChar-1)].decode('ascii')
                encounterText=encounterText+thisGroupText
                            
            # TRAP: if index is out of range, it means the game is transitioning between map states.
            # The biggest encounter table I have seen so far has 82 elements.
            # This may need to be updated as more encounter tables are discovered.
            if (encounterIndex > 82) or (myEncounterChar-1 < myEncounterType):
                break               # breaks out of the "for thisEncounter" loop
                                    # which allows the map and the encounter table to be updated
                                    
            encounterBlit = font.render(encounterText,True,encounterColor)
            encounterBlitX = encounterBlit.get_width()
            encounterBlitY = encounterBlit.get_height()

            # get encounter X and Y coordinates from within Fate
            #encounterXY=(Encounters[thisEncounter],Encounters[thisEncounter+1])
            '''
            # Testing hypothesis of party high bytes specify encounter high bytes.
            # Guessing the amount needed to add to the encounter coordinates (x and y)
            # to align it properly with the party coordinates.
            # There is a very rough correlation between correct guesses and
            # party location on the wilderness map, but no reliable ruleset.
            # When the party teleports, but the encounter table does not regenerate,
            # the same encounter (x,y) yield encounters in the new party location.
            # Even when the teleport occurs through changing of party x,y coordinates
            # outside of the game code, the same encounter table yields the same
            # encounters, despite very great party coordinate changes.
            # Hopefully, there is a reliable rule of thumb that will work.

            # a few hypotheses:
            # -what if fate notices teleports and updates some encounter offset memory?
            # -what if fate always chooses encounter offset, each turn, so that (for example)
            #  it is the multiple of 40 that makes the first encounter in the table closest to the party?
            #  Go back and look if first or last encounter is surprisingly close to center of encounters.
            
            '''
            guessX=-40
            guessY=320
            
            encounterXY=(Encounters[thisEncounter],Encounters[thisEncounter+1])

            # wilderness encounters on the 640x400 map are plotted differently
            # than are town city or dungeon encounters on the 56x56 maps
            if FateMapImageFilename[0] == 57:   # wilderness
                encounterXY=(guessX+Encounters[thisEncounter],guessY+Encounters[thisEncounter+1])
            else:
                encounterXY=(Encounters[thisEncounter],Encounters[thisEncounter+1])
                

            # convert game coordinates into pixel locations
            #encounterPlotX=xyOffset[0]+int(userZoom[0]*(windowScale[0]*encounterX+windowScale[0]/2))
            #encounterPlotY=xyOffset[1]+int(userZoom[1]*(windowPixels[1]-(windowScale[1]*encounterY+windowScale[1]/2))-encounterBlitY/2)
            encounterPlotXY = fate2win(encounterXY,(0,encounterBlitY))

            # write the encounter groups on the map
            myWindowObject.blit(encounterBlit,encounterPlotXY)
            

            # print encounter information if appropriate
            if (printEncounter == True):
                print("FateE=",encounterXY,"Window=",encounterPlotXY,windowPixels,"xyOffset=",xyOffset,"userZoom=",userZoom,"windowScale=",windowScale,encounterText,Encounters[thisEncounter+8])
                if encounterXY != (0,0):
                    minXY=(min(encounterXY[0],minXY[0]),min(encounterXY[1],minXY[1]))
                    maxXY=(max(encounterXY[0],maxXY[0]),max(encounterXY[1],maxXY[1]))                

        if (printEncounter == True):
            print(minXY[0],"-",maxXY[0],"[",maxXY[0]-minXY[0],"]",minXY[1],"-",maxXY[1],"[",maxXY[1]-minXY[1],"]")

            # After printing party and encounter coordinates once, stop until next time 'p' key is selected.
            printEncounter = False


        # debugging print
        #print("party",partyX,partyY,"guess",guessX,guessY)
    
        
        # --- Go ahead and update the screen with what we've drawn.
        pygame.display.flip()
 
        # --- Limit to 2 frames per second
        clock.tick(2)
        
    pygame.display.quit()
    pygame.quit()
    sys.exit()
