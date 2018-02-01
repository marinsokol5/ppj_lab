import fileinput
import lab2_python.source.Util as util
import pickle
fileinput_gen = fileinput.input()
with open('/home/marin/ppj/lab2_python/source/lr_table.pkl', 'rb') as handle:
    lr_table = pickle.load(handle)
util.lr_parse(lr_table=lr_table, fileinput_gen=fileinput_gen, file='/home/marin/ppj/lab2_python/test/kanon_gramatika.mine', synchornizing_sings={'TOCKAZAREZ', 'D_VIT_ZAGRADA'})