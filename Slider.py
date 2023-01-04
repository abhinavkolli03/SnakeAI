import pygame

pygame.init()


# Takes rectangle's size, position and a point. Returns true if that
# point is inside the rectangle and false if it isnt.
def pointInRectanlge(px, py, rw, rh, rx, ry):
    if px > rx and px < rx + rw:
        if py > ry and py < ry + rh:
            return True
    return False


# Blueprint to make sliders in the game
class Slider:
    def __init__(self, position: tuple, upperValue: float = 10, sliderWidth: float = 20,
                 text: str = "Editing features for simulation",
                 outlineSize: tuple = (140, 70)) -> None:
        self.position = position
        self.outlineSize = outlineSize
        self.text = text
        self.sliderWidth = sliderWidth
        self.upperValue = upperValue

    # returns the current value of the slider
    def getValue(self) -> float:
        value = self.sliderWidth / (self.outlineSize[0] / self.upperValue)
        return value

    # renders slider and the text showing the value of the slider
    def render(self, display: pygame.display) -> None:
        # draw outline and slider rectangles
        pygame.draw.rect(display, (0, 0, 0), (self.position[0], self.position[1],
                                              self.outlineSize[0], self.outlineSize[1]), 3)

        pygame.draw.rect(display, (0, 100, 255), (self.position[0], self.position[1],
                                              self.sliderWidth, self.outlineSize[1]))

        # determine size of font
        self.font = pygame.font.Font(pygame.font.get_default_font(), int((18 / 100) * self.outlineSize[1]))

        # create text surface with value
        valueSurf = self.font.render(f"{self.text}: {round(self.getValue(), 2)}", True, (0, 0, 0))

        # centre text
        textx = self.position[0] + (self.outlineSize[0] / 2) - (valueSurf.get_rect().width / 2)
        texty = self.position[1] + (self.outlineSize[1] / 2) - (valueSurf.get_rect().height / 2) - 15

        display.blit(valueSurf, (textx, texty))

    # allows users to change value of the slider by dragging it.
    def changeValue(self) -> None:
        # If mouse is pressed and mouse is inside the slider
        mousePos = pygame.mouse.get_pos()
        if pointInRectanlge(mousePos[0], mousePos[1]
                , self.outlineSize[0], self.outlineSize[1], self.position[0], self.position[1]):
            if pygame.mouse.get_pressed()[0]:
                # the size of the slider
                self.sliderWidth = mousePos[0] - self.position[0]

                # limit the size of the slider
                if self.sliderWidth < 1:
                    self.sliderWidth = 0
                if self.sliderWidth > self.outlineSize[0]:
                    self.sliderWidth = self.outlineSize[0]