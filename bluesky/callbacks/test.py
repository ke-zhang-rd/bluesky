from bluesky import RunEngine
from bluesky.callbacks.callback_factories import grid_factory
from bluesky.callbacks.callback_factories import scatter_factory
from bluesky.callbacks.core import RunRouter
from bluesky.utils import install_kicker
from databroker import Broker
from bluesky.utils import ProgressBarManager
from ophyd.sim import det4, motor1, motor2
from bluesky.plans import scan
from bluesky.plans import grid_scan

RE = RunEngine({})
install_kicker()
db = Broker.named('temp')
RE.subscribe(db.insert)
RE.waiting_hook = ProgressBarManager()

callback_factories = [scatter_factory]
router = RunRouter(callback_factories)
RE.subscribe(router)
dets = [det4]   # a list of any number of detectors
RE(grid_scan(dets, motor1, -1.5, 1.5, 3,motor2, -0.1, 0.1, 5, False))
