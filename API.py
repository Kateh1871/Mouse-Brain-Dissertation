import os
import allensdk
from allensdk.core.reference_space_cache import ReferenceSpaceCache
from allensdk.core.structure_tree import StructureTree
from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache


# API related functions
# for dynamic work/testing use the notebook

def Reference_Tree(structure_id: str = 'annotation/ccf_2017'):
    """
    Opens the information for a reference mouse brain
    region_id: id of structure to load, 1 is CCFv3 2017, most recent mouse data
    """

    resolution = 25     # in microns (um), connectivity data is 25um
    manifest = 'manifest.json'  # log of downloaded files
    rspc = ReferenceSpaceCache(resolution = resolution,
                               reference_space_key = structure_id,
                               manifest = manifest
                               )
    # see for methods:
    #   https://allensdk.readthedocs.io/en/latest/allensdk.core.structure_tree.html
    #   https://allensdk.readthedocs.io/en/latest/allensdk.core.simple_tree.html#allensdk.core.simple_tree.SimpleTree
    tree = rspc.get_structure_tree(structure_graph_id=structure_id)

    return tree


def Download_Mesh(region_id: int|list[int],
                  structure_id: str = 'annotation/ccf_2017',
                  mesh_folder: str = './Region_Mesh/Raw'):
    """
    Downloads .obj meshes for given region(s)
    region_id: int | list[int]
        ids of region(s) to download
    mesh_folder: str
        directory to save files to, if changed some functions in Utils won't work properly
    """
    resolution = 25     # in microns (um), connectivity data is 25um
    manifest = 'manifest.json'  # log of downloaded files
    rspc = ReferenceSpaceCache(resolution=resolution,
                               reference_space_key=structure_id,
                               manifest=manifest
                               )
    
    if isinstance(region_id, int):
        print(f'downloading mesh {region_id}')
        mesh = rspc.get_structure_mesh(region_id, f'{mesh_folder}/{region_id}.obj')
            

    elif isinstance(region_id, list):
        for region in region_id:
            try:
                mesh = rspc.get_structure_mesh(region, f'{mesh_folder}/{region}.obj')
            except:
                print(f'region {region} not found in API')
    
    return


def Region_Children(region_id: int = 315):
    """
    region_id: 315 corresponds to isocortex
    Gets the children (not all descendants) of a particular region
    """

    tree = Reference_Tree()

    child_id = tree.child_ids([region_id])

    return child_id[0]

