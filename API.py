import os
import allensdk
from allensdk.core.reference_space_cache import ReferenceSpaceCache
from allensdk.core.structure_tree import StructureTree
from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache


# API related functions
# for dynamic work/testing use the notebook

def Reference_Tree(region_id: int = 315):
    """
    Opens the information for a reference mouse brain
    region_id: id of region to have a parent, 315 corresponds to isocortex
    """
    resolution = 25     # in microns (um), connectivity data is 25um
    manifest = 'manifest.json'  # log of downloaded files
    space = 'annotation/ccf_2017'   # which version of data to use, 2017 is CCFv3

    rspc = ReferenceSpaceCache(resolution = resolution,
                               reference_space_key = space,
                               maifest = manifest
                               )
    # see for methods:
    #   https://allensdk.readthedocs.io/en/latest/allensdk.core.structure_tree.html
    #   https://allensdk.readthedocs.io/en/latest/allensdk.core.simple_tree.html#allensdk.core.simple_tree.SimpleTree
    tree = rspc.get_structure_tree(file_name='tree.tree', structure_graph_id=region_id)

    return tree


def Region_Children(region_id: int = 315):
    """
    region_id: 315 corresponds to isocortex
    Gets the children (not all descendants) of a particular region
    """

    tree = Reference_Tree()

    child_id = tree.child_ids([region_id])

    return child_id[0]

