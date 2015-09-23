from recursive import RecObject, RecFunc

stack_classes = [RecObject, RecFunc]

class stack(object):
    def __init__(self, iterable):
        self._l = iterable
        self._iter = iter(iterable)

    def __iter__(self):
        return self.__class__(self._l)

    def next(self):
        return next(self._iter)

    def __getattr__(self, attr):
        return StackAttr(self._l, attr)

    def __call__(self, *args, **kwargs):
        return StackCall(self._l, *args, **kwargs)

    def __repr__(self):
        return "stack("+self._l.__repr__()+")"

    def __add__(self, right):
        if isinstance(right, tuple(stack_classes)):
            right = [right]
        return stack(list(self._l) +right)


class StackAttr(object):
    def __init__(self, l, attr):
        self.l = l
        self.iterable = iter(l)
        self.attr = attr

    def __call__(self, *args, **kwargs):
        return StackMethod(self.l, self.attr, args, kwargs)

    def __iter__(self):
        return self.__class__(self.l, self.attr)

    def next(self):
        return getattr(next(self.iterable), self.attr)

    def __repr__(self):
        return "(obj.%s for obj in %s"%(self.attr, self.l.__repr__())




class StackCall(object):
    def __init__(self, l, args=None, kwargs=None):
        self.l = l
        self.iterable = iter(l)

        self.args = args or tuple()
        self.kwargs = kwargs or {}

    def __iter__(self):
        return self.__class__(self.l, self.args, self.kwargs)

    def next(self):
        item = next(self.iterable)
        return item(*self.args, **self.kwargs)

    def __repr__(self):
        return "(obj(*%s, **%s) for obj in %s"%(self.args, self.kwargs, self.l.__repr__())



class StackMethod(object):
    def __init__(self, l, attr=None, args=None, kwargs=None):
        self.l = l
        self.iterable = iter(l)
        self.attr = attr

        self.args = args or tuple()
        self.kwargs = kwargs or {}

    def __iter__(self):
        return self.__class__(self.l, self.attr, self.args, self.kwargs)

    def next(self):
        item = getattr(next(self.iterable), self.attr)
        return item(*self.args, **self.kwargs)

    def __repr__(self):
        return "(obj.%s(*%s, **%s) for obj in %s"%(self.attr, self.args, self.kwargs, self.l.__repr__())



class stackd(object):
    def __init__(self, *args, **kwargs):
        self._d = dict(*args, **kwargs)
        self._iter = self._d.iteritems()

    def __iter__(self):
        return self.__class__(self._d)

    def next(self):
        return next(self._iter)

    def __getattr__(self, attr):
        return StackdAttr(self._d, attr)

    def __call__(self, *args, **kwargs):
        return StackdCall(self._d, *args, **kwargs)

    def __repr__(self):
        return "stack("+self._d.__repr__()+")"



class StackdAttr(object):
    def __init__(self, d, attr):
        self.d = d
        self.iterable = d.iteritems()
        self.attr = attr

    def __call__(self, *args, **kwargs):
        return StackdMethod(self.d, self.attr, args, kwargs)

    def __iter__(self):
        return self.__class__(self.d, self.attr)

    def next(self):
        name, item = next(self.iterable)
        return name, getattr(item, self.attr)

    def __repr__(self):
        return "((name, obj.%s) for obj in %s"%(self.attr, self.d.__repr__())




class StackdCall(object):
    def __init__(self, d, args=None, kwargs=None):
        self.d = d
        self.iterable = d.iteritems()

        self.args = args or tuple()
        self.kwargs = kwargs or {}

    def __iter__(self):
        return self.__class__(self.d, self.args, self.kwargs)

    def next(self):
        name, item = next(self.iterable)

        return name, item(*self.args, **self.kwargs)

    def __repr__(self):
        return "((name, obj(*%s, **%s)) for obj in %s"%(self.args, self.kwargs, self.d.__repr__())



class StackdMethod(object):
    def __init__(self, d, attr=None, args=None, kwargs=None):
        self.d = d
        self.iterable = d.iteritems()
        self.attr = attr

        self.args = args or tuple()
        self.kwargs = kwargs or {}

    def __iter__(self):
        return self.__class__(self.d, self.attr, self.args, self.kwargs)

    def next(self):
        name, item = next(self.iterable)
        return name, getattr(item, self.attr)(*self.args, **self.kwargs)

    def __repr__(self):
        return "(obj.%s(*%s, **%s) for obj in %s"%(self.attr, self.args, self.kwargs, self.d.__repr__())






