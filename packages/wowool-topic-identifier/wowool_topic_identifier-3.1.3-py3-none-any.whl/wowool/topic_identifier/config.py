from pathlib import Path
from wowool.native.core import Engine


def is_language_available(language, engine: Engine = None):
    if engine == None:
        from wowool.native.core.engine import default_engine

        engine_ = default_engine()
    else:
        engine_ = engine
    for pth in engine_.lxware:
        available_topic_identifiers = set([str(Path(fn).stem) for fn in Path(pth).glob("*.topic_model")])
        if language not in available_topic_identifiers:
            return True
    return False
