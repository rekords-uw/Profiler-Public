
# coding: utf-8

# In[1]:

import json
import os
from profiler.core import *


# ## 1. Instantiate Engine
# * workers : number of processes
# * tol     : tolerance for differences when creating training data (set to 0 if data is completely clean)
# * eps     : error bound for inverse covariance estimation (since we use conservative calculation when determining minimum sample size, we recommend to set eps <= 0.01)
# * embedtxt: if set to true, differentiate b/w textual data and categorical data, and use word embedding for the former

# In[2]:

pf = Profiler(workers=2, tol=1e-6, eps=0.05, embedtxt=True)


# ## 2. Load Data
# * name: any name you like
# * src: \[FILE; DF; DB (not implemented)\]
# * fpath: required if src == FILE
# * df: required if src == DF
# * check_param: print parameters used for data loading

# In[3]:

# pf.session.load_data(name='hospital', src=FILE, fpath='data/hospital_clean_unflatten.csv', check_param=True, na_values='empty')
pf.session.load_data(name='customer', src=FILE,
                     fpath='data/customer.csv', check_param=True, na_values='empty')


# ### 2.1 Change Data Types of Attributes
# * required input:
#     * a list of attributes
#     * a list of data types (must match the order of the attributes; can be CATEGORICAL, NUMERIC, TEXT, DATE)
# * optional input:
#     * a list of regular expression extractor

# In[4]:

# pf.session.change_dtypes(['ProviderNumber', 'ZipCode', 'PhoneNumber', 'State', 'EmergencyService','Score', 'Sample','HospitalType','HospitalOwner', 'Condition'],
#                             [CATEGORICAL, NUMERIC, CATEGORICAL, TEXT, TEXT, NUMERIC, NUMERIC, TEXT,TEXT, TEXT],
#                             [None, None, None, None, None, r'(\d+)%', r'(\d+)\spatients', None, None,None])
# # pf.session.change_dtypes(['ProviderNumber', 'ZipCode', 'PhoneNumber', 'State', 'EmergencyService','Score', 'Sample'],
# #                             [CATEGORICAL, CATEGORICAL, CATEGORICAL, TEXT, TEXT, NUMERIC, NUMERIC],
# #                             [None, None, None, None, None, r'(\d+)%', r'(\d+)\spatients'])
pf.session.change_dtypes(['c_custkey', 'c_name', 'c_address', 'c_nationkey', 'c_phone', 'c_acctbal', 'c_mktsegment', 'c_comment'],
                         [CATEGORICAL, CATEGORICAL, CATEGORICAL,
                             NUMERIC, CATEGORICAL, NUMERIC, CATEGORICAL, CATEGORICAL],
                         [None, None, None, None, None, None, None, None])

# ### 2.2. Load/Train Embeddings for TEXT
# * path: path to saved/to-save embedding folder
# * load: set to true -- load saved vec from 'path'; set to false -- train locally
# * save: (only for load = False) save trained vectors to 'path'

# In[ ]:

pf.session.load_embedding(save=True, path='data/', load=True)


# ## 3. Load Training Data
# * multiplier: if set to None, will infer the minimal sample size; otherwise, it will create (# samples) * (# attributes) * (multiplier) training samples

# In[ ]:

# use simple empirical cov: difference=False
# use difference -> cov : difference=True
pf.session.load_training_data(multiplier=None, difference=True)


# ## 4. Learn Structure
# * sparsity: intensity of L1-regularizer in inverse covariance estimation (glasso)
# * take_neg: if set to true, consider equal -> equal only

# In[ ]:

# set sparsity to 0 for exp_reproduce
autoregress_matrix = pf.session.learn_structure(sparsity=0, infer_order=True)


# * score:
#     * "fit_error": mse for fitting y = B'X + c for each atttribute y
#     * "training_data_fd_vio_ratio": the higher the score, the more violations of FDs in the training data. (bounded: \[0,1\])

# In[ ]:

parent_sets = pf.session.get_dependencies(score="fit_error")


# In[ ]:


def read_fds(path='data/fds', f='TECHospital-hyfd'):
    all_fds = {}
    for line in open(os.path.join(path, f)):
        fd = json.loads(line)
        right = fd[u'dependant']['columnIdentifier']
        left = [l[u'columnIdentifier']
                for l in fd[u'determinant'][u'columnIdentifiers']]
        if right not in all_fds:
            all_fds[right] = set()
        all_fds[right].add(frozenset(left))
    return all_fds


# In[ ]:

gt = read_fds(f='hospital_clean-fun')


# In[ ]:

tp = 0
count = 0
for child in parent_sets:
    found = parent_sets[child]
    if len(found) == 0:
        continue
    count += 1
    match = False
    for parent in gt[child]:
        if set(parent).issubset(found):
            tp += 1
            match = True
            break
    if not match:
        print("{} -> {} is not valid".format(found, child))
if count > 0:
    print("Precision: %.4f" % (float(tp) / count))


# ## 5. Visualization

# In[ ]:

pf.session.visualize_covariance()


# In[ ]:

pf.session.visualize_inverse_covariance()


# In[ ]:

pf.session.visualize_autoregression()


# In[ ]:

pf.session.timer.get_stat()


# In[ ]:

pf.session.timer.to_csv()


# In[ ]:


# In[ ]: