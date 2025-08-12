import os
import pathlib

from rebotics_sdk.cli.utils import run_with_processes


def draw_annotated_drawing(root_folder, segmentation_per_image, mode, concurrency):
    calls = [f for f in os.scandir(root_folder) if f.is_dir()]

    for call in calls:
        if mode == 'items':
            result_folder = pathlib.Path(call.path) / 'annotated_img'
            result_folder.mkdir(parents=True, exist_ok=True)
            call_frames = get_call_frames(call, segmentation_per_image, mode, result_folder)
            run_with_processes(invoked=draw_bboxes, iterable=call_frames, concurrency=concurrency)
        if mode == 'remote_url':
            result_folder = pathlib.Path(call.path)
            call_frames = get_call_frames(call, segmentation_per_image, mode, result_folder)
            run_with_processes(invoked=draw_mask, iterable=call_frames, concurrency=concurrency)


def get_call_frames(call, image_segmentation, mode, result_folder):
    call_frames = [
        (frame.name, frame.path, image_segmentation, result_folder, mode) for f in os.scandir(call)
        if f.is_dir() and f.name == 'frames'
        for frame in os.scandir(f) if frame.is_file()
    ]
    return call_frames


def draw_bboxes(image_name, image_path, per_image, result_folder, mode):
    try:
        import cv2
    except ImportError:
        raise ImportError('OpenCV is not installed. Please install it with `pip install opencv-python`')

    GREEN = (0, 255, 0,)
    RED = (0, 0, 255)

    cv2_image = cv2.imread(str(image_path))
    figure_to_draw = get_parts(mode, image_name, per_image, result_folder)

    if (cv2_image is not None) and figure_to_draw:
        for items in figure_to_draw:
            color = GREEN
            if items:
                x1 = items['x1']
                y1 = items['y1']
                x2 = items['x2']
                y2 = items['y2']
                category = items['category']
                if category != 'item':
                    color = RED
                cv2.rectangle(cv2_image, (int(x1), int(y1)), (int(x2), int(y2)), color=color, thickness=2)

        local_drawn_image_path = str(result_folder / image_name)
        cv2.imwrite(str(local_drawn_image_path), cv2_image)


def draw_mask(image_name, image_path, per_image, result_folder, mode):
    import cv2

    cv2_image = cv2.imread(str(image_path))
    figure_to_draw = get_parts(mode, image_name, per_image, result_folder)

    if (cv2_image is not None) and figure_to_draw:
        id_to_color = {
            1: [255, 0, 0],
            2: [0, 0, 255]
        }
        annotated_mask = pathlib.Path(result_folder) / 'annotated_mask'
        annotated_mask.mkdir(parents=True, exist_ok=True)

        mask = cv2.imread(str(figure_to_draw))

        for idx, color in id_to_color.items():
            mask[(mask == idx).all(-1)] = color

        result_image = cv2.addWeighted(mask, 0.6, cv2_image, 0.5, 0)

        local_drawn_image_path = str(annotated_mask / image_name)
        cv2.imwrite(str(local_drawn_image_path), result_image)


def get_parts(key, image_name, per_image, result_folder):
    if key == 'items':
        for image in per_image:
            if image["image_name"] == image_name:
                return image.get(key)

    if key == 'remote_url':
        all_masks = pathlib.Path(result_folder).parent / 'all_masks'
        for frame in all_masks.glob('*.jpg'):
            if frame.name == image_name:
                return frame
    return
