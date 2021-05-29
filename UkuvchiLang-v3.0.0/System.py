from object_ import Object
import datetime

class System(Object):
    def __init__(self, type_): 
        super().__init__(type_, 0)
        self.v=self
        self.methods={"date": self.uk_date}
    def uk_date(self):
        a = datetime.datetime.today()
        print(a)   
    