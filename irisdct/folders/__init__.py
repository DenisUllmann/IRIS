import sys
sys.path.append("..")
from config import config as cfg
from .foldermaker import fmake

parent = cfg.parent

source = parent / 'fits_seq_example' # source directory of fits files

source_children = source.glob('**/*.fits') # pathes to all fits files

# directory for analysis savings corresponding to one fits file
def dir_source_child_maker(source_child, source):
    return source.parent / 'analysis' / source_child.relative_to(source).stem

# pathes created for one fits file
def dirm_dict_maker(dir_source_child):
    if cfg.downsize:
        dir_ds = dir_source_child /'Downsized_%i' % int(cfg.ds_ratio*100)
    else:
        dir_ds = dir_source_child
    
    dir_images = dir_ds / 'Images'
    dir_hist = dir_ds / 'Hist'
    dir_dct = dir_ds / '3D_DCT'
    dir_cv = dir_ds / '3D_CV'
    dir_gp = dir_ds / 'GP'
    dir_frames = dir_ds / 'Frames'
    dir_vid = dir_ds / 'Videos'
    
    return [dir_images, dir_hist, dir_dct, dir_cv, dir_gp, dir_frames, dir_vid]

# to make the pathes of one set of pathes names
def foldersmaker(dir_dict):
    for dirm in dir_dict:
        fmake(dirm)
    return

# to make the pathes for the analysis of one fits file
def source_child_foldermaker(source_child, source):
    foldersmaker(dirm_dict_maker(dir_source_child_maker(source_child, source)))
    return

# to get the path for saving in the root of analysis for one fits file
def name_saving(source_path, source, name):
    return dir_source_child_maker(source_path, source) / name

# to get the path for saving in the Images of one fits file
def pathname_image(source_path, source, name):
    return dir_source_child_maker(source_path, source) / 'Images' / name

# to get the path for saving in the 3D_DCT of one fits file
def pathname_3dct(source_path, source, name):
    return dir_source_child_maker(source_path, source) / '3D_DCT' / name

# to get the path for saving in the 3D_CV of one fits file
def pathname_3dcv(source_path, source, name):
    return dir_source_child_maker(source_path, source) / '3D_CV' / name

# to get the path for saving in the GP of one fits file
def pathname_gp(source_path, source, name):
    return dir_source_child_maker(source_path, source) / 'GP' / name

# to get the path for saving in the Frames of one fits file
def pathname_frame(source_path, source, name):
    return dir_source_child_maker(source_path, source) / 'Frames' / name

# to get the path for saving in the Videos of one fits file
def pathname_video(source_path, source, name):
    return dir_source_child_maker(source_path, source) / 'Videos' / name
