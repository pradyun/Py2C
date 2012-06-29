__author__ = "Ramchandra Apte <maniandram01@gmail.com>"
__license__ = '''
Copyright (C) 2012 Ramchandra Apte <maniandram01@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License at LICENSE.txt for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import inspect,ast,translator,itertools,python_builtins,collections,tkinter,tkinter.scrolledtext
group_features_done = 0
group_features_count = 0
table = collections.OrderedDict()
def row(tupl,group = False):
    name,status = tupl
    if isinstance(status,tuple):
        status,msg = status
    else:
        msg = None
    return '||{}{}{}||<font color = "{}">{}||'.format("_*" if group else "",name,"*_" if group else "",{True:'green',False:'red',None:'#CCCC00'}[status],{True:"Done",False:"Not Done"}.get(status,msg))
def progress(a,b,features_name):return "{:.0%} Done ({} done and {} not done out of out of {} {})".format(a/b,a,b-a,b,features_name)
def getkey(features_done,features_count,name,features_name):
    return name,(True if features_done == features_count else False if features_done == 0 else None,progress(features_done,features_count,features_name.lower()))
def group_features(features,name):
    global group_features_done,group_features_count
    features = tuple(features)
    features_done = sum(x[1] for x in features)
    features_count = len(features)
    table[getkey(features_done,features_count,name,name.lower())] = features
    group_features_count+=features_count
    group_features_done += features_done
group_features(((name,hasattr(translator.Translator,"visit_"+name) or getattr(ast,name) in translator.opdict) for name in dir(ast) if hasattr(getattr(ast,name),"_fields")),"AST node types")
group_features(((x,hasattr(python_builtins,x)) for x in dir(__builtins__) if not x.startswith("_") and (inspect.isbuiltin(getattr(__builtins__,x)) or (inspect.isclass(getattr(__builtins__,x)) and not issubclass(getattr(__builtins__,x),BaseException)))),"Functions")
i = getkey(group_features_done,group_features_count,"<h1> 0.1","items")
table[i] = ()
table.move_to_end(i,False)
text = tkinter.scrolledtext.ScrolledText()
#text.config(state = "disabled")
text.insert(tkinter.END,"\n".join(row((group_name,group_status),group = True)+("\n" if group_table else "")+"\n".join(map(row,group_table)) for (group_name,group_status),group_table in table.items()))
text.pack()
text.mainloop()
