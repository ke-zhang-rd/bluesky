from bluesky import RunEngine
from bluesky.callbacks.best_effort import BestEffortCallback
from bluesky.callbacks.mpl_plotting import scatter_factory
from bluesky.callbacks import Runrouter
from bluesky.utils import install_kicker
from databroker import Broker
from bluesky.utils import ProgressBarManager
from ophyd.sim import det1, det2  # two simulated detectors
from bluesky.plans import count

RE = RunEngine({})
bec = BestEffortCallback()
RE.subscribe(bec)
install_kicker()
db = Broker.named('temp')
RE.subscribe(db.insert)
RE.waiting_hook = ProgressBarManager()
dets = [det1, det2]   # a list of any number of detectors

callback_factories = [scatter_factory]
router = Runrouter(callback_factories)
RE.subscribe(router)
RE(count(dets))
