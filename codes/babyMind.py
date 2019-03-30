import event #file with the definition of event
#event is an object wich contains 3 methods:
 # -modPixels(idPixel,value) pixel n° idPixel take the value of value
 # -getPixels() return the list of getPixels
 # -getID() return the id of the event



listEvent=[event.event(i) for i in range(100000)]
# for evenement in listEvent:
#     print(evenement.getID())
print (listEvent[3].getPixels())
listEvent[3].modPixels(1,28)
print (listEvent[3].getPixels())
# event1=event.event(1)
# event2=event.event(2)
# print(event1.getPixels())
# event2.modPixels(0,255)
# print(event2.getPixels())
