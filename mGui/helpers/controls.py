import maya.mel as mel
from StringIO import StringIO
import constants
        

_is_widget  = lambda helptext: 'dragCallback' in helptext
_is_layout = lambda helptext: 'childArray' in helptext
__layout_cmds = []  # filled out on module initialize
__control_cmds = [] # filled out on module initialize
for item in mel.eval('help -list "*"'):
    help = mel.eval('help %s' % item)
    if _is_widget(help):
        if _is_layout(help):
            __layout_cmds.append(item)
        else:
            __control_cmds.append(item)



                      

class CommandInfo(object):
    '''
    This class uses the mel help strings for commands to generate class wrapper classes
    '''
    DEFAULTS = constants.CONTROL_ATTRIBS
    INHERITS = 'Control'
    
    
    def __init__(self, name, **flags ):
        self.Name = name
        self.Flags = flags
    
    def template(self):
        code = StringIO()
        code.write('class %s(%s):\n' % (self.Name[0].upper() + self.Name[1:], self.INHERITS))
        code.write("    '''Wrapper class for cmds.%s'''\n"  % self.Name)
        code.write('    CMD = cmds.%s\n' % self.Name)
        attribs = [k for k in self.Flags.values() if not k in self.DEFAULTS]
        ##attribs += [k for k in self.Flags.keys() if not k in _CONTROL_ATTRIBS]
        attribs.sort()
        # note this deliberately excludes short names of callbacks!
        callbacks = [c for c in attribs if 'Command' in c or 'Callback' in c] 
        attribs = list(set(attribs) - set(callbacks))
        quoted = lambda p : "'%s'" % p
        attrib_names = map (quoted, attribs)
        code.write('    _ATTRIBS = [%s]\n' %','.join(attrib_names))
        callback_names = map (quoted, callbacks)
        code.write('    _CALLBACKS = [%s]\n' %','.join(callback_names))
        return code.getvalue()
        
    @classmethod    
    def from_command(cls, commandname):
        if hasattr(commandname, "__name__"): commandname = commandname.__name__
        helptext  = mel.eval("help %s;" % commandname)
        if not helptext: raise RuntimeError, 'no command "%s" found' % commandname
        results = {}
        for line in helptext.split("\n")[4:-2]:
            tokens = line.split()
            if len(tokens) > 1:
                results[str(tokens[0][1:])] = str(tokens[1][1:])
        return cls(commandname, **results)


class LayoutInfo(CommandInfo):
    DEFAULTS = constants.CONTROL_ATTRIBS + constants.LAYOUT_ATTRIBS
    INHERITS = 'Layout'
    

def generate_controls(filename):
    with open (filename, 'wt') as filehandle:
        filehandle.write("'''\nmGui wrapper classes\n\nAuto-generated wrapper classes for use with mGui\n'''\n\n")
        filehandle.write('import maya.cmds as cmds\n')
        filehandle.write('from .core import Control\n')
        
        
        
        for each_class in constants.CONTROL_COMMANDS:
            try:
                filehandle.write(CommandInfo.from_command(each_class).template())
                filehandle.write('\n\n')
            except RuntimeError:
                filehandle.write("# command '%s' not present in this maya" % each_class)

def generate_layouts(filename):
    with open (filename, 'wt') as filehandle:
        filehandle.write("'''\nmGui wrapper classes\n\nAuto-generated wrapper classes for use with mGui\n'''\n\n")
        filehandle.write('import maya.cmds as cmds\n')
        filehandle.write('from .core import Layout\n\n')
        for each_class in constants.LAYOUT_COMMANDS:
            try:
                filehandle.write(LayoutInfo.from_command(each_class).template())
                filehandle.write('\n\n')
            except RuntimeError:
                filehandle.write("# command '%s' not present in this maya" % each_class)


                           
            