from bluesky import RunEngine
from bluesky.callbacks.callback_factories import grid_factory
from bluesky.callbacks.callback_factories import scatter_factory
from bluesky.callbacks.core import RunRouter
from bluesky.utils import install_kicker
from databroker import Broker
from bluesky.utils import ProgressBarManager
from ophyd.sim import det4, motor1, motor2
from bluesky.plans import scan_nd
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.utils import install_kicker
from cycler import cycler

RE = RunEngine({})
install_kicker()

bec = BestEffortCallback()
#RE.subscribe(bec)

callback_factories = [scatter_factory]
router = RunRouter(callback_factories)
RE.subscribe(router)
dets = [det4]
motor1.delay = 1
motor2.delay = 1
traj1 = cycler(motor1, [1, 3, 2])
traj2 = cycler(motor2, [1, 2, 3])
RE(scan_nd(dets, (traj1 + traj2)))

