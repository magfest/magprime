from uber.common import *

@all_renderable(c.PEOPLE)
class Root:
    def grouped(self, session):
        return {
            'test': "testvalue",
        }