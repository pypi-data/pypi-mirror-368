from csv import reader
from os import walk
import os
import pygame

def _resolve_asset_path(relative_path: str) -> str:
    base_dir = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(base_dir, relative_path))

def import_csv_layout(path):
    terrain_map = []
    resolved = _resolve_asset_path(path)
    with open(resolved) as level_map:
        layout = reader(level_map, delimiter=',')
        for row in layout:
            terrain_map.append(list(row))
        return terrain_map

def import_folder(path):
    surface_list = []
    resolved = _resolve_asset_path(path)

    for _, __, img_files in walk(resolved):
        for image in img_files:
            full_path = os.path.join(resolved, image)
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list
