# coding: UTF-8
import sys
bstack1ll11l_opy_ = sys.version_info [0] == 2
bstack111111l_opy_ = 2048
bstack111l1ll_opy_ = 7
def bstack11l1_opy_ (bstack1llllll1_opy_):
    global bstack1l11ll_opy_
    bstack1ll111l_opy_ = ord (bstack1llllll1_opy_ [-1])
    bstack1l1l1l1_opy_ = bstack1llllll1_opy_ [:-1]
    bstack1l111_opy_ = bstack1ll111l_opy_ % len (bstack1l1l1l1_opy_)
    bstack11ll1ll_opy_ = bstack1l1l1l1_opy_ [:bstack1l111_opy_] + bstack1l1l1l1_opy_ [bstack1l111_opy_:]
    if bstack1ll11l_opy_:
        bstack11l1ll_opy_ = unicode () .join ([unichr (ord (char) - bstack111111l_opy_ - (bstack11111ll_opy_ + bstack1ll111l_opy_) % bstack111l1ll_opy_) for bstack11111ll_opy_, char in enumerate (bstack11ll1ll_opy_)])
    else:
        bstack11l1ll_opy_ = str () .join ([chr (ord (char) - bstack111111l_opy_ - (bstack11111ll_opy_ + bstack1ll111l_opy_) % bstack111l1ll_opy_) for bstack11111ll_opy_, char in enumerate (bstack11ll1ll_opy_)])
    return eval (bstack11l1ll_opy_)
import json
import subprocess
import threading
import time
import sys
import grpc
import os
from browserstack_sdk import sdk_pb2_grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack111111ll11_opy_ import bstack111111l11l_opy_
from browserstack_sdk.sdk_cli.bstack1llll11lll1_opy_ import bstack1llll11l11l_opy_
from browserstack_sdk.sdk_cli.bstack1lll1ll1lll_opy_ import bstack1lll11111ll_opy_
from browserstack_sdk.sdk_cli.bstack1lll1l1l11l_opy_ import bstack1lll11lllll_opy_
from browserstack_sdk.sdk_cli.bstack1lll1l11l1l_opy_ import bstack1lll1l1llll_opy_
from browserstack_sdk.sdk_cli.bstack1lll11l1l11_opy_ import bstack1lll1111lll_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l1ll1ll_opy_ import bstack1lll1l1l1l1_opy_
from browserstack_sdk.sdk_cli.bstack1ll1llll111_opy_ import bstack1ll1ll111l1_opy_
from browserstack_sdk.sdk_cli.bstack1lll11l11l1_opy_ import bstack1llll111lll_opy_
from browserstack_sdk.sdk_cli.bstack1lll1l1ll11_opy_ import bstack1ll1llll11l_opy_
from browserstack_sdk.sdk_cli.bstack1llll111l1_opy_ import bstack1llll111l1_opy_, bstack11l1lllll1_opy_, bstack11l11ll1ll_opy_
from browserstack_sdk.sdk_cli.pytest_bdd_framework import PytestBDDFramework
from browserstack_sdk.sdk_cli.bstack1lll11111l1_opy_ import bstack1ll1ll1llll_opy_
from browserstack_sdk.sdk_cli.bstack1lll1l1lll1_opy_ import bstack1llll1l11l1_opy_
from browserstack_sdk.sdk_cli.bstack1llllll1l1l_opy_ import bstack1lllll111ll_opy_
from browserstack_sdk.sdk_cli.bstack1lll1ll11ll_opy_ import bstack1lll1llllll_opy_
from bstack_utils.helper import Notset, bstack1lll11l1lll_opy_, get_cli_dir, bstack1llll1l1111_opy_, bstack1l1l11l111_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework
from browserstack_sdk.sdk_cli.utils.bstack1lll1111ll1_opy_ import bstack1llll111111_opy_
from browserstack_sdk.sdk_cli.utils.bstack11l1llll11_opy_ import bstack1l1111ll11_opy_
from bstack_utils.helper import Notset, bstack1lll11l1lll_opy_, get_cli_dir, bstack1llll1l1111_opy_, bstack1l1l11l111_opy_, bstack1l11l1l1l1_opy_, bstack11l11l1111_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1lll1l111ll_opy_, bstack1lll1111l1l_opy_, bstack1lll1ll1l1l_opy_, bstack1llll111l1l_opy_
from browserstack_sdk.sdk_cli.bstack1llllll1l1l_opy_ import bstack1lllll1ll1l_opy_, bstack1llllllllll_opy_, bstack1llll1lll11_opy_
from bstack_utils.constants import *
from bstack_utils.bstack11ll1lllll_opy_ import bstack1111l1l11_opy_
from bstack_utils import bstack1l1111111_opy_
from typing import Any, List, Union, Dict
import traceback
from google.protobuf.json_format import MessageToDict
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
from functools import wraps
from bstack_utils.measure import measure
from bstack_utils.messages import bstack11l1ll11ll_opy_, bstack11l11lll1l_opy_
logger = bstack1l1111111_opy_.get_logger(__name__, bstack1l1111111_opy_.bstack1lll11lll1l_opy_())
def bstack1ll1ll11ll1_opy_(bs_config):
    bstack1lll11llll1_opy_ = None
    bstack1ll1l1ll11l_opy_ = None
    try:
        bstack1ll1l1ll11l_opy_ = get_cli_dir()
        bstack1lll11llll1_opy_ = bstack1llll1l1111_opy_(bstack1ll1l1ll11l_opy_)
        bstack1llll11l111_opy_ = bstack1lll11l1lll_opy_(bstack1lll11llll1_opy_, bstack1ll1l1ll11l_opy_, bs_config)
        bstack1lll11llll1_opy_ = bstack1llll11l111_opy_ if bstack1llll11l111_opy_ else bstack1lll11llll1_opy_
        if not bstack1lll11llll1_opy_:
            raise ValueError(bstack11l1_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤ࡫࡯࡮ࡥࠢࡖࡈࡐࡥࡃࡍࡋࡢࡆࡎࡔ࡟ࡑࡃࡗࡌࠧႡ"))
    except Exception as ex:
        logger.debug(bstack11l1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡥࡱࡺࡲࡱࡵࡡࡥ࡫ࡱ࡫ࠥࡺࡨࡦࠢ࡯ࡥࡹ࡫ࡳࡵࠢࡥ࡭ࡳࡧࡲࡺࠢࡾࢁࠧႢ").format(ex))
        bstack1lll11llll1_opy_ = os.environ.get(bstack11l1_opy_ (u"ࠥࡗࡉࡑ࡟ࡄࡎࡌࡣࡇࡏࡎࡠࡒࡄࡘࡍࠨႣ"))
        if bstack1lll11llll1_opy_:
            logger.debug(bstack11l1_opy_ (u"ࠦࡋࡧ࡬࡭࡫ࡱ࡫ࠥࡨࡡࡤ࡭ࠣࡸࡴࠦࡓࡅࡍࡢࡇࡑࡏ࡟ࡃࡋࡑࡣࡕࡇࡔࡉࠢࡩࡶࡴࡳࠠࡦࡰࡹ࡭ࡷࡵ࡮࡮ࡧࡱࡸ࠿ࠦࠢႤ") + str(bstack1lll11llll1_opy_) + bstack11l1_opy_ (u"ࠧࠨႥ"))
        else:
            logger.debug(bstack11l1_opy_ (u"ࠨࡎࡰࠢࡹࡥࡱ࡯ࡤࠡࡕࡇࡏࡤࡉࡌࡊࡡࡅࡍࡓࡥࡐࡂࡖࡋࠤ࡫ࡵࡵ࡯ࡦࠣ࡭ࡳࠦࡥ࡯ࡸ࡬ࡶࡴࡴ࡭ࡦࡰࡷ࠿ࠥࡹࡥࡵࡷࡳࠤࡲࡧࡹࠡࡤࡨࠤ࡮ࡴࡣࡰ࡯ࡳࡰࡪࡺࡥ࠯ࠤႦ"))
    return bstack1lll11llll1_opy_, bstack1ll1l1ll11l_opy_
bstack1ll1l1ll1l1_opy_ = bstack11l1_opy_ (u"ࠢ࠺࠻࠼࠽ࠧႧ")
bstack1lll11l1ll1_opy_ = bstack11l1_opy_ (u"ࠣࡴࡨࡥࡩࡿࠢႨ")
bstack1lll1llll1l_opy_ = bstack11l1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡅࡏࡍࡤࡈࡉࡏࡡࡖࡉࡘ࡙ࡉࡐࡐࡢࡍࡉࠨႩ")
bstack1lll1l11ll1_opy_ = bstack11l1_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡆࡐࡎࡥࡂࡊࡐࡢࡐࡎ࡙ࡔࡆࡐࡢࡅࡉࡊࡒࠣႪ")
bstack111l1ll11_opy_ = bstack11l1_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅ࡚࡚ࡏࡎࡃࡗࡍࡔࡔࠢႫ")
bstack1lll1ll1111_opy_ = re.compile(bstack11l1_opy_ (u"ࡷࠨࠨࡀ࡫ࠬ࠲࠯࠮ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࢁࡈࡓࠪ࠰࠭ࠦႬ"))
bstack1lll1lll1ll_opy_ = bstack11l1_opy_ (u"ࠨࡤࡦࡸࡨࡰࡴࡶ࡭ࡦࡰࡷࠦႭ")
bstack1lll1llll11_opy_ = [
    bstack11l1lllll1_opy_.bstack11l1111l1l_opy_,
    bstack11l1lllll1_opy_.CONNECT,
    bstack11l1lllll1_opy_.bstack111l1111_opy_,
]
class SDKCLI:
    _1llll11ll1l_opy_ = None
    process: Union[None, Any]
    bstack1lll11l111l_opy_: bool
    bstack1lll111ll1l_opy_: bool
    bstack1lll1111l11_opy_: bool
    bin_session_id: Union[None, str]
    cli_bin_session_id: Union[None, str]
    cli_listen_addr: Union[None, str]
    bstack1llll1l11ll_opy_: Union[None, grpc.Channel]
    bstack1ll1ll1l111_opy_: str
    test_framework: TestFramework
    bstack1llllll1l1l_opy_: bstack1lllll111ll_opy_
    session_framework: str
    config: Union[None, Dict[str, Any]]
    bstack1ll1lllllll_opy_: bstack1ll1llll11l_opy_
    accessibility: bstack1lll11111ll_opy_
    bstack11l1llll11_opy_: bstack1l1111ll11_opy_
    ai: bstack1lll11lllll_opy_
    bstack1ll1ll1111l_opy_: bstack1lll1l1llll_opy_
    bstack1lll111llll_opy_: List[bstack1llll11l11l_opy_]
    config_testhub: Any
    config_observability: Any
    config_accessibility: Any
    bstack1lll111l11l_opy_: Any
    bstack1ll1lll1l1l_opy_: Dict[str, timedelta]
    bstack1llll1l1l1l_opy_: str
    bstack111111ll11_opy_: bstack111111l11l_opy_
    def __new__(cls):
        if not cls._1llll11ll1l_opy_:
            cls._1llll11ll1l_opy_ = super(SDKCLI, cls).__new__(cls)
        return cls._1llll11ll1l_opy_
    def __init__(self):
        self.process = None
        self.bstack1lll11l111l_opy_ = False
        self.bstack1llll1l11ll_opy_ = None
        self.bstack1ll1llllll1_opy_ = None
        self.cli_bin_session_id = None
        self.cli_listen_addr = os.environ.get(bstack1lll1l11ll1_opy_, None)
        self.bstack1ll1lll11ll_opy_ = os.environ.get(bstack1lll1llll1l_opy_, bstack11l1_opy_ (u"ࠢࠣႮ")) == bstack11l1_opy_ (u"ࠣࠤႯ")
        self.bstack1lll111ll1l_opy_ = False
        self.bstack1lll1111l11_opy_ = False
        self.config = None
        self.config_testhub = None
        self.config_observability = None
        self.config_accessibility = None
        self.bstack1lll111l11l_opy_ = None
        self.test_framework = None
        self.bstack1llllll1l1l_opy_ = None
        self.bstack1ll1ll1l111_opy_=bstack11l1_opy_ (u"ࠤࠥႰ")
        self.session_framework = None
        self.logger = bstack1l1111111_opy_.get_logger(self.__class__.__name__, bstack1l1111111_opy_.bstack1lll11lll1l_opy_())
        self.bstack1ll1lll1l1l_opy_ = defaultdict(lambda: timedelta(microseconds=0))
        self.bstack111111ll11_opy_ = bstack111111l11l_opy_()
        self.bstack1lll1l11lll_opy_ = None
        self.bstack1lll11ll11l_opy_ = None
        self.bstack1ll1lllllll_opy_ = None
        self.accessibility = None
        self.ai = None
        self.percy = None
        self.bstack1lll111llll_opy_ = []
    def bstack111l1llll_opy_(self):
        return os.environ.get(bstack111l1ll11_opy_).lower().__eq__(bstack11l1_opy_ (u"ࠥࡸࡷࡻࡥࠣႱ"))
    def is_enabled(self, config):
        if bstack11l1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨႲ") in config and str(config[bstack11l1_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩႳ")]).lower() != bstack11l1_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬႴ"):
            return False
        bstack1lll1l1l111_opy_ = [bstack11l1_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺࠢႵ"), bstack11l1_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠧႶ")]
        bstack1llll111ll1_opy_ = config.get(bstack11l1_opy_ (u"ࠤࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠧႷ")) in bstack1lll1l1l111_opy_ or os.environ.get(bstack11l1_opy_ (u"ࠪࡊࡗࡇࡍࡆ࡙ࡒࡖࡐࡥࡕࡔࡇࡇࠫႸ")) in bstack1lll1l1l111_opy_
        os.environ[bstack11l1_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆࡎࡔࡁࡓ࡛ࡢࡍࡘࡥࡒࡖࡐࡑࡍࡓࡍࠢႹ")] = str(bstack1llll111ll1_opy_) # bstack1lll11l1111_opy_ bstack1ll1lll11l1_opy_ VAR to bstack1ll1ll11l1l_opy_ is binary running
        return bstack1llll111ll1_opy_
    def bstack1ll1ll1l1l_opy_(self):
        for event in bstack1lll1llll11_opy_:
            bstack1llll111l1_opy_.register(
                event, lambda event_name, *args, **kwargs: bstack1llll111l1_opy_.logger.debug(bstack11l1_opy_ (u"ࠧࢁࡥࡷࡧࡱࡸࡤࡴࡡ࡮ࡧࢀࠤࡂࡄࠠࡼࡣࡵ࡫ࡸࢃࠠࠣႺ") + str(kwargs) + bstack11l1_opy_ (u"ࠨࠢႻ"))
            )
        bstack1llll111l1_opy_.register(bstack11l1lllll1_opy_.bstack11l1111l1l_opy_, self.__1lll1lll11l_opy_)
        bstack1llll111l1_opy_.register(bstack11l1lllll1_opy_.CONNECT, self.__1lll1lll1l1_opy_)
        bstack1llll111l1_opy_.register(bstack11l1lllll1_opy_.bstack111l1111_opy_, self.__1ll1ll1l11l_opy_)
        bstack1llll111l1_opy_.register(bstack11l1lllll1_opy_.bstack1ll1llllll_opy_, self.__1llll11l1l1_opy_)
    def bstack1ll1111lll_opy_(self):
        return not self.bstack1ll1lll11ll_opy_ and os.environ.get(bstack1lll1llll1l_opy_, bstack11l1_opy_ (u"ࠢࠣႼ")) != bstack11l1_opy_ (u"ࠣࠤႽ")
    def is_running(self):
        if self.bstack1ll1lll11ll_opy_:
            return self.bstack1lll11l111l_opy_
        else:
            return bool(self.bstack1llll1l11ll_opy_)
    def bstack1ll1l1lllll_opy_(self, module):
        return any(isinstance(m, module) for m in self.bstack1lll111llll_opy_) and cli.is_running()
    def __1lll11ll1ll_opy_(self, bstack1lll111l1l1_opy_=10):
        if self.bstack1ll1llllll1_opy_:
            return
        bstack11ll111l1l_opy_ = datetime.now()
        cli_listen_addr = os.environ.get(bstack1lll1l11ll1_opy_, self.cli_listen_addr)
        self.logger.debug(bstack11l1_opy_ (u"ࠤ࡞ࠦႾ") + str(id(self)) + bstack11l1_opy_ (u"ࠥࡡࠥࡩ࡯࡯ࡰࡨࡧࡹ࡯࡮ࡨࠤႿ"))
        channel = grpc.insecure_channel(cli_listen_addr, options=[(bstack11l1_opy_ (u"ࠦ࡬ࡸࡰࡤ࠰ࡨࡲࡦࡨ࡬ࡦࡡ࡫ࡸࡹࡶ࡟ࡱࡴࡲࡼࡾࠨჀ"), 0), (bstack11l1_opy_ (u"ࠧ࡭ࡲࡱࡥ࠱ࡩࡳࡧࡢ࡭ࡧࡢ࡬ࡹࡺࡰࡴࡡࡳࡶࡴࡾࡹࠣჁ"), 0)])
        grpc.channel_ready_future(channel).result(timeout=bstack1lll111l1l1_opy_)
        self.bstack1llll1l11ll_opy_ = channel
        self.bstack1ll1llllll1_opy_ = sdk_pb2_grpc.SDKStub(self.bstack1llll1l11ll_opy_)
        self.bstack1ll11lll11_opy_(bstack11l1_opy_ (u"ࠨࡧࡳࡲࡦ࠾ࡨࡵ࡮࡯ࡧࡦࡸࠧჂ"), datetime.now() - bstack11ll111l1l_opy_)
        self.cli_listen_addr = cli_listen_addr
        os.environ[bstack1lll1l11ll1_opy_] = self.cli_listen_addr
        self.logger.debug(bstack11l1_opy_ (u"ࠢ࡜ࡽ࡬ࡨ࠭ࡹࡥ࡭ࡨࠬࢁࡢࠦࡣࡰࡰࡱࡩࡨࡺࡥࡥ࠼ࠣ࡭ࡸࡥࡣࡩ࡫࡯ࡨࡤࡶࡲࡰࡥࡨࡷࡸࡃࠢჃ") + str(self.bstack1ll1111lll_opy_()) + bstack11l1_opy_ (u"ࠣࠤჄ"))
    def __1ll1ll1l11l_opy_(self, event_name):
        if self.bstack1ll1111lll_opy_():
            self.logger.debug(bstack11l1_opy_ (u"ࠤࡦ࡬࡮ࡲࡤ࠮ࡲࡵࡳࡨ࡫ࡳࡴ࠼ࠣࡷࡹࡵࡰࡱ࡫ࡱ࡫ࠥࡉࡌࡊࠤჅ"))
        self.__1ll1ll111ll_opy_()
    def __1llll11l1l1_opy_(self, event_name, bstack1llll1l111l_opy_ = None, exit_code=1):
        if exit_code == 1:
            self.logger.error(bstack11l1_opy_ (u"ࠥࡗࡴࡳࡥࡵࡪ࡬ࡲ࡬ࠦࡷࡦࡰࡷࠤࡼࡸ࡯࡯ࡩࠥ჆"))
        bstack1lll1l11l11_opy_ = Path(bstack1lll1lll111_opy_ (u"ࠦࢀࡹࡥ࡭ࡨ࠱ࡧࡱ࡯࡟ࡥ࡫ࡵࢁ࠴ࡻ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡆࡴࡵࡳࡷࡹ࠮࡫ࡵࡲࡲࠧჇ"))
        if self.bstack1ll1l1ll11l_opy_ and bstack1lll1l11l11_opy_.exists():
            with open(bstack1lll1l11l11_opy_, bstack11l1_opy_ (u"ࠬࡸࠧ჈"), encoding=bstack11l1_opy_ (u"࠭ࡵࡵࡨ࠰࠼ࠬ჉")) as fp:
                data = json.load(fp)
                try:
                    bstack1l11l1l1l1_opy_(bstack11l1_opy_ (u"ࠧࡑࡑࡖࡘࠬ჊"), bstack1111l1l11_opy_(bstack1l11l111ll_opy_), data, {
                        bstack11l1_opy_ (u"ࠨࡣࡸࡸ࡭࠭჋"): (self.config[bstack11l1_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫ჌")], self.config[bstack11l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭Ⴭ")])
                    })
                except Exception as e:
                    logger.debug(bstack11l11lll1l_opy_.format(str(e)))
            bstack1lll1l11l11_opy_.unlink()
        sys.exit(exit_code)
    @measure(event_name=EVENTS.bstack1llll1ll11l_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def __1lll1lll11l_opy_(self, event_name: str, data):
        from bstack_utils.bstack1ll111lll1_opy_ import bstack1ll1ll11111_opy_
        self.bstack1ll1ll1l111_opy_, self.bstack1ll1l1ll11l_opy_ = bstack1ll1ll11ll1_opy_(data.bs_config)
        os.environ[bstack11l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢ࡛ࡗࡏࡔࡂࡄࡏࡉࡤࡊࡉࡓࠩ჎")] = self.bstack1ll1l1ll11l_opy_
        if not self.bstack1ll1ll1l111_opy_ or not self.bstack1ll1l1ll11l_opy_:
            raise ValueError(bstack11l1_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡨ࡬ࡲࡩࠦࡴࡩࡧࠣࡗࡉࡑࠠࡄࡎࡌࠤࡧ࡯࡮ࡢࡴࡼࠦ჏"))
        if self.bstack1ll1111lll_opy_():
            self.__1lll1lll1l1_opy_(event_name, bstack11l11ll1ll_opy_())
            return
        try:
            bstack1ll1ll11111_opy_.end(EVENTS.bstack11l11lllll_opy_.value, EVENTS.bstack11l11lllll_opy_.value + bstack11l1_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨა"), EVENTS.bstack11l11lllll_opy_.value + bstack11l1_opy_ (u"ࠢ࠻ࡧࡱࡨࠧბ"), status=True, failure=None, test_name=None)
            logger.debug(bstack11l1_opy_ (u"ࠣࡅࡲࡱࡵࡲࡥࡵࡧࠣࡗࡉࡑࠠࡔࡧࡷࡹࡵ࠴ࠢგ"))
        except Exception as e:
            logger.debug(bstack11l1_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡽࡨࡪ࡮ࡨࠤࡲࡧࡲ࡬࡫ࡱ࡫ࠥࡱࡥࡺࠢࡰࡩࡹࡸࡩࡤࡵࠣࡿࢂࠨდ").format(e))
        start = datetime.now()
        is_started = self.__1ll1ll1lll1_opy_()
        self.bstack1ll11lll11_opy_(bstack11l1_opy_ (u"ࠥࡷࡵࡧࡷ࡯ࡡࡷ࡭ࡲ࡫ࠢე"), datetime.now() - start)
        if is_started:
            start = datetime.now()
            self.__1lll11ll1ll_opy_()
            self.bstack1ll11lll11_opy_(bstack11l1_opy_ (u"ࠦࡨࡵ࡮࡯ࡧࡦࡸࡤࡺࡩ࡮ࡧࠥვ"), datetime.now() - start)
            start = datetime.now()
            self.__1ll1lll1lll_opy_(data)
            self.bstack1ll11lll11_opy_(bstack11l1_opy_ (u"ࠧࡹࡴࡢࡴࡷࡣࡸ࡫ࡳࡴ࡫ࡲࡲࡤࡺࡩ࡮ࡧࠥზ"), datetime.now() - start)
    @measure(event_name=EVENTS.bstack1ll1llll1ll_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def __1lll1lll1l1_opy_(self, event_name: str, data: bstack11l11ll1ll_opy_):
        if not self.bstack1ll1111lll_opy_():
            self.logger.debug(bstack11l1_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡦࡳࡳࡴࡥࡤࡶ࠽ࠤࡳࡵࡴࠡࡣࠣࡧ࡭࡯࡬ࡥ࠯ࡳࡶࡴࡩࡥࡴࡵࠥთ"))
            return
        bin_session_id = os.environ.get(bstack1lll1llll1l_opy_)
        start = datetime.now()
        self.__1lll11ll1ll_opy_()
        self.bstack1ll11lll11_opy_(bstack11l1_opy_ (u"ࠢࡤࡱࡱࡲࡪࡩࡴࡠࡶ࡬ࡱࡪࠨი"), datetime.now() - start)
        self.cli_bin_session_id = bin_session_id
        self.logger.debug(bstack11l1_opy_ (u"ࠣ࡝ࡾ࡭ࡩ࠮ࡳࡦ࡮ࡩ࠭ࢂࡣࠠࡤࡪ࡬ࡰࡩ࠳ࡰࡳࡱࡦࡩࡸࡹ࠺ࠡࡥࡲࡲࡳ࡫ࡣࡵࡧࡧࠤࡹࡵࠠࡦࡺ࡬ࡷࡹ࡯࡮ࡨࠢࡆࡐࡎࠦࠢკ") + str(bin_session_id) + bstack11l1_opy_ (u"ࠤࠥლ"))
        start = datetime.now()
        self.__1ll1llll1l1_opy_()
        self.bstack1ll11lll11_opy_(bstack11l1_opy_ (u"ࠥࡷࡹࡧࡲࡵࡡࡶࡩࡸࡹࡩࡰࡰࡢࡸ࡮ࡳࡥࠣმ"), datetime.now() - start)
    def __1ll1ll11lll_opy_(self):
        if not self.bstack1ll1llllll1_opy_ or not self.cli_bin_session_id:
            self.logger.debug(bstack11l1_opy_ (u"ࠦࡨࡧ࡮࡯ࡱࡷࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷ࡫ࠠ࡮ࡱࡧࡹࡱ࡫ࡳࠣნ"))
            return
        bstack1lll1l11111_opy_ = {
            bstack11l1_opy_ (u"ࠧࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠤო"): (bstack1ll1ll111l1_opy_, bstack1llll111lll_opy_, bstack1lll1llllll_opy_),
            bstack11l1_opy_ (u"ࠨࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࠣპ"): (bstack1lll1111lll_opy_, bstack1lll1l1l1l1_opy_, bstack1llll1l11l1_opy_),
        }
        if not self.bstack1lll1l11lll_opy_ and self.session_framework in bstack1lll1l11111_opy_:
            bstack1llll11l1ll_opy_, bstack1ll1l1llll1_opy_, bstack1lll11ll111_opy_ = bstack1lll1l11111_opy_[self.session_framework]
            bstack1llll11llll_opy_ = bstack1ll1l1llll1_opy_()
            self.bstack1lll11ll11l_opy_ = bstack1llll11llll_opy_
            self.bstack1lll1l11lll_opy_ = bstack1lll11ll111_opy_
            self.bstack1lll111llll_opy_.append(bstack1llll11llll_opy_)
            self.bstack1lll111llll_opy_.append(bstack1llll11l1ll_opy_(self.bstack1lll11ll11l_opy_))
        if not self.bstack1ll1lllllll_opy_ and self.config_observability and self.config_observability.success: # bstack1lll111l111_opy_
            self.bstack1ll1lllllll_opy_ = bstack1ll1llll11l_opy_(self.bstack1lll1l11lll_opy_, self.bstack1lll11ll11l_opy_) # bstack1lll1l111l1_opy_
            self.bstack1lll111llll_opy_.append(self.bstack1ll1lllllll_opy_)
        if not self.accessibility and self.config_accessibility and self.config_accessibility.success:
            self.accessibility = bstack1lll11111ll_opy_(self.bstack1lll1l11lll_opy_, self.bstack1lll11ll11l_opy_)
            self.bstack1lll111llll_opy_.append(self.accessibility)
        if not self.ai and isinstance(self.config, dict) and self.config.get(bstack11l1_opy_ (u"ࠢࡴࡧ࡯ࡪࡍ࡫ࡡ࡭ࠤჟ"), False) == True:
            self.ai = bstack1lll11lllll_opy_()
            self.bstack1lll111llll_opy_.append(self.ai)
        if not self.percy and self.bstack1lll111l11l_opy_ and self.bstack1lll111l11l_opy_.success:
            self.percy = bstack1lll1l1llll_opy_(self.bstack1lll111l11l_opy_)
            self.bstack1lll111llll_opy_.append(self.percy)
        for mod in self.bstack1lll111llll_opy_:
            if not mod.bstack1llll1l1ll1_opy_():
                mod.configure(self.bstack1ll1llllll1_opy_, self.config, self.cli_bin_session_id, self.bstack111111ll11_opy_)
    def __1ll1lll111l_opy_(self):
        for mod in self.bstack1lll111llll_opy_:
            if mod.bstack1llll1l1ll1_opy_():
                mod.configure(self.bstack1ll1llllll1_opy_, None, None, None)
    @measure(event_name=EVENTS.bstack1lll11lll11_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def __1ll1lll1lll_opy_(self, data):
        if not self.cli_bin_session_id or self.bstack1lll111ll1l_opy_:
            return
        self.__1ll1lll1ll1_opy_(data)
        bstack11ll111l1l_opy_ = datetime.now()
        req = structs.StartBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        req.path_project = os.getcwd()
        req.language = bstack11l1_opy_ (u"ࠣࡲࡼࡸ࡭ࡵ࡮ࠣრ")
        req.sdk_language = bstack11l1_opy_ (u"ࠤࡳࡽࡹ࡮࡯࡯ࠤს")
        req.path_config = data.path_config
        req.sdk_version = data.sdk_version
        req.test_framework = data.test_framework
        req.frameworks.extend(data.frameworks)
        req.framework_versions.update(data.framework_versions)
        req.env_vars.update({key: value for key, value in os.environ.items() if bool(bstack1lll1ll1111_opy_.search(key))})
        req.cli_args.extend(sys.argv)
        try:
            self.logger.debug(bstack11l1_opy_ (u"ࠥ࡟ࠧტ") + str(id(self)) + bstack11l1_opy_ (u"ࠦࡢࠦ࡭ࡢ࡫ࡱ࠱ࡵࡸ࡯ࡤࡧࡶࡷ࠿ࠦࡳࡵࡣࡵࡸࡤࡨࡩ࡯ࡡࡶࡩࡸࡹࡩࡰࡰࠥუ"))
            r = self.bstack1ll1llllll1_opy_.StartBinSession(req)
            self.bstack1ll11lll11_opy_(bstack11l1_opy_ (u"ࠧ࡭ࡲࡱࡥ࠽ࡷࡹࡧࡲࡵࡡࡥ࡭ࡳࡥࡳࡦࡵࡶ࡭ࡴࡴࠢფ"), datetime.now() - bstack11ll111l1l_opy_)
            os.environ[bstack1lll1llll1l_opy_] = r.bin_session_id
            self.__1lll1ll1l11_opy_(r)
            self.__1ll1ll11lll_opy_()
            self.bstack111111ll11_opy_.start()
            self.bstack1lll111ll1l_opy_ = True
            self.logger.debug(bstack11l1_opy_ (u"ࠨ࡛ࠣქ") + str(id(self)) + bstack11l1_opy_ (u"ࠢ࡞ࠢࡰࡥ࡮ࡴ࠭ࡱࡴࡲࡧࡪࡹࡳ࠻ࠢࡦࡳࡳࡴࡥࡤࡶࡨࡨࠧღ"))
        except grpc.bstack1ll1lll1111_opy_ as bstack1llll1l1l11_opy_:
            self.logger.error(bstack11l1_opy_ (u"ࠣ࡝ࡾ࡭ࡩ࠮ࡳࡦ࡮ࡩ࠭ࢂࡣࠠࡵ࡫ࡰࡩࡴ࡫ࡵࡵ࠯ࡨࡶࡷࡵࡲ࠻ࠢࠥყ") + str(bstack1llll1l1l11_opy_) + bstack11l1_opy_ (u"ࠤࠥშ"))
            traceback.print_exc()
            raise bstack1llll1l1l11_opy_
        except grpc.RpcError as e:
            self.logger.error(bstack11l1_opy_ (u"ࠥ࡟ࢀ࡯ࡤࠩࡵࡨࡰ࡫࠯ࡽ࡞ࠢࡵࡴࡨ࠳ࡥࡳࡴࡲࡶ࠿ࠦࠢჩ") + str(e) + bstack11l1_opy_ (u"ࠦࠧც"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1ll1ll1l1l1_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def __1ll1llll1l1_opy_(self):
        if not self.bstack1ll1111lll_opy_() or not self.cli_bin_session_id or self.bstack1lll1111l11_opy_:
            return
        bstack11ll111l1l_opy_ = datetime.now()
        req = structs.ConnectBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        req.platform_index = int(os.environ.get(bstack11l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠬძ"), bstack11l1_opy_ (u"࠭࠰ࠨწ")))
        try:
            self.logger.debug(bstack11l1_opy_ (u"ࠢ࡜ࠤჭ") + str(id(self)) + bstack11l1_opy_ (u"ࠣ࡟ࠣࡧ࡭࡯࡬ࡥ࠯ࡳࡶࡴࡩࡥࡴࡵ࠽ࠤࡨࡵ࡮࡯ࡧࡦࡸࡤࡨࡩ࡯ࡡࡶࡩࡸࡹࡩࡰࡰࠥხ"))
            r = self.bstack1ll1llllll1_opy_.ConnectBinSession(req)
            self.bstack1ll11lll11_opy_(bstack11l1_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡤࡱࡱࡲࡪࡩࡴࡠࡤ࡬ࡲࡤࡹࡥࡴࡵ࡬ࡳࡳࠨჯ"), datetime.now() - bstack11ll111l1l_opy_)
            self.__1lll1ll1l11_opy_(r)
            self.__1ll1ll11lll_opy_()
            self.bstack111111ll11_opy_.start()
            self.bstack1lll1111l11_opy_ = True
            self.logger.debug(bstack11l1_opy_ (u"ࠥ࡟ࠧჰ") + str(id(self)) + bstack11l1_opy_ (u"ࠦࡢࠦࡣࡩ࡫࡯ࡨ࠲ࡶࡲࡰࡥࡨࡷࡸࡀࠠࡤࡱࡱࡲࡪࡩࡴࡦࡦࠥჱ"))
        except grpc.bstack1ll1lll1111_opy_ as bstack1llll1l1l11_opy_:
            self.logger.error(bstack11l1_opy_ (u"ࠧࡡࡻࡪࡦࠫࡷࡪࡲࡦࠪࡿࡠࠤࡹ࡯࡭ࡦࡱࡨࡹࡹ࠳ࡥࡳࡴࡲࡶ࠿ࠦࠢჲ") + str(bstack1llll1l1l11_opy_) + bstack11l1_opy_ (u"ࠨࠢჳ"))
            traceback.print_exc()
            raise bstack1llll1l1l11_opy_
        except grpc.RpcError as e:
            self.logger.error(bstack11l1_opy_ (u"ࠢ࡜ࡽ࡬ࡨ࠭ࡹࡥ࡭ࡨࠬࢁࡢࠦࡲࡱࡥ࠰ࡩࡷࡸ࡯ࡳ࠼ࠣࠦჴ") + str(e) + bstack11l1_opy_ (u"ࠣࠤჵ"))
            traceback.print_exc()
            raise e
    def __1lll1ll1l11_opy_(self, r):
        self.bstack1llll1ll111_opy_(r)
        if not r.bin_session_id or not r.config or not isinstance(r.config, str):
            raise ValueError(bstack11l1_opy_ (u"ࠤࡸࡲࡪࡾࡰࡦࡥࡷࡩࡩࠦࡳࡦࡴࡹࡩࡷࠦࡲࡦࡵࡳࡳࡳࡹࡥࠣჶ") + str(r))
        self.config = json.loads(r.config)
        if not self.config:
            raise ValueError(bstack11l1_opy_ (u"ࠥࡩࡲࡶࡴࡺࠢࡦࡳࡳ࡬ࡩࡨࠢࡩࡳࡺࡴࡤࠣჷ"))
        self.session_framework = r.session_framework
        self.config_testhub = r.testhub
        self.config_observability = r.observability
        self.config_accessibility = r.accessibility
        bstack11l1_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡒࡨࡶࡨࡿࠠࡪࡵࠣࡷࡪࡴࡴࠡࡱࡱࡰࡾࠦࡡࡴࠢࡳࡥࡷࡺࠠࡰࡨࠣࡸ࡭࡫ࠠࠣࡅࡲࡲࡳ࡫ࡣࡵࡄ࡬ࡲࡘ࡫ࡳࡴ࡫ࡲࡲ࠱ࠨࠠࡢࡰࡧࠤࡹ࡮ࡩࡴࠢࡩࡹࡳࡩࡴࡪࡱࡱࠤ࡮ࡹࠠࡢ࡮ࡶࡳࠥࡻࡳࡦࡦࠣࡦࡾࠦࡓࡵࡣࡵࡸࡇ࡯࡮ࡔࡧࡶࡷ࡮ࡵ࡮࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡘ࡭࡫ࡲࡦࡨࡲࡶࡪ࠲ࠠࡏࡱࡱࡩࠥ࡮ࡡ࡯ࡦ࡯࡭ࡳ࡭ࠠࡪࡵࠣ࡭ࡲࡶ࡬ࡦ࡯ࡨࡲࡹ࡫ࡤ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨჸ")
        self.bstack1lll111l11l_opy_ = getattr(r, bstack11l1_opy_ (u"ࠬࡶࡥࡳࡥࡼࠫჹ"), None)
        self.cli_bin_session_id = r.bin_session_id
        os.environ[bstack11l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪჺ")] = self.config_testhub.jwt
        os.environ[bstack11l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬ჻")] = self.config_testhub.build_hashed_id
    def bstack1ll1ll1ll1l_opy_(event_name: EVENTS, stage: STAGE):
        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                if self.bstack1lll11l111l_opy_:
                    return func(self, *args, **kwargs)
                @measure(event_name=event_name, stage=stage)
                def bstack1ll1lllll1l_opy_(*a, **kw):
                    return func(self, *a, **kw)
                return bstack1ll1lllll1l_opy_(*args, **kwargs)
            return wrapper
        return decorator
    @bstack1ll1ll1ll1l_opy_(event_name=EVENTS.bstack1llll111l11_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def __1ll1ll1lll1_opy_(self, bstack1lll111l1l1_opy_=10):
        if self.bstack1lll11l111l_opy_:
            self.logger.debug(bstack11l1_opy_ (u"ࠣࡵࡷࡥࡷࡺ࠺ࠡࡣ࡯ࡶࡪࡧࡤࡺࠢࡵࡹࡳࡴࡩ࡯ࡩࠥჼ"))
            return True
        self.logger.debug(bstack11l1_opy_ (u"ࠤࡶࡸࡦࡸࡴࠣჽ"))
        if os.getenv(bstack11l1_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡆࡐࡎࡥࡅࡏࡘࠥჾ")) == bstack1lll1lll1ll_opy_:
            self.cli_bin_session_id = bstack1lll1lll1ll_opy_
            self.cli_listen_addr = bstack11l1_opy_ (u"ࠦࡺࡴࡩࡹ࠼࠲ࡸࡲࡶ࠯ࡴࡦ࡮࠱ࡵࡲࡡࡵࡨࡲࡶࡲ࠳ࠥࡴ࠰ࡶࡳࡨࡱࠢჿ") % (self.cli_bin_session_id)
            self.bstack1lll11l111l_opy_ = True
            return True
        self.process = subprocess.Popen(
            [self.bstack1ll1ll1l111_opy_, bstack11l1_opy_ (u"ࠧࡹࡤ࡬ࠤᄀ")],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(os.environ),
            text=True,
            universal_newlines=True, # bstack1lll1ll111l_opy_ compat for text=True in bstack1lll111lll1_opy_ python
            encoding=bstack11l1_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧᄁ"),
            bufsize=1,
            close_fds=True,
        )
        bstack1lll111ll11_opy_ = threading.Thread(target=self.__1ll1l1lll11_opy_, args=(bstack1lll111l1l1_opy_,))
        bstack1lll111ll11_opy_.start()
        bstack1lll111ll11_opy_.join()
        if self.process.returncode is not None:
            self.logger.debug(bstack11l1_opy_ (u"ࠢ࡜ࡽ࡬ࡨ࠭ࡹࡥ࡭ࡨࠬࢁࡢࠦࡳࡱࡣࡺࡲ࠿ࠦࡲࡦࡶࡸࡶࡳࡩ࡯ࡥࡧࡀࡿࡸ࡫࡬ࡧ࠰ࡳࡶࡴࡩࡥࡴࡵ࠱ࡶࡪࡺࡵࡳࡰࡦࡳࡩ࡫ࡽࠡࡱࡸࡸࡂࢁࡳࡦ࡮ࡩ࠲ࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡹࡴࡥࡱࡸࡸ࠳ࡸࡥࡢࡦࠫ࠭ࢂࠦࡥࡳࡴࡀࠦᄂ") + str(self.process.stderr.read()) + bstack11l1_opy_ (u"ࠣࠤᄃ"))
        if not self.bstack1lll11l111l_opy_:
            self.logger.debug(bstack11l1_opy_ (u"ࠤ࡞ࠦᄄ") + str(id(self)) + bstack11l1_opy_ (u"ࠥࡡࠥࡩ࡬ࡦࡣࡱࡹࡵࠨᄅ"))
            self.__1ll1ll111ll_opy_()
        self.logger.debug(bstack11l1_opy_ (u"ࠦࡠࢁࡩࡥࠪࡶࡩࡱ࡬ࠩࡾ࡟ࠣࡴࡷࡵࡣࡦࡵࡶࡣࡷ࡫ࡡࡥࡻ࠽ࠤࠧᄆ") + str(self.bstack1lll11l111l_opy_) + bstack11l1_opy_ (u"ࠧࠨᄇ"))
        return self.bstack1lll11l111l_opy_
    def __1ll1l1lll11_opy_(self, bstack1ll1l1lll1l_opy_=10):
        bstack1llll1l1lll_opy_ = time.time()
        while self.process and time.time() - bstack1llll1l1lll_opy_ < bstack1ll1l1lll1l_opy_:
            try:
                line = self.process.stdout.readline()
                if bstack11l1_opy_ (u"ࠨࡩࡥ࠿ࠥᄈ") in line:
                    self.cli_bin_session_id = line.split(bstack11l1_opy_ (u"ࠢࡪࡦࡀࠦᄉ"))[-1:][0].strip()
                    self.logger.debug(bstack11l1_opy_ (u"ࠣࡥ࡯࡭ࡤࡨࡩ࡯ࡡࡶࡩࡸࡹࡩࡰࡰࡢ࡭ࡩࡀࠢᄊ") + str(self.cli_bin_session_id) + bstack11l1_opy_ (u"ࠤࠥᄋ"))
                    continue
                if bstack11l1_opy_ (u"ࠥࡰ࡮ࡹࡴࡦࡰࡀࠦᄌ") in line:
                    self.cli_listen_addr = line.split(bstack11l1_opy_ (u"ࠦࡱ࡯ࡳࡵࡧࡱࡁࠧᄍ"))[-1:][0].strip()
                    self.logger.debug(bstack11l1_opy_ (u"ࠧࡩ࡬ࡪࡡ࡯࡭ࡸࡺࡥ࡯ࡡࡤࡨࡩࡸ࠺ࠣᄎ") + str(self.cli_listen_addr) + bstack11l1_opy_ (u"ࠨࠢᄏ"))
                    continue
                if bstack11l1_opy_ (u"ࠢࡱࡱࡵࡸࡂࠨᄐ") in line:
                    port = line.split(bstack11l1_opy_ (u"ࠣࡲࡲࡶࡹࡃࠢᄑ"))[-1:][0].strip()
                    self.logger.debug(bstack11l1_opy_ (u"ࠤࡳࡳࡷࡺ࠺ࠣᄒ") + str(port) + bstack11l1_opy_ (u"ࠥࠦᄓ"))
                    continue
                if line.strip() == bstack1lll11l1ll1_opy_ and self.cli_bin_session_id and self.cli_listen_addr:
                    if os.getenv(bstack11l1_opy_ (u"ࠦࡘࡊࡋࡠࡅࡏࡍࡤࡌࡌࡂࡉࡢࡍࡔࡥࡓࡕࡔࡈࡅࡒࠨᄔ"), bstack11l1_opy_ (u"ࠧ࠷ࠢᄕ")) == bstack11l1_opy_ (u"ࠨ࠱ࠣᄖ"):
                        if not self.process.stdout.closed:
                            self.process.stdout.close()
                        if not self.process.stderr.closed:
                            self.process.stderr.close()
                    self.bstack1lll11l111l_opy_ = True
                    return True
            except Exception as e:
                self.logger.debug(bstack11l1_opy_ (u"ࠢࡦࡴࡵࡳࡷࡀࠠࠣᄗ") + str(e) + bstack11l1_opy_ (u"ࠣࠤᄘ"))
        return False
    @measure(event_name=EVENTS.bstack1lll11ll1l1_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def __1ll1ll111ll_opy_(self):
        if self.bstack1llll1l11ll_opy_:
            self.bstack111111ll11_opy_.stop()
            start = datetime.now()
            if self.bstack1lll1111111_opy_():
                self.cli_bin_session_id = None
                if self.bstack1lll1111l11_opy_:
                    self.bstack1ll11lll11_opy_(bstack11l1_opy_ (u"ࠤࡶࡸࡴࡶ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠࡶ࡬ࡱࡪࠨᄙ"), datetime.now() - start)
                else:
                    self.bstack1ll11lll11_opy_(bstack11l1_opy_ (u"ࠥࡷࡹࡵࡰࡠࡵࡨࡷࡸ࡯࡯࡯ࡡࡷ࡭ࡲ࡫ࠢᄚ"), datetime.now() - start)
            self.__1ll1lll111l_opy_()
            start = datetime.now()
            self.bstack1llll1l11ll_opy_.close()
            self.bstack1ll11lll11_opy_(bstack11l1_opy_ (u"ࠦࡩ࡯ࡳࡤࡱࡱࡲࡪࡩࡴࡠࡶ࡬ࡱࡪࠨᄛ"), datetime.now() - start)
            self.bstack1llll1l11ll_opy_ = None
        if self.process:
            self.logger.debug(bstack11l1_opy_ (u"ࠧࡹࡴࡰࡲࠥᄜ"))
            start = datetime.now()
            self.process.terminate()
            self.bstack1ll11lll11_opy_(bstack11l1_opy_ (u"ࠨ࡫ࡪ࡮࡯ࡣࡹ࡯࡭ࡦࠤᄝ"), datetime.now() - start)
            self.process = None
            if self.bstack1ll1lll11ll_opy_ and self.config_observability and self.config_testhub and self.config_testhub.testhub_events:
                self.bstack1lll1ll11l_opy_()
                self.logger.info(
                    bstack11l1_opy_ (u"ࠢࡗ࡫ࡶ࡭ࡹࠦࡨࡵࡶࡳࡷ࠿࠵࠯ࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯࠲ࡦࡺ࡯࡬ࡥࡵ࠲ࡿࢂࠦࡴࡰࠢࡹ࡭ࡪࡽࠠࡣࡷ࡬ࡰࡩࠦࡲࡦࡲࡲࡶࡹ࠲ࠠࡪࡰࡶ࡭࡬࡮ࡴࡴ࠮ࠣࡥࡳࡪࠠ࡮ࡣࡱࡽࠥࡳ࡯ࡳࡧࠣࡨࡪࡨࡵࡨࡩ࡬ࡲ࡬ࠦࡩ࡯ࡨࡲࡶࡲࡧࡴࡪࡱࡱࠤࡦࡲ࡬ࠡࡣࡷࠤࡴࡴࡥࠡࡲ࡯ࡥࡨ࡫ࠡ࡝ࡰࠥᄞ").format(
                        self.config_testhub.build_hashed_id
                    )
                )
                os.environ[bstack11l1_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡈࡕࡊࡎࡇࡣࡍࡇࡓࡉࡇࡇࡣࡎࡊࠧᄟ")] = self.config_testhub.build_hashed_id
        self.bstack1lll11l111l_opy_ = False
    def __1ll1lll1ll1_opy_(self, data):
        try:
            import selenium
            data.framework_versions[bstack11l1_opy_ (u"ࠤࡶࡩࡱ࡫࡮ࡪࡷࡰࠦᄠ")] = selenium.__version__
            data.frameworks.append(bstack11l1_opy_ (u"ࠥࡷࡪࡲࡥ࡯࡫ࡸࡱࠧᄡ"))
        except:
            pass
        try:
            from playwright._repo_version import __version__
            data.framework_versions[bstack11l1_opy_ (u"ࠦࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣᄢ")] = __version__
            data.frameworks.append(bstack11l1_opy_ (u"ࠧࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠤᄣ"))
        except:
            pass
    def bstack1lll1l1111l_opy_(self, hub_url: str, platform_index: int, bstack1111ll1l_opy_: Any):
        if self.bstack1llllll1l1l_opy_:
            self.logger.debug(bstack11l1_opy_ (u"ࠨࡳ࡬࡫ࡳࡴࡪࡪࠠࡴࡧࡷࡹࡵࠦࡳࡦ࡮ࡨࡲ࡮ࡻ࡭࠻ࠢࡤࡰࡷ࡫ࡡࡥࡻࠣࡷࡪࡺࠠࡶࡲࠥᄤ"))
            return
        try:
            bstack11ll111l1l_opy_ = datetime.now()
            import selenium
            from selenium.webdriver.remote.webdriver import WebDriver
            from selenium.webdriver.common.service import Service
            framework = bstack11l1_opy_ (u"ࠢࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࠤᄥ")
            self.bstack1llllll1l1l_opy_ = bstack1llll1l11l1_opy_(
                cli.config.get(bstack11l1_opy_ (u"ࠣࡪࡸࡦ࡚ࡸ࡬ࠣᄦ"), hub_url),
                platform_index,
                framework_name=framework,
                framework_version=selenium.__version__,
                classes=[WebDriver],
                bstack1lll1l1ll1l_opy_={bstack11l1_opy_ (u"ࠤࡦࡶࡪࡧࡴࡦࡡࡲࡴࡹ࡯࡯࡯ࡵࡢࡪࡷࡵ࡭ࡠࡥࡤࡴࡸࠨᄧ"): bstack1111ll1l_opy_}
            )
            def bstack1lll11l1l1l_opy_(self):
                return
            if self.config.get(bstack11l1_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠧᄨ"), True):
                Service.start = bstack1lll11l1l1l_opy_
                Service.stop = bstack1lll11l1l1l_opy_
            def get_accessibility_results(driver):
                if self.accessibility and self.accessibility.is_enabled():
                    return self.accessibility.get_accessibility_results(driver, framework_name=framework)
            def get_accessibility_results_summary(driver):
                if self.accessibility and self.accessibility.is_enabled():
                    return self.accessibility.get_accessibility_results_summary(driver, framework_name=framework)
            def perform_scan(driver):
                if self.accessibility and self.accessibility.is_enabled():
                    return self.accessibility.perform_scan(driver, method=None, framework_name=framework)
            WebDriver.getAccessibilityResults = get_accessibility_results
            WebDriver.get_accessibility_results = get_accessibility_results
            WebDriver.getAccessibilityResultsSummary = get_accessibility_results_summary
            WebDriver.get_accessibility_results_summary = get_accessibility_results_summary
            WebDriver.upload_attachment = staticmethod(bstack1l1111ll11_opy_.upload_attachment)
            WebDriver.set_custom_tag = staticmethod(bstack1llll111111_opy_.set_custom_tag)
            WebDriver.performScan = perform_scan
            WebDriver.perform_scan = perform_scan
            self.bstack1ll11lll11_opy_(bstack11l1_opy_ (u"ࠦࡸ࡫ࡴࡶࡲࡢࡷࡪࡲࡥ࡯࡫ࡸࡱࠧᄩ"), datetime.now() - bstack11ll111l1l_opy_)
        except Exception as e:
            self.logger.error(bstack11l1_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡸࡺࡶࠠࡴࡧ࡯ࡩࡳ࡯ࡵ࡮࠼ࠣࠦᄪ") + str(e) + bstack11l1_opy_ (u"ࠨࠢᄫ"))
    def bstack1lll1l1l1ll_opy_(self, platform_index: int):
        try:
            from playwright.sync_api import BrowserType
            from playwright.sync_api import BrowserContext
            from playwright._impl._connection import Connection
            from playwright._repo_version import __version__
            from bstack_utils.helper import bstack11ll1l1l11_opy_
            self.bstack1llllll1l1l_opy_ = bstack1lll1llllll_opy_(
                platform_index,
                framework_name=bstack11l1_opy_ (u"ࠢࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠦᄬ"),
                framework_version=__version__,
                classes=[BrowserType, BrowserContext, Connection],
            )
        except Exception as e:
            self.logger.error(bstack11l1_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡸ࡫ࡴࡶࡲࠣࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺ࠺ࠡࠤᄭ") + str(e) + bstack11l1_opy_ (u"ࠤࠥᄮ"))
            pass
    def bstack1lll111l1ll_opy_(self):
        if self.test_framework:
            self.logger.debug(bstack11l1_opy_ (u"ࠥࡷࡰ࡯ࡰࡱࡧࡧࠤࡸ࡫ࡴࡶࡲࠣࡴࡾࡺࡥࡴࡶ࠽ࠤࡦࡲࡲࡦࡣࡧࡽࠥࡹࡥࡵࠢࡸࡴࠧᄯ"))
            return
        if bstack1l1l11l111_opy_():
            import pytest
            self.test_framework = PytestBDDFramework({ bstack11l1_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷࠦᄰ"): pytest.__version__ }, [bstack11l1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠤᄱ")], self.bstack111111ll11_opy_, self.bstack1ll1llllll1_opy_)
            return
        try:
            import pytest
            self.test_framework = bstack1ll1ll1llll_opy_({ bstack11l1_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹࠨᄲ"): pytest.__version__ }, [bstack11l1_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺࠢᄳ")], self.bstack111111ll11_opy_, self.bstack1ll1llllll1_opy_)
        except Exception as e:
            self.logger.error(bstack11l1_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡸ࡫ࡴࡶࡲࠣࡴࡾࡺࡥࡴࡶ࠽ࠤࠧᄴ") + str(e) + bstack11l1_opy_ (u"ࠤࠥᄵ"))
        self.bstack1lll111111l_opy_()
    def bstack1lll111111l_opy_(self):
        if not self.bstack111l1llll_opy_():
            return
        bstack11ll11l1l1_opy_ = None
        def bstack11l11ll1_opy_(config, startdir):
            return bstack11l1_opy_ (u"ࠥࡨࡷ࡯ࡶࡦࡴ࠽ࠤࢀ࠶ࡽࠣᄶ").format(bstack11l1_opy_ (u"ࠦࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠥᄷ"))
        def bstack1l111lllll_opy_():
            return
        def bstack1l11l11111_opy_(self, name: str, default=Notset(), skip: bool = False):
            if str(name).lower() == bstack11l1_opy_ (u"ࠬࡪࡲࡪࡸࡨࡶࠬᄸ"):
                return bstack11l1_opy_ (u"ࠨࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠧᄹ")
            else:
                return bstack11ll11l1l1_opy_(self, name, default, skip)
        try:
            from pytest_selenium import pytest_selenium
            from _pytest.config import Config
            bstack11ll11l1l1_opy_ = Config.getoption
            pytest_selenium.pytest_report_header = bstack11l11ll1_opy_
            from pytest_selenium.drivers import browserstack
            browserstack.pytest_selenium_runtest_makereport = bstack1l111lllll_opy_
            Config.getoption = bstack1l11l11111_opy_
        except Exception as e:
            self.logger.error(bstack11l1_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡴࡦࡺࡣࡩࠢࡳࡽࡹ࡫ࡳࡵࠢࡶࡩࡱ࡫࡮ࡪࡷࡰࠤ࡫ࡵࡲࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠺ࠡࠤᄺ") + str(e) + bstack11l1_opy_ (u"ࠣࠤᄻ"))
    def bstack1llll1111ll_opy_(self):
        bstack1l111llll1_opy_ = MessageToDict(cli.config_testhub, preserving_proto_field_name=True)
        if isinstance(bstack1l111llll1_opy_, dict):
            if cli.config_observability:
                bstack1l111llll1_opy_.update(
                    {bstack11l1_opy_ (u"ࠤࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠤᄼ"): MessageToDict(cli.config_observability, preserving_proto_field_name=True)}
                )
            if cli.config_accessibility:
                accessibility = MessageToDict(cli.config_accessibility, preserving_proto_field_name=True)
                if isinstance(accessibility, dict) and bstack11l1_opy_ (u"ࠥࡧࡴࡳ࡭ࡢࡰࡧࡷࡤࡺ࡯ࡠࡹࡵࡥࡵࠨᄽ") in accessibility.get(bstack11l1_opy_ (u"ࠦࡴࡶࡴࡪࡱࡱࡷࠧᄾ"), {}):
                    bstack1llll11ll11_opy_ = accessibility.get(bstack11l1_opy_ (u"ࠧࡵࡰࡵ࡫ࡲࡲࡸࠨᄿ"))
                    bstack1llll11ll11_opy_.update({ bstack11l1_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪࡳࡕࡱ࡚ࡶࡦࡶࠢᅀ"): bstack1llll11ll11_opy_.pop(bstack11l1_opy_ (u"ࠢࡤࡱࡰࡱࡦࡴࡤࡴࡡࡷࡳࡤࡽࡲࡢࡲࠥᅁ")) })
                bstack1l111llll1_opy_.update({bstack11l1_opy_ (u"ࠣࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠣᅂ"): accessibility })
        return bstack1l111llll1_opy_
    @measure(event_name=EVENTS.bstack1ll1lll1l11_opy_, stage=STAGE.bstack11lll1l1_opy_)
    def bstack1lll1111111_opy_(self, bstack1lll11l11ll_opy_: str = None, bstack1lll1ll11l1_opy_: str = None, exit_code: int = None):
        if not self.cli_bin_session_id or not self.bstack1ll1llllll1_opy_:
            return
        bstack11ll111l1l_opy_ = datetime.now()
        req = structs.StopBinSessionRequest()
        req.bin_session_id = self.cli_bin_session_id
        if exit_code:
            req.exit_code = exit_code
        if bstack1lll11l11ll_opy_:
            req.bstack1lll11l11ll_opy_ = bstack1lll11l11ll_opy_
        if bstack1lll1ll11l1_opy_:
            req.bstack1lll1ll11l1_opy_ = bstack1lll1ll11l1_opy_
        try:
            r = self.bstack1ll1llllll1_opy_.StopBinSession(req)
            SDKCLI.automate_buildlink = r.automate_buildlink
            SDKCLI.hashed_id = r.hashed_id
            self.bstack1ll11lll11_opy_(bstack11l1_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡴࡶࡲࡴࡤࡨࡩ࡯ࡡࡶࡩࡸࡹࡩࡰࡰࠥᅃ"), datetime.now() - bstack11ll111l1l_opy_)
            return r.success
        except grpc.RpcError as e:
            traceback.print_exc()
            raise e
    def bstack1ll11lll11_opy_(self, key: str, value: timedelta):
        tag = bstack11l1_opy_ (u"ࠥࡧ࡭࡯࡬ࡥ࠯ࡳࡶࡴࡩࡥࡴࡵࠥᅄ") if self.bstack1ll1111lll_opy_() else bstack11l1_opy_ (u"ࠦࡲࡧࡩ࡯࠯ࡳࡶࡴࡩࡥࡴࡵࠥᅅ")
        self.bstack1ll1lll1l1l_opy_[bstack11l1_opy_ (u"ࠧࡀࠢᅆ").join([tag + bstack11l1_opy_ (u"ࠨ࠭ࠣᅇ") + str(id(self)), key])] += value
    def bstack1lll1ll11l_opy_(self):
        if not os.getenv(bstack11l1_opy_ (u"ࠢࡅࡇࡅ࡙ࡌࡥࡐࡆࡔࡉࠦᅈ"), bstack11l1_opy_ (u"ࠣ࠲ࠥᅉ")) == bstack11l1_opy_ (u"ࠤ࠴ࠦᅊ"):
            return
        bstack1ll1lllll11_opy_ = dict()
        bstack1lllll1llll_opy_ = []
        if self.test_framework:
            bstack1lllll1llll_opy_.extend(list(self.test_framework.bstack1lllll1llll_opy_.values()))
        if self.bstack1llllll1l1l_opy_:
            bstack1lllll1llll_opy_.extend(list(self.bstack1llllll1l1l_opy_.bstack1lllll1llll_opy_.values()))
        for instance in bstack1lllll1llll_opy_:
            if not instance.platform_index in bstack1ll1lllll11_opy_:
                bstack1ll1lllll11_opy_[instance.platform_index] = defaultdict(lambda: timedelta(microseconds=0))
            report = bstack1ll1lllll11_opy_[instance.platform_index]
            for k, v in instance.bstack1ll1ll11l11_opy_().items():
                report[k] += v
                report[k.split(bstack11l1_opy_ (u"ࠥ࠾ࠧᅋ"))[0]] += v
        bstack1llll11111l_opy_ = sorted([(k, v) for k, v in self.bstack1ll1lll1l1l_opy_.items()], key=lambda o: o[1], reverse=True)
        bstack1lll1ll1ll1_opy_ = 0
        for r in bstack1llll11111l_opy_:
            bstack1lll1lllll1_opy_ = r[1].total_seconds()
            bstack1lll1ll1ll1_opy_ += bstack1lll1lllll1_opy_
            self.logger.debug(bstack11l1_opy_ (u"ࠦࡠࡶࡥࡳࡨࡠࠤࡨࡲࡩ࠻ࡽࡵ࡟࠵ࡣࡽ࠾ࠤᅌ") + str(bstack1lll1lllll1_opy_) + bstack11l1_opy_ (u"ࠧࠨᅍ"))
        self.logger.debug(bstack11l1_opy_ (u"ࠨ࠭࠮ࠤᅎ"))
        bstack1ll1ll1ll11_opy_ = []
        for platform_index, report in bstack1ll1lllll11_opy_.items():
            bstack1ll1ll1ll11_opy_.extend([(platform_index, k, v) for k, v in report.items()])
        bstack1ll1ll1ll11_opy_.sort(key=lambda o: o[2], reverse=True)
        bstack1ll1ll11_opy_ = set()
        bstack1llll1111l1_opy_ = 0
        for r in bstack1ll1ll1ll11_opy_:
            bstack1lll1lllll1_opy_ = r[2].total_seconds()
            bstack1llll1111l1_opy_ += bstack1lll1lllll1_opy_
            bstack1ll1ll11_opy_.add(r[0])
            self.logger.debug(bstack11l1_opy_ (u"ࠢ࡜ࡲࡨࡶ࡫ࡣࠠࡵࡧࡶࡸ࠿ࡶ࡬ࡢࡶࡩࡳࡷࡳ࠭ࡼࡴ࡞࠴ࡢࢃ࠺ࡼࡴ࡞࠵ࡢࢃ࠽ࠣᅏ") + str(bstack1lll1lllll1_opy_) + bstack11l1_opy_ (u"ࠣࠤᅐ"))
        if self.bstack1ll1111lll_opy_():
            self.logger.debug(bstack11l1_opy_ (u"ࠤ࠰࠱ࠧᅑ"))
            self.logger.debug(bstack11l1_opy_ (u"ࠥ࡟ࡵ࡫ࡲࡧ࡟ࠣࡧࡱ࡯࠺ࡤࡪ࡬ࡰࡩ࠳ࡰࡳࡱࡦࡩࡸࡹ࠽ࡼࡶࡲࡸࡦࡲ࡟ࡤ࡮࡬ࢁࠥࡺࡥࡴࡶ࠽ࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠳ࡻࡴࡶࡵࠬࡵࡲࡡࡵࡨࡲࡶࡲࡹࠩࡾ࠿ࠥᅒ") + str(bstack1llll1111l1_opy_) + bstack11l1_opy_ (u"ࠦࠧᅓ"))
        else:
            self.logger.debug(bstack11l1_opy_ (u"ࠧࡡࡰࡦࡴࡩࡡࠥࡩ࡬ࡪ࠼ࡰࡥ࡮ࡴ࠭ࡱࡴࡲࡧࡪࡹࡳ࠾ࠤᅔ") + str(bstack1lll1ll1ll1_opy_) + bstack11l1_opy_ (u"ࠨࠢᅕ"))
        self.logger.debug(bstack11l1_opy_ (u"ࠢ࠮࠯ࠥᅖ"))
    def test_orchestration_session(self, test_files: list, orchestration_strategy: str):
        request = structs.TestOrchestrationRequest(
            bin_session_id=self.cli_bin_session_id,
            orchestration_strategy=orchestration_strategy,
            test_files=test_files
        )
        if not self.bstack1ll1llllll1_opy_:
            self.logger.error(bstack11l1_opy_ (u"ࠣࡥ࡯࡭ࡤࡹࡥࡳࡸ࡬ࡧࡪࠦࡩࡴࠢࡱࡳࡹࠦࡩ࡯࡫ࡷ࡭ࡦࡲࡩࡻࡧࡧ࠲ࠥࡉࡡ࡯ࡰࡲࡸࠥࡶࡥࡳࡨࡲࡶࡲࠦࡴࡦࡵࡷࠤࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱ࠲ࠧᅗ"))
            return None
        response = self.bstack1ll1llllll1_opy_.TestOrchestration(request)
        self.logger.debug(bstack11l1_opy_ (u"ࠤࡷࡩࡸࡺ࠭ࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴ࠭ࡴࡧࡶࡷ࡮ࡵ࡮࠾ࡽࢀࠦᅘ").format(response))
        if response.success:
            return list(response.ordered_test_files)
        return None
    def bstack1llll1ll111_opy_(self, r):
        if r is not None and getattr(r, bstack11l1_opy_ (u"ࠪࡸࡪࡹࡴࡩࡷࡥࠫᅙ"), None) and getattr(r.testhub, bstack11l1_opy_ (u"ࠫࡪࡸࡲࡰࡴࡶࠫᅚ"), None):
            errors = json.loads(r.testhub.errors.decode(bstack11l1_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦᅛ")))
            for bstack1ll1ll1l1ll_opy_, err in errors.items():
                if err[bstack11l1_opy_ (u"࠭ࡴࡺࡲࡨࠫᅜ")] == bstack11l1_opy_ (u"ࠧࡪࡰࡩࡳࠬᅝ"):
                    self.logger.info(err[bstack11l1_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩᅞ")])
                else:
                    self.logger.error(err[bstack11l1_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪᅟ")])
    def bstack11l1l1lll_opy_(self):
        return SDKCLI.automate_buildlink, SDKCLI.hashed_id
cli = SDKCLI()