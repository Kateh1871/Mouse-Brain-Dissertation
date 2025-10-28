import os
import nibabel as nib
import trimesh
import numpy as np
import pyvista as pv
import matplotlib.pyplot as plt
import API as allen
import pickle as pkl
import nrrd

# AVOID CIRCULAR IMPORTS

class Mesh_Handler():
    # base for handling mesh files

    def __init__(self,
                 folder_path: str = './Region_Mesh/Raw',
                 missing_mesh_log: str = 'missing.pyobj'
                 ):

        self.folder = folder_path
        self.missing_filepath = f'{folder_path}/{missing_mesh_log}'
        self.tree = allen.Reference_Tree()

        # if mesh folder doesnt exist
        if not os.path.exists(self.folder):
            os.makedirs(self.folder, exist_ok=True)
            self.missing = []
        
        # if mesh folder exists and missing meshes file exists
        elif os.path.exists(self.missing_filepath):
            with open(self.missing_filepath, 'rb') as f:
                self.missing = pkl.load(f)

        # if mesh folder exists and missing mesh file doesnt exist
        elif not os.path.exists(self.missing_filepath):
            self.missing = []

    def Load_Mesh(self,
                  region: int,
                  transform: bool = True):
        """
        region : id of region to open
        transform : transform the mesh so that the centroid of the cortex is at [0, 0, 0] and camera can be reset to the preferred view

        returns: trimesh object

        opens raw .obj file from Allen Institute
        """

        path = f'{self.folder}/{region}.obj'

        # if mesh is known not to exist
        if region in self.missing:
            file = trimesh.Trimesh()
            return file

        # if mesh may exist but hasn't been downloaded
        elif not os.path.exists(path) and region not in self.missing:
            try:
                allen.Download_Mesh(region)
                file = trimesh.load(path)

            except FileNotFoundError:
                # if mesh isn't available remember it
                self.missing.append(region)
                with open (self.missing_filepath, 'wb') as f:
                    pkl.dump(self.missing, f)

                file = trimesh.Trimesh()
                return file

        # if mesh is already downloaded
        elif os.path.exists(path):
            file = trimesh.load(path)


        # transform mesh so that the centroid of the isocortex is at [0, 0, 0]
        if transform is True:
            # centroid of isocortex
            translation = -1 * np.asarray([5815.30949447, 501.96668849, 5692.50297221])
            file.apply_translation(translation)

        return file


    def Hemisphere_Filter(self,
                          region: int,
                          hemisphere: str = 'left'):
        """
        Filters meshes to only single side of brain
        at leat one of id and mesh should be provided

        region: id of brain region, if provided loads from file
        hemisphere: which side of brain to keep, should be either 'left' or 'right' or 'both'
            'both' returns entire set of bodies
        """


        mesh_original = self.Load_Mesh(region)

        if hemisphere == 'both':
            return mesh

        mesh_bodies_temp = []
        mesh_bodies = mesh_original.split()
        for mesh in mesh_bodies:
            # left side has -ve coords
            if hemisphere == 'left' and mesh.center_mass[2] < 0:
                mesh_bodies_temp.append(mesh)

            if hemisphere == 'right' and mesh.center_mass[2] > 0:
                mesh_bodies_temp.append(mesh)

            if -0.0001 < mesh.center_mass[2] < 0.0001:
                print(f'mesh has centroid at z: 0. Unable to determine hemisphere returning full mesh')
                return mesh_original
        
        mesh_new = trimesh.util.concatenate(mesh_bodies_temp)

        return mesh_new


def Obj_Gifti(loadFolder: str = 'Raw',
              saveFolder: str = 'Gii'
              ):
    # converts raw meshes from allen api from .obj to .gii types
    # targets main/Region_Mesh/Raw 

    meshFolder = 'Region_Mesh'  # all meshes
    rawMesh = os.listdir(f'{meshFolder}/{loadFolder}/')  # list of raw mesh files
    giiFolder = f'./{meshFolder}/{saveFolder}'     # save location


    # make Gii subfolder if doesn't exist
    meshTypes = os.listdir(meshFolder)
    if 'Gii' not in meshTypes:
        os.mkdir(f'{meshFolder}/Gii')


    for meshFile in rawMesh:
        mesh = trimesh.load(f'./{meshFolder}/Raw/{meshFile}')

        # split out vertices
        giiVertices = nib.gifti.GiftiDataArray(data=mesh.vertices.astype(np.float32),
                                               intent='NIFTI_INTENT_POINTSET')
        
        # split out triangle faces
        # print(mesh.faces.astype(np.float32))
        giiFaces = nib.gifti.GiftiDataArray(data=mesh.faces.astype(np.float32),
                                            intent='NIFTI_INTENT_POINTSET')

        # merge into single gifti image 
        giiImg = nib.gifti.GiftiImage(darrays=[giiVertices, giiFaces])
    
        # print(f'{giiFolder}/{meshFile[:-4]}.gii')

        nib.save(giiImg, f'{giiFolder}/{meshFile[:-4]}.gii')


def Open_Gifti(region: int = None,
               filePath: str = None
               ):
    
    # requires one of region or filePath
    if region is not None:
        file = nib.load(f'Region_Mesh/Gii/{region}.gii')
    
    if filePath is not None:
        file = nib.load(filePath)

    return file


def Open_Raw(region: int,
             transform = True,
             rotation: float = np.pi
             ):
    
    """
    region : id of region to open
    transform : transform the mesh so that the centroid of the cortex is at [0, 0, 0] and camera can be reset to the preferred view

    returns: trimesh object

    opens raw .obj file from Allen Institute, easier to work with in pymesh than a gifti
    """

    path = f'./Region_Mesh/Raw/{region}.obj'

    # list of meshes that don't exist in API to avoid attempting to download the same file multiple times
    if  os.path.exists('./Region_Mesh/Raw/missing.pyobj'):
        with open ('./Region_Mesh/Raw/missing.pyobj', 'rb') as f:
            missing_mesh = pkl.load(f)
    else:
        missing_mesh = []


    # if mesh is known not to exist
    if region in missing_mesh:
        file = trimesh.Trimesh()
        return file

    # if mesh may exists but hasn't been downloaded
    elif not os.path.exists(path) and region not in missing_mesh:
        try:
            allen.Download_Mesh(region)
            file = trimesh.load(path)
            
        except FileNotFoundError:
            # if mesh isn't available remember it
            missing_mesh.append(region)
            with open ('./Region_Mesh/Raw/missing.pyobj', 'wb') as f:
                pkl.dump(missing_mesh, f)

            file = trimesh.Trimesh()
            return file

    # if mesh is already downloaded
    elif os.path.exists(path):
        file = trimesh.load(path)
    


    # transform mesh so that the centroid of the isocortex is at [0, 0, 0] and is rotated correctly
    if transform is True:
        # centroid of isocortex
        translation = -1 * np.asarray([5815.30949447, 501.96668849, 5692.50297221])
        # rotation origin and amount
        rotation = trimesh.transformations.rotation_matrix(1*rotation, [0, 1, 0], [0, 0, 0])
        # scale factor
        scale = np.eye(4)

        file.apply_translation(translation)
        # file.apply_transform(rotation)


    return file


def Open_Voxel(region: int):
    """
    opens .nrrd voxel file. This should be compatible with functions that expects nifti data since it splits volume and header data
    returns:
        data: boolean array of 3D space, where 1 is structure existing and 0 is empty
        header: dictionary of nrrd header data. includes metadata about structure and spacing/volume/origin data
    """

    path = f'./Region_Mesh/Voxel/{region}.nrrd'

    # list of regions that don't exist in API to avoid attempting to download the same file multiple times
    if  os.path.exists('./Region_Mesh/Voxel/missing.pyobj'):
        with open ('./Region_Mesh/Voxel/missing.pyobj', 'rb') as f:
            missing_voxel = pkl.load(f)
    else:
        missing_voxel = []


    # if voxel is known not to exist
    if region in missing_voxel:
        data, header = [None, None]
        return data, header

    # if voxel may exists but hasn't been downloaded
    elif not os.path.exists(path) and region not in missing_voxel:
        try:
            allen.Download_Voxel(region)
            data, header = nrrd.read(path)  # raises FileNotFound if failed to download
            
        except FileNotFoundError:
            # if voxel isn't available remember it
            missing_voxel.append(region)
            with open ('./Region_Mesh/Raw/missing.pyobj', 'wb') as f:
                pkl.dump(missing_voxel, f)

            data, header = [None, None]
            return data, header

    # if voxel is already downloaded
    elif os.path.exists(path):
        data, header = nrrd.read(path)
    
    return data, header



    


    