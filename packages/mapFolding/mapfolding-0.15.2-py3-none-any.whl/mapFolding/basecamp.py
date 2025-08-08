"""
Unified interface for map folding computation orchestration.

(AI generated docstring)

This module represents the culmination of the computational ecosystem, providing
the primary entry point where users interact with the complete map folding analysis
system. It orchestrates all preceding layers: the configuration foundation,
type system, core utilities, state management, and persistent storage to deliver
a seamless computational experience.

The interface handles multiple computation flows including sequential algorithms,
experimental task division strategies, and various mathematical theorem implementations.
It provides flexible parameter validation, computation method selection, task
division management, processor utilization control, and automatic result persistence.
Integration with OEIS sequences enables research validation and mathematical
verification of computed results.

Through this unified interface, researchers and practitioners can access the full
power of Lunnon's algorithm implementation while the underlying computational
complexity remains elegantly abstracted. The interface ensures that whether
solving simple 2D problems or complex multi-dimensional challenges, users receive
consistent, reliable, and efficiently computed folding pattern counts.
"""

from collections.abc import Sequence
from mapFolding import (
	getPathFilenameFoldsTotal, packageSettings, saveFoldsTotal, saveFoldsTotalFAILearly, setProcessorLimit,
	validateListDimensions)
from os import PathLike
from pathlib import PurePath
import contextlib

def countFolds(listDimensions: Sequence[int] | None = None
				, pathLikeWriteFoldsTotal: PathLike[str] | PurePath | None = None
				, computationDivisions: int | str | None = None
				# , * # TODO improve `standardizedEqualToCallableReturn` so it will work with keyword arguments
				, CPUlimit: int | float | bool | None = None  # noqa: FBT001
				, mapShape: tuple[int, ...] | None = None
				, oeisID: str | None = None
				, oeis_n: int | None = None
				, flow: str | None = None
				) -> int:
	"""
	Count the total number of possible foldings for a given map dimensions.

	(AI generated docstring)

	This function serves as the main public interface to the map folding algorithm, handling all parameter validation,
	computation state management, and result persistence in a user-friendly way.

	Parameters
	----------
	listDimensions
		List of integers representing the dimensions of the map to be folded.
	pathLikeWriteFoldsTotal: None
		Path, filename, or pathFilename to write the total fold count to. If a directory is provided, creates a file
		with a default name based on map dimensions.
	computationDivisions: None
		Whether and how to divide the computational work.
		- `None`: no division of the computation into tasks; sets task divisions to 0.
		- int: directly set the number of task divisions; cannot exceed the map's total leaves.
		- `'maximum'`: divides into `leavesTotal`-many `taskDivisions`.
		- `'cpu'`: limits the divisions to the number of available CPUs: i.e., `concurrencyLimit`.
	CPUlimit: None
		This is only relevant if there are `computationDivisions`: whether and how to limit the CPU usage.
		- `False`, `None`, or `0`: No limits on processor usage; uses all available processors. All other values will
		potentially limit processor usage.
		- `True`: Yes, limit the processor usage; limits to 1 processor.
		- Integer `>= 1`: Limits usage to the specified number of processors.
		- Decimal value (`float`) between 0 and 1: Fraction of total processors to use.
		- Decimal value (`float`) between -1 and 0: Fraction of processors to _not_ use.
		- Integer `<= -1`: Subtract the absolute value from total processors.

	Returns
	-------
	foldsTotal: Total number of distinct ways to fold a map of the given dimensions.

	Note well
	---------
	You probably do not want to divide your computation into tasks.

	If you want to compute a large `foldsTotal`, dividing the computation into tasks is usually a bad idea. Dividing the
	algorithm into tasks is inherently inefficient: efficient division into tasks means there would be no overlap in the
	work performed by each task. When dividing this algorithm, the amount of overlap is between 50% and 90% by all
	tasks: at least 50% of the work done by every task must be done by _all_ tasks. If you improve the computation time,
	it will only change by -10 to -50% depending on (at the very least) the ratio of the map dimensions and the number
	of leaves. If an undivided computation would take 10 hours on your computer, for example, the computation will still
	take at least 5 hours but you might reduce the time to 9 hours. Most of the time, however, you will increase the
	computation time. If logicalCores >= `leavesTotal`, it will probably be faster. If logicalCores <= 2 * `leavesTotal`, it
	will almost certainly be slower for all map dimensions.
	"""
	# mapShape ---------------------------------------------------------------------

	if mapShape:
		pass
	else:
		if oeisID and oeis_n:
			from mapFolding.oeis import dictionaryOEIS  # noqa: PLC0415
			with contextlib.suppress(KeyError):
				mapShape = dictionaryOEIS[oeisID]['getMapShape'](oeis_n)
		if not mapShape and listDimensions:
			mapShape = validateListDimensions(listDimensions)

	if mapShape is None:
		message = (
			f"""I received these values:
	`{listDimensions = }`,
	`{mapShape = }`,
	`{oeisID = }` and `{oeis_n = }`,
	but I was unable to select a map for which to count the folds."""
		)
		raise ValueError(message)

	# task division instructions -----------------------------------------------------

	if computationDivisions:
		concurrencyLimit: int = setProcessorLimit(CPUlimit, packageSettings.concurrencyPackage)
		from mapFolding.beDRY import getLeavesTotal, getTaskDivisions  # noqa: PLC0415
		leavesTotal: int = getLeavesTotal(mapShape)
		taskDivisions = getTaskDivisions(computationDivisions, concurrencyLimit, leavesTotal)
		del leavesTotal
	else:
		concurrencyLimit = 1
		taskDivisions = 0

	# memorialization instructions ---------------------------------------------

	if pathLikeWriteFoldsTotal is not None:
		pathFilenameFoldsTotal = getPathFilenameFoldsTotal(mapShape, pathLikeWriteFoldsTotal)
		saveFoldsTotalFAILearly(pathFilenameFoldsTotal)
	else:
		pathFilenameFoldsTotal = None

	# Flow control until I can figure out a good way ---------------------------------

	# A007822 flow control until I can figure out a good way ---------------------------------
	if oeisID == 'A007822':
		"""Temporary notes.

		The REAL motivation for integrating into basecamp is to integrate into the test modules. No, wait: to stop having to work
		around the test modules.

		I put `if oeisID == 'A007822'` in the `elif flow ==` cascade, before the `flow` checks because I want to remove A007822
		from those flow paths. It is fundamentally incompatible and it will cause `Exception` or incorrect computations.

		To use A007822, oeisID is mandatory.

		Parameters:
			listDimensions should work. mapShape should work. oeis_n should work. `pathLikeWriteFoldsTotal` should work!!! I
			didn't think about that, and I like it.

		Parallel version:
			idk. The computation division logic will try to execute. As of 2025 Aug 6 at 7 PM, I haven't tried or thought about a
			parallel version. TODO Watch out for errors.

		`flow`:
			It looks like I will need to make decisions tree just for A007822. That's probably not a big deal since all of the
			possible routes are predictable.

		"""
		match flow:
			case 'numba':
				from mapFolding.dataBaskets import MapFoldingState  # noqa: PLC0415
				mapFoldingState: MapFoldingState = MapFoldingState(mapShape)

				from mapFolding.syntheticModules.algorithmA007822Numba import doTheNeedful  # noqa: PLC0415
				mapFoldingState = doTheNeedful(mapFoldingState)

			case 'theorem2':
				from mapFolding.dataBaskets import MapFoldingState  # noqa: PLC0415
				mapFoldingState: MapFoldingState = MapFoldingState(mapShape)

				from mapFolding.syntheticModules.initializeStateA007822 import transitionOnGroupsOfFolds  # noqa: PLC0415
				mapFoldingState = transitionOnGroupsOfFolds(mapFoldingState)

				from mapFolding.syntheticModules.theorem2A007822 import count  # noqa: PLC0415
				mapFoldingState = count(mapFoldingState)

			case 'theorem2Numba':
				from mapFolding.dataBaskets import MapFoldingState  # noqa: PLC0415
				mapFoldingState: MapFoldingState = MapFoldingState(mapShape)

				from mapFolding.syntheticModules.initializeStateA007822 import transitionOnGroupsOfFolds  # noqa: PLC0415
				mapFoldingState = transitionOnGroupsOfFolds(mapFoldingState)

				from mapFolding.syntheticModules.dataPackingA007822 import sequential  # noqa: PLC0415
				mapFoldingState = sequential(mapFoldingState)

			case 'theorem2Trimmed':
				from mapFolding.dataBaskets import MapFoldingState  # noqa: PLC0415
				mapFoldingState: MapFoldingState = MapFoldingState(mapShape)

				from mapFolding.syntheticModules.initializeStateA007822 import transitionOnGroupsOfFolds  # noqa: PLC0415
				mapFoldingState = transitionOnGroupsOfFolds(mapFoldingState)

				from mapFolding.syntheticModules.theorem2A007822Trimmed import count  # noqa: PLC0415
				mapFoldingState = count(mapFoldingState)

			case _:
				from mapFolding.dataBaskets import MapFoldingState  # noqa: PLC0415
				mapFoldingState: MapFoldingState = MapFoldingState(mapShape)

				from mapFolding.syntheticModules.algorithmA007822 import doTheNeedful  # noqa: PLC0415
				mapFoldingState = doTheNeedful(mapFoldingState)

		foldsTotal = mapFoldingState.groupsOfFolds

	elif flow == 'daoOfMapFolding':
		from mapFolding.dataBaskets import MapFoldingState  # noqa: PLC0415
		mapFoldingState: MapFoldingState = MapFoldingState(mapShape)

		from mapFolding.daoOfMapFolding import doTheNeedful  # noqa: PLC0415
		mapFoldingState = doTheNeedful(mapFoldingState)
		foldsTotal = mapFoldingState.foldsTotal

	elif flow == 'numba':
		from mapFolding.dataBaskets import MapFoldingState  # noqa: PLC0415
		mapFoldingState: MapFoldingState = MapFoldingState(mapShape)

		from mapFolding.syntheticModules.daoOfMapFoldingNumba import doTheNeedful  # noqa: PLC0415
		mapFoldingState = doTheNeedful(mapFoldingState)
		foldsTotal = mapFoldingState.foldsTotal

	elif flow == 'theorem2' and any(dimension > 2 for dimension in mapShape):
		from mapFolding.dataBaskets import MapFoldingState  # noqa: PLC0415
		mapFoldingState: MapFoldingState = MapFoldingState(mapShape)

		from mapFolding.syntheticModules.initializeState import transitionOnGroupsOfFolds  # noqa: PLC0415
		mapFoldingState = transitionOnGroupsOfFolds(mapFoldingState)

		from mapFolding.syntheticModules.theorem2 import count  # noqa: PLC0415
		mapFoldingState = count(mapFoldingState)

		foldsTotal = mapFoldingState.foldsTotal

	elif flow == 'theorem2Trimmed' and any(dimension > 2 for dimension in mapShape):
		from mapFolding.dataBaskets import MapFoldingState  # noqa: PLC0415
		mapFoldingState: MapFoldingState = MapFoldingState(mapShape)

		from mapFolding.syntheticModules.initializeState import transitionOnGroupsOfFolds  # noqa: PLC0415
		mapFoldingState = transitionOnGroupsOfFolds(mapFoldingState)

		from mapFolding.syntheticModules.theorem2Trimmed import count  # noqa: PLC0415
		mapFoldingState = count(mapFoldingState)

		foldsTotal = mapFoldingState.foldsTotal

	elif (flow == 'theorem2Numba' or taskDivisions == 0) and any(dimension > 2 for dimension in mapShape):
		from mapFolding.dataBaskets import MapFoldingState  # noqa: PLC0415
		mapFoldingState: MapFoldingState = MapFoldingState(mapShape)

		from mapFolding.syntheticModules.initializeState import transitionOnGroupsOfFolds  # noqa: PLC0415
		mapFoldingState = transitionOnGroupsOfFolds(mapFoldingState)

		from mapFolding.syntheticModules.dataPacking import sequential  # noqa: PLC0415
		mapFoldingState = sequential(mapFoldingState)

		foldsTotal = mapFoldingState.foldsTotal

	elif taskDivisions > 1:
		from mapFolding.dataBaskets import ParallelMapFoldingState  # noqa: PLC0415
		parallelMapFoldingState: ParallelMapFoldingState = ParallelMapFoldingState(mapShape, taskDivisions=taskDivisions)

		from mapFolding.syntheticModules.countParallelNumba import doTheNeedful  # noqa: PLC0415

		# `listStatesParallel` exists in case you want to research the parallel computation.
		foldsTotal, listStatesParallel = doTheNeedful(parallelMapFoldingState, concurrencyLimit) # pyright: ignore[reportUnusedVariable]

	else:
		from mapFolding.dataBaskets import MapFoldingState  # noqa: PLC0415
		mapFoldingState: MapFoldingState = MapFoldingState(mapShape)

		from mapFolding.syntheticModules.daoOfMapFoldingNumba import doTheNeedful  # noqa: PLC0415
		mapFoldingState = doTheNeedful(mapFoldingState)
		foldsTotal = mapFoldingState.foldsTotal

	# Follow memorialization instructions ---------------------------------------------

	if pathFilenameFoldsTotal is not None:
		saveFoldsTotal(pathFilenameFoldsTotal, foldsTotal)

	return foldsTotal
