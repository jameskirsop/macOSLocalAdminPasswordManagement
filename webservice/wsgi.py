import os, sys, site, pathlib
print(pathlib.Path(__file__).parent.absolute())

site.addsitedir(f'{pathlib.Path(__file__).parent.absolute()}/venv/lib/python3.7/site-packages')

os.chdir(os.path.dirname(__file__))

activate_this = f"{pathlib.Path(__file__).parent.absolute()}/venv/bin/activate_this.py"
exec(compile(open(activate_this).read(), activate_this, 'exec'), dict(__file__=activate_this))

sys.path.append(os.path.dirname(__file__))

import bottle
import server
from bottle.ext import beaker

application = bottle.default_app()
application = beaker.middleware.SessionMiddleware(bottle.app())