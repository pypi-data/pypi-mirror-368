import os
import sys
import glob

def get_Xtzxy(X,X_ref,tzxy0,resc,target=3):
    tzxy = tzxy0
    Npts =0
    for dist_th in np.linspace(resc,target,5):
        XT = X-tzxy
        ds,inds = cKDTree(X_ref).query(XT)
        keep = ds<dist_th
        X_ref_ = X_ref[inds[keep]]
        X_ = X[keep]
        tzxy = np.mean(X_-X_ref_,axis=0)
        #print(tzxy)
        Npts = np.sum(keep)
    return tzxy,Npts

def get_im_from_Xh(Xh,resc=5,pad=10):
    X = np.round(Xh[:,:3]/resc).astype(int)
    Xm = np.min(X,axis=0)
    XM = np.max(X,axis=0)
    keep = X<=(XM-[0,pad,pad])
    keep &= X>=(Xm+[0,pad,pad])
    keep = np.all(keep,-1)
    X = X[keep]
    if False:
        Xm = np.min(X,axis=0)
        X-=Xm
    else:
        Xm=np.array([0,0,0])

    sz = np.max(X,axis=0)
    imf = np.zeros(sz+1,dtype=np.float32)
    imf[tuple(X.T)]=1
    return imf,Xm

def get_best_translation_points(X,X_ref,resc=10,target=1,return_counts=False):

    im,Xm = get_im_from_Xh(X,resc=resc)
    im_ref,Xm_ref = get_im_from_Xh(X_ref,resc=resc)

    from scipy.signal import fftconvolve
    im_cor = fftconvolve(im,im_ref[::-1,::-1,::-1])
    #plt.imshow(np.max(im_cor,0))
    tzxy = np.array(np.unravel_index(np.argmax(im_cor),im_cor.shape))-im_ref.shape+1+Xm-Xm_ref
    tzxy = tzxy*resc
    Npts=0
    tzxy,Npts = get_Xtzxy(X,X_ref,tzxy,resc=resc,target=target)
    if return_counts:
        return tzxy,Npts
    return tzxy

def get_best_translation_pointsV2(fl,fl_ref,save_folder,set_,resc=5):

	obj = get_dapi_features(fl,save_folder,set_)
	obj_ref = get_dapi_features(fl_ref,save_folder,set_)
	tzxyf,tzxy_plus,tzxy_minus,N_plus,N_minus = np.array([0,0,0]),np.array([0,0,0]),np.array([0,0,0]),0,0
	if (len(obj.Xh_plus)>0) and (len(obj.Xh_minus)>0) and  (len(obj_ref.Xh_plus)>0) and (len(obj_ref.Xh_minus)>0):
		X = obj.Xh_plus[:,:3]
		X_ref = obj_ref.Xh_plus[:,:3]
		tzxy_plus,N_plus = get_best_translation_points(X,X_ref,resc=resc,return_counts=True)

		X = obj.Xh_minus[:,:3]
		X_ref = obj_ref.Xh_minus[:,:3]
		tzxy_minus,N_minus = get_best_translation_points(X,X_ref,resc=resc,return_counts=True)

		tzxyf = -(tzxy_plus+tzxy_minus)/2 

def compute_drift_V2(save_folder,fov,all_flds,set_,redo=False,gpu=True):
	drift_fl = save_folder+os.sep+'driftNew_'+fov.split('.')[0]+'--'+set_+'.pkl'
	if not os.path.exists(drift_fl) or redo:
		fls = [fld+os.sep+fov for fld in all_flds]
		fl_ref = fls[len(fls)//2]
		newdrifts = []
		for fl in fls:
			drft = get_best_translation_pointsV2(fl,fl_ref,save_folder,set_,resc=5)
			newdrifts.append(drft)
		pickle.dump([newdrifts,all_flds,fov,fl_ref],open(drift_fl,'wb'))

if __name__ == "__main__":
	sf = '../MERFISH_Analysis_AER'
	fov = 'Conv_zscan1_001'
	set_ = 'set1'
	all_flds = glob.glob('../MERFISH_Analysis_AER/Conv_zscan1_001--H*_AER_set1--dapiFeatures.npz')
	print(all_flds)
	compute_drift_V2(sf, fov,all_flds, set_)


