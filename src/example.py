class Advanced(object):
    def __init__(self, name):
        self.name = name
    def Description():
        return 'This is an advanced class.'
    def ClassDescription(cls):
        return 'This is advanced class: %s' % repr(cls)
    Description = staticmethod(Description)
    ClassDescription = classmethod(ClassDescription)

obj1 = Advanced('Nectarine')
print obj1.Description()
print obj1.ClassDescription()
print '=' * 30
print Advanced.Description()
print  Advanced.ClassDescription()
