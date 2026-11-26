from domain.matches_api import router as matches
from domain.plies_api import router as plies
from domain.referee_flags_api import router as referee_flags
from domain.errata_api import router as errata

routers = (matches, plies, referee_flags, errata,)
