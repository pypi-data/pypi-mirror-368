import matplotlib
matplotlib.use('Agg')
from shinestacker.config.constants import constants
from shinestacker.algorithms.utils import read_img
from shinestacker.algorithms.stack_framework import StackJob, CombinedActions
from shinestacker.algorithms.align import align_images, AlignFrames


def test_align():
    try:
        img_1, img_2 = [read_img(f"examples/input/img-jpg/000{i}.jpg") for i in (2, 3)]
        n_good_matches, M, img_warp = align_images(img_1, img_2)
        assert img_warp is not None
        assert n_good_matches > 100
    except Exception:
        assert False


def test_align_homo():
    try:
        img_1, img_2 = [read_img(f"examples/input/img-jpg/000{i}.jpg") for i in (2, 3)]
        n_good_matches, M, img_warp = align_images(img_1, img_2, alignment_config={'transform': constants.ALIGN_HOMOGRAPHY})
        assert img_warp is not None
        assert n_good_matches > 10
    except Exception:
        assert False


def test_align_rescale():
    try:
        img_1, img_2 = [read_img(f"examples/input/img-jpg/000{i}.jpg") for i in (2, 3)]
        n_good_matches, M, img_warp = align_images(img_1, img_2, alignment_config={'subsample': 4})
        assert img_warp is not None
        assert n_good_matches > 10
    except Exception:
        assert False


def test_align_ecc():
    try:
        img_1, img_2 = [read_img(f"examples/input/img-jpg/000{i}.jpg") for i in (2, 3)]
        n_good_matches, M, img_warp = align_images(img_1, img_2, alignment_config={'ecc_refinement': True})
        assert img_warp is not None
        assert n_good_matches > 10
    except Exception:
        assert False


def test_jpg():
    try:
        job = StackJob("job", "examples", input_path="input/img-jpg", callbacks='tqdm')
        job.add_action(CombinedActions("align-jpg", [AlignFrames(plot_summary=True)],
                                       output_path="output/img-jpg-align"))
        job.run()
    except Exception:
        assert False


def test_tif():
    try:
        job = StackJob("job", "examples", input_path="input/img-tif", callbacks='tqdm')
        job.add_action(CombinedActions("align-tif", [AlignFrames(plot_summary=True)],
                                       output_path="output/img-tif-align"))
        job.run()
    except Exception:
        assert False


if __name__ == '__main__':
    test_align()
    test_align_homo()
    test_align_rescale()
    test_jpg()
    test_tif()
