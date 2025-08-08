# ImpactHPC - Python library designed to estimate the environmental impact of jobs on data centers
# Copyright (C) 2025 Valentin Regnault <valentinregnault22@gmail.com>, Marius Garénaux Gruau <marius.garenaux-gruau@irisa.fr>, Gael Guennebaud <gael.guennebaud@inria.fr>, Didier Mallarino <didier.mallarino@osupytheas.fr>.
#
# This file is part of ImpactHPC.
# ImpactHPC is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# ImpactHPC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with ImpactHPC. If not, see <https://www.gnu.org/licenses/>.

__version__ = "0.0.1"

from impacthpc.src.core.ReplicableValue import SourcedValue
from impacthpc.src.core.formatters import TextFormatter, HTMLFormatter, JSONFormatter, UncertaintyFormat
from impacthpc.src.core.config import ureg
from impacthpc.src.cpu import PowerMeasure, CPU
from impacthpc.src.gpu import GPU
from impacthpc.src.server import Server
from impacthpc.src.ram import RAM
from impacthpc.src.job import Job
from impacthpc.src.battery import batteries_impacts
from impacthpc.src.park import Park, Cluster
from impacthpc.src.other_components import HDD, PowerSupply, Case, MotherBoard
from impacthpc.src.core.fuzzymatch import (
    find_close_cpu_model_name,
    find_close_ram_manufacturer_name,
    find_close_ssd_manufacturer_name,
    find_close_gpu_model_name,
    ExactName,
)
from impacthpc.src.core.impacts import Impacts
from impacthpc.src.core.allocation import naive_allocation, decrease_over_time_allocation

#  park_impact, server_impacts, SourcedValue, cpu_impacts, hdd_embodied_impacts, power_supply_embodied_impacts, gpu_impacts, ram_impact, ssd_impacts, decrease_over_time_allocation, case_embodied_impact, TextFormatter
__all__ = [
    "CPU",
    "Server",
    "RAM",
    "Park",
    "HDD",
    "PowerSupply",
    "Case",
    "find_close_cpu_model_name",
    "find_close_gpu_model_name",
    "find_close_ram_manufacturer_name",
    "find_close_ssd_manufacturer_name",
    "ExactName",
    "SourcedValue",
    "PowerMeasure",
    "TextFormatter",
    "HTMLFormatter",
    "JSONFormatter",
    "batteries_impacts",
    "ureg",
    "Cluster",
    "GPU",
    "Job",
    "MotherBoard",
    "Impacts",
    "naive_allocation",
    "decrease_over_time_allocation",
    "UncertaintyFormat",
]
