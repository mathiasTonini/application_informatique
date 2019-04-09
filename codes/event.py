class event:

    # an event is defined by 144 pixels and id (to check if it's necessary)
    # with an event we can access to the 144 pixels, and change those pixels.

    # be careful ! pixels is a list :-> first pixels is 0 ans pixels go from 0 to 143
    self.trailer1
    self.trailer2
    def __init__(self,ident):
        self.id = ident  #id event, numero de l'évenemt dans la liste.
        self.pixels=[0 for i in range(144)]

    #methode to change the value of a pixel
    def modifPixels(self,idPixel,value):
        self.pixels[idPixel]=value
    def getPixels(self):
        return self.pixels
    def getID(self):
        return self.id
    def changeTrailer1(self,value)
        self.trailer1=value
    def changeTrailer2(self,value)
        self.trailer2=value
    def getTrailer1(self)
        return self.trailer1
    def getTrailer2
        return self.trailer2
