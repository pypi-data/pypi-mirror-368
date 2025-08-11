from . import gameObjects, pygamePIL, ingameData

import math

SHAPE_BORDER_COLOR = (35,25,35)
BG_CIRCLE_COLOR = (31,41,61,25)
SHADOW_COLOR = (50,50,50,127)
EMPTY_COLOR = (0,0,0,0)
PIN_COLOR = (71,69,75)
COLORBLIND_PATTERN_COLOR = (0,0,0)

# according to 'dnSpy > ShapeMeshGenerator > GenerateShapeMesh()', this value should be 0.85
# according to ingame screenshots, it should be 0.77
# according to me, the closest to ingame is 0.8
# but, to me, the best for this context is 0.75
LAYER_SIZE_REDUCTION = 0.75

# below are sizes in pixels taken from a screenshot of the ingame shape viewer
DEFAULT_IMAGE_SIZE = 602
DEFAULT_BG_CIRCLE_DIAMETER = 520
DEFAULT_SHAPE_DIAMETER = 407
DEFAULT_BORDER_SIZE = 15

FAKE_SURFACE_SIZE = 500
SIZE_CHANGE_RATIO = FAKE_SURFACE_SIZE / DEFAULT_IMAGE_SIZE
SHAPE_SIZE = DEFAULT_SHAPE_DIAMETER * SIZE_CHANGE_RATIO
SHAPE_BORDER_SIZE = round(DEFAULT_BORDER_SIZE*SIZE_CHANGE_RATIO)
BG_CIRCLE_DIAMETER = DEFAULT_BG_CIRCLE_DIAMETER * SIZE_CHANGE_RATIO

COLORBLIND_NUM_PATTERNS = 13
COLORBLIND_PATTERN_SPACING = (FAKE_SURFACE_SIZE) / (COLORBLIND_NUM_PATTERNS-1)
COLORBLIND_PATTERN_WIDTH = COLORBLIND_PATTERN_SPACING * 0.25

SQRT_2 = math.sqrt(2)
SQRT_3 = math.sqrt(3)
SQRT_6 = math.sqrt(6)

def _preRenderColorblindPatterns() -> None:

    global _colorblindPatterns
    surfaceSize = FAKE_SURFACE_SIZE
    redSurface = pygamePIL.Surface((surfaceSize,surfaceSize),pygamePIL.SRCALPHA)
    greenSurface = redSurface.copy()
    blueSurface = redSurface.copy()

    for i in range(COLORBLIND_NUM_PATTERNS):
        pygamePIL.draw.line(
            redSurface,
            COLORBLIND_PATTERN_COLOR,
            (i*COLORBLIND_PATTERN_SPACING,0),
            (i*COLORBLIND_PATTERN_SPACING,surfaceSize),
            round(COLORBLIND_PATTERN_WIDTH)
        )

    for x in range(COLORBLIND_NUM_PATTERNS-1):
        for y in range(COLORBLIND_NUM_PATTERNS):
            pygamePIL.draw.rect(
                greenSurface,
                COLORBLIND_PATTERN_COLOR,
                pygamePIL.Rect(
                    (x*COLORBLIND_PATTERN_SPACING) + (COLORBLIND_PATTERN_SPACING/2) - (COLORBLIND_PATTERN_WIDTH/2),
                    (y*COLORBLIND_PATTERN_SPACING) - (COLORBLIND_PATTERN_WIDTH/2),
                    COLORBLIND_PATTERN_WIDTH,
                    COLORBLIND_PATTERN_WIDTH
                )
            )

    for i in range((COLORBLIND_NUM_PATTERNS*2)-1):
        pygamePIL.draw.line(
            blueSurface,
            COLORBLIND_PATTERN_COLOR,
            ((i-COLORBLIND_NUM_PATTERNS+1)*COLORBLIND_PATTERN_SPACING,0),
            (i*COLORBLIND_PATTERN_SPACING,surfaceSize),
            round(COLORBLIND_PATTERN_WIDTH)
        )

    _colorblindPatterns = {
        "r" : redSurface,
        "g" : greenSurface,
        "b" : blueSurface
    }


_colorblindPatterns:dict[str,pygamePIL.Surface]
_preRenderColorblindPatterns()

def _getScaledShapeSize(shapeSize:float,layerIndex:int) -> float:
    return shapeSize * (LAYER_SIZE_REDUCTION**layerIndex)

def _drawShapePart(
    shapePart:gameObjects.ShapePart,
    shapeSize:float,
    partIndex:int,
    layerIndex:int,
    fullShape:gameObjects.Shape,
    colorSkin:gameObjects.ColorSkin,
    shapesConfig:gameObjects.ShapesConfiguration
    ) -> tuple[pygamePIL.Surface|None,pygamePIL.Surface|None]:
    # returns part with shadow, border

    borderSize = SHAPE_BORDER_SIZE
    halfBorderSize = borderSize / 2
    curShapeSize = _getScaledShapeSize(shapeSize,layerIndex)
    curPartSize = curShapeSize / 2

    withBorderPartSize = round(curPartSize+borderSize)
    partSurface = pygamePIL.Surface(
        (withBorderPartSize,withBorderPartSize),
        pygamePIL.SRCALPHA
    )
    partSurfaceForBorder = partSurface.copy()

    drawShadow = layerIndex != 0
    color = colorSkin.colors.get(shapePart.color)
    borderColor = SHAPE_BORDER_COLOR

    if shapePart.type is None:
        return None, None

    partShape = shapePart.type.code

    if partShape == "C":

        pygamePIL.draw.circle(partSurface,color, # main circle
            (halfBorderSize,withBorderPartSize-halfBorderSize),
            curPartSize,
            draw_top_right=True
        )

        pygamePIL.draw.circle(partSurfaceForBorder,borderColor, # circle border
            (halfBorderSize,withBorderPartSize-halfBorderSize),
            curPartSize+halfBorderSize,
            borderSize,
            draw_top_right=True
        )
        pygamePIL.draw.line(partSurfaceForBorder,borderColor, # left border
            (halfBorderSize,0),
            (halfBorderSize,withBorderPartSize),
            borderSize
        )
        pygamePIL.draw.line(partSurfaceForBorder,borderColor, # down border
            (0,withBorderPartSize-halfBorderSize),
            (withBorderPartSize,withBorderPartSize-halfBorderSize),
            borderSize
        )

        return partSurface, partSurfaceForBorder

    if partShape == "R":

        pygamePIL.draw.rect(partSurface,color, # main rect
            pygamePIL.Rect(halfBorderSize,halfBorderSize,curPartSize,curPartSize)
        )

        pygamePIL.draw.rect(partSurfaceForBorder,borderColor, # rect border
            pygamePIL.Rect(0,0,withBorderPartSize,withBorderPartSize),
            borderSize
        )

        return partSurface, partSurfaceForBorder

    if partShape == "S":

        points = [(curPartSize,0),(curPartSize/2,curPartSize),(0,curPartSize),(0,curPartSize/2)]
        points = [(halfBorderSize+x,halfBorderSize+y) for x,y in points]

        pygamePIL.draw.polygon(partSurface,color,points) # main polygon

        pygamePIL.draw.polygon(partSurfaceForBorder,borderColor,points,borderSize) # border polygon
        for point in points:
            pygamePIL.draw.circle(partSurfaceForBorder,borderColor,point,halfBorderSize-1) # fill in the missing vertices

        return partSurface, partSurfaceForBorder

    if partShape == "W":

        arcCenter = (halfBorderSize+(curPartSize*1.4),halfBorderSize+(curPartSize*-0.4))
        arcRadius = curPartSize * 1.18
        sideLength = curPartSize / 3.75

        pygamePIL.draw.rect(partSurface,color, # first fill in the whole part
            pygamePIL.Rect(halfBorderSize,halfBorderSize,curPartSize,curPartSize)
        )
        pygamePIL.draw.circle(partSurface,EMPTY_COLOR,arcCenter,arcRadius) # then carve out a circle

        pygamePIL.draw.circle(partSurfaceForBorder,borderColor,arcCenter,arcRadius+halfBorderSize,borderSize) # arc border
        pygamePIL.draw.line(partSurfaceForBorder,borderColor, # left border
            (halfBorderSize,0),
            (halfBorderSize,withBorderPartSize),
            borderSize
        )
        pygamePIL.draw.line(partSurfaceForBorder,borderColor, # down border
            (0,withBorderPartSize-halfBorderSize),
            (withBorderPartSize,withBorderPartSize-halfBorderSize),
            borderSize
        )
        pygamePIL.draw.line(partSurfaceForBorder,borderColor, # top edge border
            (halfBorderSize,halfBorderSize),
            (halfBorderSize+sideLength,halfBorderSize),
            borderSize
        )
        pygamePIL.draw.line(partSurfaceForBorder,borderColor, # right edge border
            (withBorderPartSize-halfBorderSize,withBorderPartSize-halfBorderSize-sideLength),
            (withBorderPartSize-halfBorderSize,withBorderPartSize-halfBorderSize),
            borderSize
        )

        return partSurface, partSurfaceForBorder

    if partShape == "H":

        points = [(0,0),((SQRT_3/2)*curPartSize,curPartSize/2),(0,curPartSize)]
        points = [(halfBorderSize+x,halfBorderSize+y) for x,y in points]

        pygamePIL.draw.polygon(partSurface,color,points) # main polygon

        pygamePIL.draw.polygon(partSurfaceForBorder,borderColor,points,borderSize) # border polygon
        for point in points:
            pygamePIL.draw.circle(partSurfaceForBorder,borderColor,point,halfBorderSize-1) # fill in the missing vertices

        return partSurface, partSurfaceForBorder

    if partShape == "F":

        semicircleRadius = ((3-SQRT_3)/4) * curPartSize
        triangleSideLength = 2 * semicircleRadius
        semicircleCenterX = (triangleSideLength*(SQRT_3/2)) / 2
        semicircleCenterY = (
            curPartSize
            - triangleSideLength
            + math.sqrt((semicircleRadius*semicircleRadius)-(semicircleCenterX*semicircleCenterX))
        )
        trianglePoints = [
            (0,curPartSize-triangleSideLength),
            ((SQRT_3/2)*triangleSideLength,curPartSize-semicircleRadius),
            (0,curPartSize)
        ]
        semicircleStartAngle = math.radians(360-30)
        semicircleStopAngle = math.radians(360-30-180)

        semicircleCenterX += halfBorderSize
        semicircleCenterY += halfBorderSize
        trianglePoints = [(halfBorderSize+x,halfBorderSize+y) for x,y in trianglePoints]

        pygamePIL.draw.polygon(partSurface,color,trianglePoints) # triangle part

        pygamePIL.draw.arc(partSurface,color,pygamePIL.Rect( # semicircle part
            semicircleCenterX-semicircleRadius,semicircleCenterY-semicircleRadius,triangleSideLength,triangleSideLength
        ),semicircleStartAngle,semicircleStopAngle,math.ceil(semicircleRadius))

        pygamePIL.draw.line(partSurfaceForBorder,borderColor,trianglePoints[0],trianglePoints[2],borderSize) # left border

        pygamePIL.draw.line(partSurfaceForBorder,borderColor,trianglePoints[1],trianglePoints[2],borderSize) # bottom border

        pygamePIL.draw.arc(partSurfaceForBorder,borderColor,pygamePIL.Rect( # semicircle border
            semicircleCenterX - semicircleRadius - halfBorderSize,
            semicircleCenterY - semicircleRadius - halfBorderSize,
            triangleSideLength + borderSize,
            triangleSideLength + borderSize
        ),semicircleStartAngle,semicircleStopAngle,borderSize)

        for point in trianglePoints:
            pygamePIL.draw.circle(partSurfaceForBorder,borderColor,point,halfBorderSize-1) # fill in the missing vertices

        return partSurface, partSurfaceForBorder

    if partShape == "G":

        points = [(0,0),((SQRT_3/6)*curPartSize,curPartSize/2),((SQRT_3/2)*curPartSize,curPartSize/2),(0,curPartSize)]
        points = [(halfBorderSize+x,halfBorderSize+y) for x,y in points]

        pygamePIL.draw.polygon(partSurface,color,points) # main polygon

        pygamePIL.draw.polygon(partSurfaceForBorder,borderColor,points,borderSize) # border polygon
        for point in points:
            pygamePIL.draw.circle(partSurfaceForBorder,borderColor,point,halfBorderSize-1) # fill in the missing vertices

        return partSurface, partSurfaceForBorder

    if partShape == "P":

        if shapesConfig.numPartsPerLayer == 4:
            pinCenter = (halfBorderSize+(curPartSize/3),halfBorderSize+(2*(curPartSize/3)))
        elif shapesConfig.numPartsPerLayer == 6:
            pinCenter = (halfBorderSize+((SQRT_2/6)*curPartSize),halfBorderSize+((1-(SQRT_6/6))*curPartSize))
        pinRadius = curPartSize/6

        if drawShadow:
            pygamePIL.draw.circle(partSurface,SHADOW_COLOR,pinCenter,pinRadius+halfBorderSize) # shadow

        pygamePIL.draw.circle(partSurface,PIN_COLOR,pinCenter,pinRadius) # main circle

        return partSurface, None

    if partShape == "c":

        darkenedColor = tuple(round(c/2) for c in color)

        if shapesConfig.numPartsPerLayer == 4:

            darkenedAreasOffset = 0 if layerIndex%2 == 0 else 22.5
            startAngle1 = math.radians(67.5-darkenedAreasOffset)
            stopAngle1 = math.radians(90-darkenedAreasOffset)
            startAngle2 = math.radians(22.5-darkenedAreasOffset)
            stopAngle2 = math.radians(45-darkenedAreasOffset)
            darkenedAreasRect = pygamePIL.Rect(
                halfBorderSize - curPartSize,
                halfBorderSize,
                2 * curPartSize,
                2 * curPartSize
            )

            if drawShadow:
                pygamePIL.draw.circle(partSurface,SHADOW_COLOR, # shadow
                    (halfBorderSize,withBorderPartSize-halfBorderSize),
                    curPartSize+halfBorderSize,
                    borderSize,
                    draw_top_right=True
                )

            pygamePIL.draw.circle(partSurface,color, # main circle
                (halfBorderSize,withBorderPartSize-halfBorderSize),
                curPartSize,
                draw_top_right=True
            )
            pygamePIL.draw.arc(partSurface,darkenedColor, # 1st darkened area
                darkenedAreasRect,
                startAngle1,
                stopAngle1,
                math.ceil(curPartSize)
            )
            pygamePIL.draw.arc(partSurface,darkenedColor, # 2nd darkened area
                darkenedAreasRect,
                startAngle2,
                stopAngle2,
                math.ceil(curPartSize)
            )

            return partSurface, None

        elif shapesConfig.numPartsPerLayer == 6:

            points = [(0,0),((SQRT_3/2)*curPartSize,curPartSize/2),(0,curPartSize)]
            points = [(halfBorderSize+x,halfBorderSize+y) for x,y in points]

            shadowPoints = [
                (points[0][0],points[0][1]-halfBorderSize),
                (points[1][0]+((SQRT_3/2)*halfBorderSize),points[1][1]-(halfBorderSize/2)),
                (points[2][0],points[2][1])
            ]

            sideMiddlePoint = ((points[0][0]+points[1][0])/2,(points[0][1]+points[1][1])/2)
            if layerIndex%2 == 0:
                darkenedArea = [points[0],sideMiddlePoint,points[2]]
            else:
                darkenedArea = [sideMiddlePoint,points[1],points[2]]

            if drawShadow:
                pygamePIL.draw.polygon(partSurface,SHADOW_COLOR,shadowPoints) # shadow

            pygamePIL.draw.polygon(partSurface,color,points) # main polygon

            pygamePIL.draw.polygon(partSurface,darkenedColor,darkenedArea) # darkened area

            return partSurface, None

    raise ValueError(f"Unknown shape type : {partShape}")

def _drawColorblindPatterns(layerSurface:pygamePIL.Surface,color:gameObjects.Color) -> None:

    curMask = pygamePIL.mask.from_surface(layerSurface,200)

    for colors,pattern in zip(
        (["r","m","y","w"],["g","y","c","w"],["b","c","m","w"]),
        _colorblindPatterns.values()
    ):
        if color.code not in colors:
            continue

        curPattern = pygamePIL.Surface(layerSurface.get_size(),pygamePIL.SRCALPHA)
        _blitCentered(pattern,curPattern)

        curPatternMasked = pygamePIL.Surface(curPattern.get_size(),pygamePIL.SRCALPHA)
        curMask.to_surface(curPatternMasked,curPattern,unsetcolor=None)

        layerSurface.blit(curPatternMasked,(0,0))

def _blitCentered(blitFrom:pygamePIL.Surface,blitTo:pygamePIL.Surface) -> None:
    blitTo.blit(
        blitFrom,
        (
            (blitTo.get_width()/2) - (blitFrom.get_width()/2),
            (blitTo.get_height()/2) - (blitFrom.get_height()/2)
        )
    )

def _rotateSurf(toRotate:pygamePIL.Surface,numParts:int,partIndex:int,layerIndex:int,shapeSize:float) -> pygamePIL.Surface:
    curShapeSize = _getScaledShapeSize(shapeSize,layerIndex)
    tempSurf = pygamePIL.Surface(
        (curShapeSize+SHAPE_BORDER_SIZE,)*2,
        pygamePIL.SRCALPHA
    )
    tempSurf.blit(toRotate,(curShapeSize/2,0))
    tempSurf = pygamePIL.transform.rotate(tempSurf,-((360/numParts)*partIndex))
    return tempSurf

# reduce displayed type annotations length
_defaultColorMode = ingameData.DEFAULT_COLOR_SCHEME.colorModesById["RGB"]
_defaultShapesConfig = ingameData.QUAD_SHAPES_CONFIG
def renderShape(
    shape:gameObjects.Shape,
    surfaceSize:int,
    colorMode:gameObjects.ColorMode=_defaultColorMode,
    shapesConfig:gameObjects.ShapesConfiguration=_defaultShapesConfig
) -> pygamePIL.Surface:

    returnSurface = pygamePIL.Surface((FAKE_SURFACE_SIZE,FAKE_SURFACE_SIZE),pygamePIL.SRCALPHA)
    pygamePIL.draw.circle(returnSurface,BG_CIRCLE_COLOR,(FAKE_SURFACE_SIZE/2,FAKE_SURFACE_SIZE/2),BG_CIRCLE_DIAMETER/2)

    for layerIndex, layer in enumerate(shape.layers):

        partBorders = []

        for partIndex, part in enumerate(layer):

            partSurface, partBorder = _drawShapePart(
                part,
                SHAPE_SIZE,
                partIndex,
                layerIndex,
                shape,
                colorMode.colorSkin,
                shapesConfig
            )
            partBorders.append(partBorder)

            if partSurface is None:
                continue

            rotatedLayer = _rotateSurf(partSurface,shape.numParts,partIndex,layerIndex,SHAPE_SIZE)
            if colorMode.colorblindPatterns and (part.color is not None):
                _drawColorblindPatterns(rotatedLayer,part.color)
            _blitCentered(rotatedLayer,returnSurface)

        for partIndex, border in enumerate(partBorders):

            if border is None:
                continue

            _blitCentered(_rotateSurf(border,shape.numParts,partIndex,layerIndex,SHAPE_SIZE),returnSurface)

    # pygame doesn't work well at low resolution so render at size 500 then downscale to the desired size
    return pygamePIL.transform.smoothscale(returnSurface,(surfaceSize,surfaceSize))