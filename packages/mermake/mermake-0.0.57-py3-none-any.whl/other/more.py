from mermake.deconvolver import Deconvolver
import os, time, queue, threading
import numpy as np
import cupy as cp

# YOUR read_im unchanged
def read_im(path, return_pos=False):
    import dask.array as da
    dirname = os.path.dirname(path)
    fov = os.path.basename(path).split('_')[-1].split('.')[0]
    file_ = dirname + os.sep + fov + os.sep + 'data'
    image = da.from_zarr(file_)[1:]

    shape = image.shape
    xml_file = os.path.dirname(path) + os.sep + os.path.basename(path).split('.')[0] + '.xml'
    if os.path.exists(xml_file):
        txt = open(xml_file, 'r').read()
        tag = '<z_offsets type="string">'
        zstack = txt.split(tag)[-1].split('</')[0]

        tag = '<stage_position type="custom">'
        x, y = eval(txt.split(tag)[-1].split('</')[0])

        nchannels = int(zstack.split(':')[-1])
        nzs = (shape[0] // nchannels) * nchannels
        image = image[:nzs].reshape([shape[0] // nchannels, nchannels, shape[-2], shape[-1]])
        image = image.swapaxes(0, 1)
    if image.dtype == np.uint8:
        image = image.astype(np.float32)**2
    if return_pos:
        return image, x, y
    return image
import os, time
import numpy as np
import cupy as cp
import dask.array as da
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue

stop = object()

def async_fetch(paths, max_queue=4, max_workers=4):
    q = Queue(maxsize=max_queue)
    executor = ThreadPoolExecutor(max_workers=max_workers)

    def fetch_and_push(path):
        try:
            im = read_im(path)
            for i in range(im.shape[0]):
                arr = im[i].compute()
                gpu = cp.asarray(arr)
                q.put(gpu)
        except Exception as e:
            print(f"Error reading {path}: {e}")

    def runner():
        futures = [executor.submit(fetch_and_push, path) for path in paths]
        for fut in as_completed(futures):
            pass
        q.put(stop)

    from threading import Thread
    Thread(target=runner, daemon=True).start()
    return q

from concurrent.futures import ThreadPoolExecutor
import queue
import threading
import cupy as cp
import dask.array as da

stop = object()

def prefetch_gpu(paths, max_workers=4):
    q = queue.Queue(maxsize=2)

    def fetch_and_push(path):
        im = read_im(path)
        gpu_im = cp.asarray(im.compute())  # load + transfer to GPU
        q.put(gpu_im)

    def runner():
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(fetch_and_push, path) for path in paths]
            for f in futures:
                f.result()  # wait and re-raise errors if any
        q.put(stop)

    threading.Thread(target=runner, daemon=True).start()
    return q




if __name__ == "__main__":
	from glob import glob

	master_data_folders = ['/data/07_22_2024__PFF_PTBP1']
	iHm = 1; iHM = 16
	shape = (4, 40, 3000, 3000)
	items = [(set_, ifov) for set_ in ['_set1'] for ifov in range(1, 5)]
	hybs = []
	fovs = []

	psf_file = '../psfs/dic_psf_60X_cy5_Scope5.pkl'
	psfs = np.load(psf_file, allow_pickle=True)
	key = (0,1500,1500)
	psfs = { key : psfs[key] }
	deconvolver = Deconvolver(psfs, shape[1:], tile_size=300, overlap=89, zpad=39, beta=0.0001)

	def get_files(master_folders, item, iHm, iHM):
		set_, ifov = item
		fov = f"Conv_zscan{ifov:01d}_001.zarr"
		all_flds = []
		for master in master_folders:
			for i in range(iHm, iHM + 1):
				fld = os.path.join(master, f"H{i}_AER{set_}")
				if os.path.isdir(fld):
					all_flds.append(fld)
		return all_flds, fov

	for item in items[:4]:
		all_flds, fov = get_files(master_data_folders, item, iHm=iHm, iHM=iHM)
		hybs.append(all_flds)
		fovs.append(fov)

	paths = []
	for all_flds, fov in zip(hybs, fovs):
		for hyb in all_flds:
			file = os.path.join(hyb, fov)
			paths.append(file)

	q = prefetch_gpu(paths)

	while True:
		start = time.time()
		im = q.get()
		end = time.time()
		print(f"Got GPU image: {im.shape}", end=' ')
		print(f"time: {end - start:.6f} seconds")
		if im is stop:
			break
		start = time.time()
		for icol in [0,1,2,3]:
			for tile in deconvolver.tile_wise(im[icol]):
				pass
		end = time.time()
		print(f"deconv time: {end - start:.6f} seconds")

