

class Pattern:
    _persistent: bool

    def _activate(self, model):
        pass

    def _deactivate(self, model):
        tag = self.tag
        if self._persistent:
            model.loadConst(tag=tag)
        else:
            model.removePattern(tag=tag)


class Acceleration(Pattern):
    def __init__(self, tag, dof, data, dt=None, time=None, persist=True):
        self.tag = tag
        self._dof = dof
        self._data = data
        if dt is not None:
            pass
        super().__init__(persist=persist)


    def _activate(self, model):
        if self.tag not in model._patterns:
            model.pattern("UniformExcitation", 
                          self.tag, self._dof, self._data)
        else:
            model.activatePattern(tag=self.tag)
