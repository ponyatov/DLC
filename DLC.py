import config

import os, sys, re
import datetime as dt

## base object (hyper)graph node = Marvin Minsky's Frame
class Object:
    def __init__(self, V):
        ## type/class tag /required for PLY/
        self.type = self.__class__.__name__.lower()
        ## scalar value: name, number, string..
        self.value = V
        ## associative array = env/namespace = grammar attrubites
        self.slot = {}
        ## ordered container = vector = stack = queue = AST subtree
        self.nest = []

    ## Python types wrapper
    def box(self, that):
        if isinstance(that, Object): return that
        if isinstance(that, str): return S(that)
        if that is None: return Nil()
        raise TypeError(['box', type(that), that])

    ## @name text tree dump

    ## `print` callback
    def __repr__(self): return self.dump(test=False)

    ## repeatable print for tests
    def test(self): return self.dump(test=True)

    ## full tree dump
    def dump(self, cycle=[], depth=0, prefix='', test=False):
        # head
        def pad(depth): return '\n' + '\t' * depth
        ret = pad(depth) + self.head(prefix, test)
        # cycle block
        if not depth: cycle = []
        if self in cycle: return ret + ' _/'
        else: cycle.append(self)
        # slot{}s
        for i in self.keys():
            ret += self[i].dump(cycle, depth + 1, f'{i} = ', test)
        # nest[]ed
        for j, k in enumerate(self):
            ret += k.dump(cycle, depth + 1, f'{j}: ', test)
        # subtree
        return ret

    ## single `<T:V>` header
    def head(self, prefix='', test=False):
        gid = '' if test else f' @{id(self):x}'
        return f'{prefix}<{self.type}:{self.value}>{gid}'

    ## @name operator

    ## ` A.keys() `
    def keys(self): return sorted(self.slot.keys())

    ## ` iter(A) `
    def __iter__(self): return iter(self.nest)

    ## ` len(A) `
    def __len__(self): return len(self.nest)

    ## ` A // B -> A.push(B) `
    def __floordiv__(self, that):
        self.nest.append(self.box(that)); return self

    ## ` A[key] `
    def __getitem__(self, key):
        if isinstance(key, str): return self.slot[key]
        if isinstance(key, int): return self.nest[key]
        raise TypeError(['__getitem__', type(key), key])

    ## ` A[key] = that `
    def __setitem__(self, key, that):
        that = self.box(that)
        if isinstance(key, str): self.slot[key] = that; return self
        if isinstance(key, int): self.nest[key] = that; return self
        raise TypeError(['__setitem__', type(key), key])

    ## ` A << B -> A[B.type] `
    def __lshift__(self, that):
        that = self.box(that)
        return self.__setitem__(that.type, that)

    ## ` A >> B -> A[B.value] `
    def __rshift__(self, that):
        that = self.box(that)
        return self.__setitem__(that.value, that)


class Primitive(Object):
    ## evaluates to itself
    def eval(self, env): return self

class Num(Primitive):
    def __init__(self, F): Primitive.__init__(self, float(F))

class Int(Num):
    def __init__(self, N): Primitive.__init__(self, int(N))

class Atom(Primitive):
    def eval(self, env): return env[self.value]

class Nil(Primitive):
    def __init__(self): super().__init__('')
    def __bool__(self): return False

## nested source code block ~ string
class S(Primitive): pass


class Container(Object): pass

class Vector(Container): pass

class Map(Container): pass

## code section
class Sec(Container, S): pass


## EDS: Executable Data Structure
class Active(Object): pass

class Env(Active, Map):
    def __init__(self, V):
        super().__init__(V)
        self.compile = Nil()

glob = Env('global'); glob << glob >> glob

class Op(Active): pass
class Quote(Op):
    def __init__(self, V='`'): super().__init__(V)
    def eval(self, env): return self.nest[0]

class Cmd(Active):
    def __init__(self, F):
        assert callable(F)
        super().__init__(F.__name__)
        self.fn = F

    def eval(self, env): return self.fn(env)
    def apply(self, env, that): return self.fn(env, that)


def nop(env=glob, that=None): pass
glob >> Cmd(nop)


class Meta(Object): pass

class Module(Meta): pass

class Project(Module): pass


class IO(Object): pass

class Path(IO): pass

class Dir(IO): pass

class File(IO): pass


import ply.lex as lex

tokens = ['int', 'atom', 'quote']

t_ignore = ' \t\r'

def t_nl(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore_comment = r'\#.*'

def t_quote(t):
    r'`'
    t.value = Quote(); return t

def t_int(t):
    r'[+\-]?[0-9]+'
    t.value = Int(t.value); return t

def t_atom(t):
    r'[^ \t\r\n]+'
    t.value = Atom(t.value); return t

def t_error(t): raise SyntaxError(t)

lexer = lex.lex()


import ply.yacc as yacc


def p_REPL_none(p):
    ' REPL : '
    pass
def p_REPL_recur(p):
    ' REPL : REPL ex '
    env = p.parser.env
    item = p[2].eval(env) # lookup -> pritimive/definition
    if env.compile:
        env.compile // item # compile
    else:
        env // item.eval(env) # execute


def p_int(p):
    ' ex : int '
    p[0] = p[1]

def p_atom(p):
    ' ex : atom '
    p[0] = p[1]

def p_quote(p):
    ' ex : quote ex '
    p[0] = p[1] // p[2]


def p_error(p): raise SyntaxError(t)

parser = yacc.yacc(debug=False, write_tables=False)


import traceback

def REPL(env=glob):
    print(env)
    parser.env = env
    while True:
        try:
            parser.parse(input(f'\n{env.head(test=True)} '))
            # while True:
            #     token = lexer.token()
            #     if not token: break
            #     if env.compile:
            #         env.compile // token.eval(env)
            #     else:
            #         env // token.eval(env).eval(env)
            print(env)
        except EOFError:
            sys.exit(0)
            # os._exit(0)
        except:
            traceback.print_exc()

class Net(IO): pass

class IP(Net): pass

class Port(Net, Int): pass

class Web(Net): pass

web = Web('interface'); glob << web
web << IP(config.HOST); web << Port(config.PORT)


from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

watch = Observer()

try: watch.start()
except: pass

class py_restart(FileSystemEventHandler):
    def on_closed(self, event):
        if not event.is_directory:
            if self.sio: self.sio.emit('reload')
            os._exit(0)

    def watch(sio=None):
        item = py_restart(); item.sio = sio
        pyfile = sys.argv[0].split('/')[-1]
        watch.schedule(item, f'{pyfile}')
        watch.schedule(item, f'test_{pyfile}')

class flask_reload(FileSystemEventHandler):
    def on_closed(self, event):
        if not event.is_directory:
            if self.sio: self.sio.emit('reload')

    def watch(sio=None):
        item = flask_reload(); item.sio = sio
        watch.schedule(item, "static", recursive=True)
        watch.schedule(item, "templates", recursive=True)


import flask
from flask_socketio import SocketIO

class Engine(Web):
    def __init__(self, V='Flask'):
        super().__init__(V)
        self.app = flask.Flask(__name__)
        self.app.config['SECRET_KEY'] = config.SECRET
        self.sio = flask_reload.sio = SocketIO(self.app)

    def eval(self, env):
        @self.app.route('/')
        def index():
            return flask.render_template('index.html', glob=glob, env=env)

        @self.sio.on('localtime')
        def localtime(msg):
            now = dt.datetime.now()
            dd = now.strftime('%d.%m.%Y')
            tt = now.strftime('%H:%M:%S')
            self.sio.emit('localtime', {'date': dd, 'time': tt})

        @self.sio.on('connect')
        def connect(msg):
            localtime(msg)

        py_restart.watch(self.sio); flask_reload.watch(self.sio)

        self.sio.run(self.app, debug=True,
                     host=web['ip'].value, port=web['port'].value)

engine = Engine(); web << engine


if __name__ == '__main__':
    if sys.argv[1] == 'web':
        engine.eval(glob)
    if sys.flags.interactive:
        py_restart.watch(None)
        REPL(glob)
