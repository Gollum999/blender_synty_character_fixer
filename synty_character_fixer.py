#!/usr/bin/env python3
bl_info = {
    # required
    'name': 'Synty FBX Character Importer Addon',
    'blender': (2, 82, 0),
    'category': 'Import-Export',
    # optional
    'version': (1, 0, 0),
    'author': 'Tim Sanders',
    'description': 'Import and clean up Synty FBX character models',
}

import argparse
import contextlib
import logging
import sys
from pathlib import Path

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator


logger = logging.getLogger(__name__)


class SyntyFbxImporter(Operator, ImportHelper):
    """ Import Synty FBX character file and clean up the model. """
    bl_idname = 'importers.synty_fbx_importer'
    bl_label = 'Import'

    # ImportHelper mixin class uses this
    filename_ext = '.fbx'

    filter_glob: StringProperty(
        default='*.fbx',
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context: bpy.types.Context):
        import_and_clean_up_model(self.filepath)
        return {'FINISHED'}


ADDON_CLASSES = [
    SyntyFbxImporter,
]


def menu_func_import(self, context: bpy.types.Context) -> None:
    self.layout.operator(SyntyFbxImporter.bl_idname, text='Synty FBX (.fbx)')


def register() -> None:
    for cls in ADDON_CLASSES:
        bpy.utils.register_class(cls)
        bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister() -> None:
    for cls in ADDON_CLASSES:
        bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
        bpy.utils.unregister_class(cls)


def prepare_scene() -> None:
    # delete default cube
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.data.objects['Cube'].select_set(True)
    bpy.ops.object.delete()
    bpy.data.materials.remove(bpy.data.materials['Material'])


def import_and_clean_up_model(model_file: str):
    logger.debug(f'Importing {model_file}')
    bpy.ops.import_scene.fbx(
        filepath=model_file,
        use_anim=False,
        ignore_leaf_bones=True,
        force_connect_children=True,
        automatic_bone_orientation=True,
    )

    # reset pose
    logger.debug('Resetting pose')
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.transforms_clear()

    # delete useless bones
    logger.debug('Deleting extra bones')
    bpy.ops.object.mode_set(mode='EDIT')
    for armature in bpy.data.armatures.values():
        for name, bone in armature.edit_bones.items():
            if name.startswith(('ik_', '_ik_')):
                armature.edit_bones.remove(bone)

    # fix shading
    logger.debug('Fixing shading')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_flat()
    for mesh in bpy.data.meshes.values():
        mesh.use_auto_smooth = False

    # load texture
    logger.debug('Loading texture')
    texture_path = _find_texture_file(model_file)
    for material in bpy.data.materials.values():
        if material.node_tree is None:
            continue
        base_color = material.node_tree.nodes['Principled BSDF'].inputs[0]
        texture_node = material.node_tree.nodes.new('ShaderNodeTexImage')
        img = bpy.data.images.load(str(texture_path))
        texture_node.image = img
        material.node_tree.links.new(texture_node.outputs[0], base_color)


def _find_texture_file(model_file: str) -> Path:
    model_path = Path(model_file)
    current_dir = model_path.parent.resolve()
    while not (current_dir / 'Textures').exists():
        current_dir = current_dir.parent
        if current_dir == current_dir.root:
            raise RuntimeError(f'Failed to find Textures directory when starting from {model_file} - make sure the model'
                               'shares a parent directory with the Textures directory')
    texture_dir = current_dir / 'Textures'
    texture_glob = '*Texture_01_A.png'
    textures = list(texture_dir.glob(texture_glob))  # they seem to be pretty consistent with this naming convention
    if len(textures) > 1:
        # assume that extra qualifiers mean the texture is specialized for some non-character objects
        logger.warning('Found multiple potential textures - taking the one with the shortest name')
        return sorted(textures, key=lambda f: len(str(f)))[0]
    elif len(textures) == 1:
        return textures[0]
    else:
        raise RuntimeError(f'Failed to find texture with a name like "{texture_glob}"')


def save(output_file: str) -> None:
    bpy.ops.wm.save_as_mainfile(filepath=output_file)


def parse_batch_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing output')
    parser.add_argument('input_file', nargs=1, help='Input FBX file')
    parser.add_argument('output_file', nargs=1, help='Output BLEND file')

    extra_args_start_idx = sys.argv.index('--') + 1
    passthrough_args = sys.argv[extra_args_start_idx:]
    args = parser.parse_args(passthrough_args)

    args.input_file = args.input_file[0]
    args.output_file = args.output_file[0]

    return args


def run_batch(args: argparse.Namespace) -> None:
    if Path(args.output_file).exists() and not args.overwrite:
        logger.warning(f'{args.output_file} already exists, skipping')
    else:
        prepare_scene()
        import_and_clean_up_model(args.input_file)
        save(args.output_file)


if __name__ == '__main__':
    if len(sys.argv) == 1:  # blender plugin
        with contextlib.suppress(RuntimeError):
            unregister()
        register()
    else:  # batch mode
        args = parse_batch_args()
        run_batch(args)
