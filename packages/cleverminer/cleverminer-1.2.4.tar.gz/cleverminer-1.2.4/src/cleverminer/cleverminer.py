import sys #line:1
import time #line:2
import copy #line:3
import inspect #line:4
from time import strftime #line:6
from time import gmtime #line:7
import pandas as pd #line:9
import numpy as np #line:10
from pandas .api .types import CategoricalDtype #line:11
import progressbar #line:12
import re #line:13
from textwrap import wrap #line:14
import seaborn as sns #line:15
import matplotlib .pyplot as plt #line:16
import re #line:17
import pickle #line:18
import json #line:19
import hashlib #line:20
from datetime import datetime #line:21
import tempfile #line:22
import os #line:23
import urllib #line:24
class cleverminer :#line:26
    version_string ="1.2.4"#line:28
    temppath =tempfile .gettempdir ()#line:30
    cache_dir =os .path .join (temppath ,'clm_cache')#line:31
    def __init__ (OOOOO00OO0OO00O00 ,**OOO00OO00O0000O0O ):#line:33
        ""#line:62
        OOOOO00OO0OO00O00 ._print_disclaimer ()#line:63
        OOOOO00OO0OO00O00 .use_cache =False #line:64
        OOOOO00OO0OO00O00 .cache_also_data =True #line:65
        OOOOO00OO0OO00O00 .stats ={'total_cnt':0 ,'total_ver':0 ,'total_valid':0 ,'control_number':0 ,'start_prep_time':time .time (),'end_prep_time':time .time (),'start_proc_time':time .time (),'end_proc_time':time .time ()}#line:74
        OOOOO00OO0OO00O00 .options ={'max_categories':100 ,'max_rules':None ,'optimizations':True ,'automatic_data_conversions':True ,'progressbar':True ,'keep_df':False }#line:82
        OOOOO00OO0OO00O00 .df =None #line:83
        OOOOO00OO0OO00O00 .kwargs =None #line:84
        if len (OOO00OO00O0000O0O )>0 :#line:85
            OOOOO00OO0OO00O00 .kwargs =OOO00OO00O0000O0O #line:86
        OOOOO00OO0OO00O00 .profiles ={}#line:87
        OOOOO00OO0OO00O00 .verbosity ={}#line:88
        OOOOO00OO0OO00O00 .verbosity ['debug']=False #line:89
        OOOOO00OO0OO00O00 .verbosity ['print_rules']=False #line:90
        OOOOO00OO0OO00O00 .verbosity ['print_hashes']=True #line:91
        OOOOO00OO0OO00O00 .verbosity ['last_hash_time']=0 #line:92
        OOOOO00OO0OO00O00 .verbosity ['hint']=False #line:93
        if "opts"in OOO00OO00O0000O0O :#line:94
            OOOOO00OO0OO00O00 ._set_opts (OOO00OO00O0000O0O .get ("opts"))#line:95
        if "opts"in OOO00OO00O0000O0O :#line:96
            OOO000OO0OO00O00O =OOO00OO00O0000O0O ['opts']#line:97
            if 'use_cache'in OOO000OO0OO00O00O :#line:98
                OOOOO00OO0OO00O00 .use_cache =OOO000OO0OO00O00O ['use_cache']#line:99
            if 'cache_also_data'in OOO000OO0OO00O00O :#line:100
                OOOOO00OO0OO00O00 .cache_also_data =OOO000OO0OO00O00O ['cache_also_data']#line:101
            if "verbose"in OOO00OO00O0000O0O .get ('opts'):#line:102
                OO00O0OOO0O0OOOO0 =OOO00OO00O0000O0O .get ('opts').get ('verbose')#line:103
                if OO00O0OOO0O0OOOO0 .upper ()=='FULL':#line:104
                    OOOOO00OO0OO00O00 .verbosity ['debug']=True #line:105
                    OOOOO00OO0OO00O00 .verbosity ['print_rules']=True #line:106
                    OOOOO00OO0OO00O00 .verbosity ['print_hashes']=False #line:107
                    OOOOO00OO0OO00O00 .verbosity ['hint']=True #line:108
                    OOOOO00OO0OO00O00 .options ['progressbar']=False #line:109
                elif OO00O0OOO0O0OOOO0 .upper ()=='RULES':#line:110
                    OOOOO00OO0OO00O00 .verbosity ['debug']=False #line:111
                    OOOOO00OO0OO00O00 .verbosity ['print_rules']=True #line:112
                    OOOOO00OO0OO00O00 .verbosity ['print_hashes']=True #line:113
                    OOOOO00OO0OO00O00 .verbosity ['hint']=True #line:114
                    OOOOO00OO0OO00O00 .options ['progressbar']=False #line:115
                elif OO00O0OOO0O0OOOO0 .upper ()=='HINT':#line:116
                    OOOOO00OO0OO00O00 .verbosity ['debug']=False #line:117
                    OOOOO00OO0OO00O00 .verbosity ['print_rules']=False #line:118
                    OOOOO00OO0OO00O00 .verbosity ['print_hashes']=True #line:119
                    OOOOO00OO0OO00O00 .verbosity ['last_hash_time']=0 #line:120
                    OOOOO00OO0OO00O00 .verbosity ['hint']=True #line:121
                    OOOOO00OO0OO00O00 .options ['progressbar']=False #line:122
                elif OO00O0OOO0O0OOOO0 .upper ()=='DEBUG':#line:123
                    OOOOO00OO0OO00O00 .verbosity ['debug']=True #line:124
                    OOOOO00OO0OO00O00 .verbosity ['print_rules']=True #line:125
                    OOOOO00OO0OO00O00 .verbosity ['print_hashes']=True #line:126
                    OOOOO00OO0OO00O00 .verbosity ['last_hash_time']=0 #line:127
                    OOOOO00OO0OO00O00 .verbosity ['hint']=True #line:128
                    OOOOO00OO0OO00O00 .options ['progressbar']=False #line:129
        if "load"in OOO00OO00O0000O0O :#line:132
            if OOOOO00OO0OO00O00 .use_cache :#line:134
                OOOOO00OO0OO00O00 .use_cache =False #line:135
        OOO0O0OOO000OOO00 =copy .deepcopy (OOO00OO00O0000O0O )#line:136
        if 'df'in OOO0O0OOO000OOO00 :#line:137
            OOO0O0OOO000OOO00 ['df']=OOO0O0OOO000OOO00 ['df'].to_json ()#line:138
        OO0OOO00O0OO00O0O =OOOOO00OO0OO00O00 ._get_hash (OOO0O0OOO000OOO00 )#line:139
        OOOOO00OO0OO00O00 .guid =OO0OOO00O0OO00O0O #line:140
        if OOOOO00OO0OO00O00 .use_cache :#line:141
            if not (os .path .isdir (OOOOO00OO0OO00O00 .cache_dir )):#line:142
                os .mkdir (OOOOO00OO0OO00O00 .cache_dir )#line:143
            OOOOO00OO0OO00O00 .cache_fname =os .path .join (OOOOO00OO0OO00O00 .cache_dir ,OO0OOO00O0OO00O0O +'.clm')#line:144
            if os .path .isfile (OOOOO00OO0OO00O00 .cache_fname ):#line:145
                print (f"Will use cached file {OOOOO00OO0OO00O00.cache_fname}")#line:146
                OOOOO00O000000O00 ='pickle'#line:147
                if "fmt"in OOO00OO00O0000O0O :#line:148
                    OOOOO00O000000O00 =OOO00OO00O0000O0O .get ('fmt')#line:149
                OOOOO00OO0OO00O00 .load (OOOOO00OO0OO00O00 .cache_fname ,fmt =OOOOO00O000000O00 )#line:150
                return #line:151
            print (f"Task {OO0OOO00O0OO00O0O} not in cache, will calculate it.")#line:152
        OOOOO00OO0OO00O00 ._is_py310 =sys .version_info [0 ]>=4 or (sys .version_info [0 ]>=3 and sys .version_info [1 ]>=10 )#line:154
        if not (OOOOO00OO0OO00O00 ._is_py310 ):#line:155
            print ("Warning: Python 3.10+ NOT detected. You should upgrade to Python 3.10 or greater to get better performance")#line:156
        else :#line:157
            if (OOOOO00OO0OO00O00 .verbosity ['debug']):#line:158
                print ("Python 3.10+ detected.")#line:159
        OOOOO00OO0OO00O00 ._initialized =False #line:160
        if "load"in OOO00OO00O0000O0O :#line:161
            OOOOO00O000000O00 ='pickle'#line:162
            if "fmt"in OOO00OO00O0000O0O :#line:163
                OOOOO00O000000O00 =OOO00OO00O0000O0O .get ('fmt')#line:164
            OOOOO00OO0OO00O00 .load (filename =OOO00OO00O0000O0O .get ('load'),fmt =OOOOO00O000000O00 )#line:165
            return #line:166
        OOOOO00OO0OO00O00 ._init_data ()#line:167
        OOOOO00OO0OO00O00 ._init_task ()#line:168
        if len (OOO00OO00O0000O0O )>0 :#line:169
            if "df"in OOO00OO00O0000O0O :#line:170
                OOOOO00OO0OO00O00 ._prep_data (OOO00OO00O0000O0O .get ("df"))#line:171
            else :#line:172
                print ("Missing dataframe. Cannot initialize.")#line:173
                OOOOO00OO0OO00O00 ._initialized =False #line:174
                return #line:175
            OO000O0000000OO00 =OOO00OO00O0000O0O .get ("proc",None )#line:176
            if not (OO000O0000000OO00 ==None ):#line:177
                OOOOO00OO0OO00O00 ._calculate (**OOO00OO00O0000O0O )#line:178
            else :#line:179
                if OOOOO00OO0OO00O00 .verbosity ['debug']:#line:180
                    print ("INFO: just initialized")#line:181
                O00O0OO0000O00000 ={}#line:182
                OO00O0OO00O0O0O0O ={}#line:183
                OO00O0OO00O0O0O0O ["varname"]=OOOOO00OO0OO00O00 .data ["varname"]#line:184
                OO00O0OO00O0O0O0O ["catnames"]=OOOOO00OO0OO00O00 .data ["catnames"]#line:185
                O00O0OO0000O00000 ["datalabels"]=OO00O0OO00O0O0O0O #line:186
                OOOOO00OO0OO00O00 .result =O00O0OO0000O00000 #line:187
        OOOOO00OO0OO00O00 ._initialized =True #line:189
        if OOOOO00OO0OO00O00 .use_cache :#line:190
            OOOOO00OO0OO00O00 .save (OOOOO00OO0OO00O00 .cache_fname ,savedata =OOOOO00OO0OO00O00 .cache_also_data ,embeddata =False )#line:191
            print (f"CACHE: results cache saved into {OOOOO00OO0OO00O00.cache_fname}")#line:192
    def _get_hash (O00O0O0OO00OO0OO0 ,OOOO00OO00OOOOO0O ):#line:195
        class O0OO0O0000OO000OO (json .JSONEncoder ):#line:197
            def default (O0OOOO00OO0O000O0 ,O0OO0O0O0O00OOOO0 ):#line:198
                if isinstance (O0OO0O0O0O00OOOO0 ,np .integer ):#line:199
                    return int (O0OO0O0O0O00OOOO0 )#line:200
                if isinstance (O0OO0O0O0O00OOOO0 ,np .floating ):#line:201
                    return float (O0OO0O0O0O00OOOO0 )#line:202
                if isinstance (O0OO0O0O0O00OOOO0 ,np .ndarray ):#line:203
                    return O0OO0O0O0O00OOOO0 .tolist ()#line:204
                if callable (O0OO0O0O0O00OOOO0 ):#line:205
                    return time .time ()#line:207
                return super (O0OO0O0000OO000OO ,O0OOOO00OO0O000O0 ).default (O0OO0O0O0O00OOOO0 )#line:209
        OOO0O00O000OO0OOO =hashlib .sha256 (json .dumps (OOOO00OO00OOOOO0O ,sort_keys =True ,cls =O0OO0O0000OO000OO ).encode ('utf-8')).hexdigest ()#line:211
        return OOO0O00O000OO0OOO #line:212
    def _get_fast_hash (OOOOOOO0OOO0O000O ,OOOO0O00OO00OO0O0 ):#line:215
        OO0O0O0OOO0OO0O0O =pickle .dumps (OOOO0O00OO00OO0O0 )#line:216
        print (f"...CALC THE HASH {datetime.now()}")#line:217
        OOOO00OOO00O00OO0 =hashlib .md5 (OO0O0O0OOO0OO0O0O ).hexdigest ()#line:218
        return OOOO00OOO00O00OO0 #line:219
    def _set_opts (OOO0O000O000OO0O0 ,OO0OOOO0O0O0O0OO0 ):#line:221
        if "no_optimizations"in OO0OOOO0O0O0O0OO0 :#line:222
            OOO0O000O000OO0O0 .options ['optimizations']=not (OO0OOOO0O0O0O0OO0 ['no_optimizations'])#line:223
            print ("No optimization will be made.")#line:224
        if "disable_progressbar"in OO0OOOO0O0O0O0OO0 :#line:225
            OOO0O000O000OO0O0 .options ['progressbar']=False #line:226
            print ("Progressbar will not be shown.")#line:227
        if "max_rules"in OO0OOOO0O0O0O0OO0 :#line:228
            OOO0O000O000OO0O0 .options ['max_rules']=OO0OOOO0O0O0O0OO0 ['max_rules']#line:229
        if "max_categories"in OO0OOOO0O0O0O0OO0 :#line:230
            OOO0O000O000OO0O0 .options ['max_categories']=OO0OOOO0O0O0O0OO0 ['max_categories']#line:231
            if OOO0O000O000OO0O0 .verbosity ['debug']==True :#line:232
                print (f"Maximum number of categories set to {OOO0O000O000OO0O0.options['max_categories']}")#line:233
        if "no_automatic_data_conversions"in OO0OOOO0O0O0O0OO0 :#line:234
            OOO0O000O000OO0O0 .options ['automatic_data_conversions']=not (OO0OOOO0O0O0O0OO0 ['no_automatic_data_conversions'])#line:235
            print ("No automatic data conversions will be made.")#line:236
        if "keep_df"in OO0OOOO0O0O0O0OO0 :#line:237
            OOO0O000O000OO0O0 .options ['keep_df']=OO0OOOO0O0O0O0OO0 ['keep_df']#line:238
    def _init_data (O00OO0OOOOO000OO0 ):#line:241
        O00OO0OOOOO000OO0 .data ={}#line:243
        O00OO0OOOOO000OO0 .data ["varname"]=[]#line:244
        O00OO0OOOOO000OO0 .data ["catnames"]=[]#line:245
        O00OO0OOOOO000OO0 .data ["vtypes"]=[]#line:246
        O00OO0OOOOO000OO0 .data ["dm"]=[]#line:247
        O00OO0OOOOO000OO0 .data ["rows_count"]=int (0 )#line:248
        O00OO0OOOOO000OO0 .data ["data_prepared"]=0 #line:249
    def _init_task (O0O0O0O0O0O000000 ):#line:251
        if "opts"in O0O0O0O0O0O000000 .kwargs :#line:253
            O0O0O0O0O0O000000 ._set_opts (O0O0O0O0O0O000000 .kwargs .get ("opts"))#line:254
        O0O0O0O0O0O000000 .cedent ={'cedent_type':'none','defi':{},'num_cedent':0 ,'trace_cedent':[],'trace_cedent_asindata':[],'traces':[],'generated_string':'','rule':{},'filter_value':int (0 )}#line:264
        O0O0O0O0O0O000000 .task_actinfo ={'proc':'','cedents_to_do':[],'cedents':[]}#line:268
        O0O0O0O0O0O000000 .rulelist =[]#line:269
        O0O0O0O0O0O000000 .stats ['total_cnt']=0 #line:270
        O0O0O0O0O0O000000 .stats ['total_valid']=0 #line:271
        O0O0O0O0O0O000000 .stats ['control_number']=0 #line:272
        O0O0O0O0O0O000000 .result ={}#line:273
        O0O0O0O0O0O000000 ._opt_base =None #line:274
        O0O0O0O0O0O000000 ._opt_relbase =None #line:275
        O0O0O0O0O0O000000 ._opt_base1 =None #line:276
        O0O0O0O0O0O000000 ._opt_relbase1 =None #line:277
        O0O0O0O0O0O000000 ._opt_base2 =None #line:278
        O0O0O0O0O0O000000 ._opt_relbase2 =None #line:279
        O0OO00OOO000O00OO =None #line:280
        if not (O0O0O0O0O0O000000 .kwargs ==None ):#line:281
            O0OO00OOO000O00OO =O0O0O0O0O0O000000 .kwargs .get ("quantifiers",None )#line:282
            if not (O0OO00OOO000O00OO ==None ):#line:283
                for OO00O0OO0O00OOO00 in O0OO00OOO000O00OO .keys ():#line:284
                    if OO00O0OO0O00OOO00 .upper ()=='BASE':#line:285
                        O0O0O0O0O0O000000 ._opt_base =O0OO00OOO000O00OO .get (OO00O0OO0O00OOO00 )#line:286
                    if OO00O0OO0O00OOO00 .upper ()=='RELBASE':#line:287
                        O0O0O0O0O0O000000 ._opt_relbase =O0OO00OOO000O00OO .get (OO00O0OO0O00OOO00 )#line:288
                    if (OO00O0OO0O00OOO00 .upper ()=='FRSTBASE')|(OO00O0OO0O00OOO00 .upper ()=='BASE1'):#line:289
                        O0O0O0O0O0O000000 ._opt_base1 =O0OO00OOO000O00OO .get (OO00O0OO0O00OOO00 )#line:290
                    if (OO00O0OO0O00OOO00 .upper ()=='SCNDBASE')|(OO00O0OO0O00OOO00 .upper ()=='BASE2'):#line:291
                        O0O0O0O0O0O000000 ._opt_base2 =O0OO00OOO000O00OO .get (OO00O0OO0O00OOO00 )#line:292
                    if (OO00O0OO0O00OOO00 .upper ()=='FRSTRELBASE')|(OO00O0OO0O00OOO00 .upper ()=='RELBASE1'):#line:293
                        O0O0O0O0O0O000000 ._opt_relbase1 =O0OO00OOO000O00OO .get (OO00O0OO0O00OOO00 )#line:294
                    if (OO00O0OO0O00OOO00 .upper ()=='SCNDRELBASE')|(OO00O0OO0O00OOO00 .upper ()=='RELBASE2'):#line:295
                        O0O0O0O0O0O000000 ._opt_relbase2 =O0OO00OOO000O00OO .get (OO00O0OO0O00OOO00 )#line:296
            else :#line:297
                print ("Warning: no quantifiers found. Optimization will not take place (1)")#line:298
        else :#line:299
            print ("Warning: no quantifiers found. Optimization will not take place (2)")#line:300
    def mine (O0O0O00000OOO0OO0 ,**O0000O0OO0OOO00O0 ):#line:303
        ""#line:308
        if not (O0O0O00000OOO0OO0 ._initialized ):#line:309
            print ("Class NOT INITIALIZED. Please call constructor with dataframe first")#line:310
            return #line:311
        O0O0O00000OOO0OO0 .kwargs =None #line:312
        if len (O0000O0OO0OOO00O0 )>0 :#line:313
            O0O0O00000OOO0OO0 .kwargs =O0000O0OO0OOO00O0 #line:314
        O0O0O00000OOO0OO0 ._init_task ()#line:315
        if len (O0000O0OO0OOO00O0 )>0 :#line:316
            OO0O0000O0OOO0O00 =O0000O0OO0OOO00O0 .get ("proc",None )#line:317
            if not (OO0O0000O0OOO0O00 ==None ):#line:318
                O0O0O00000OOO0OO0 ._calc_all (**O0000O0OO0OOO00O0 )#line:319
            else :#line:320
                print ("Rule mining procedure missing")#line:321
    def _get_ver (OOO000O00OO00OOO0 ):#line:324
        return OOO000O00OO00OOO0 .version_string #line:325
    def _print_disclaimer (OO000O0OO0O000O00 ):#line:327
        print (f"Cleverminer version {OO000O0OO0O000O00._get_ver()}.")#line:328
    def _automatic_data_conversions (OO0O00OOO0OO0OOOO ,OOOO0O00O0000OOOO ):#line:329
        print ("Automatically reordering numeric categories ...")#line:330
        for O00O00O000OO00OOO in range (len (OOOO0O00O0000OOOO .columns )):#line:331
            if OO0O00OOO0OO0OOOO .verbosity ['debug']:#line:332
                print (f"#{O00O00O000OO00OOO}: {OOOO0O00O0000OOOO.columns[O00O00O000OO00OOO]} : {OOOO0O00O0000OOOO.dtypes[O00O00O000OO00OOO]}.")#line:333
            try :#line:334
                OOOO0O00O0000OOOO [OOOO0O00O0000OOOO .columns [O00O00O000OO00OOO ]]=OOOO0O00O0000OOOO [OOOO0O00O0000OOOO .columns [O00O00O000OO00OOO ]].astype (str ).astype (float )#line:335
                if OO0O00OOO0OO0OOOO .verbosity ['debug']:#line:336
                    print (f"CONVERTED TO FLOATS #{O00O00O000OO00OOO}: {OOOO0O00O0000OOOO.columns[O00O00O000OO00OOO]} : {OOOO0O00O0000OOOO.dtypes[O00O00O000OO00OOO]}.")#line:337
                O0OOO0O00OO00O000 =pd .unique (OOOO0O00O0000OOOO [OOOO0O00O0000OOOO .columns [O00O00O000OO00OOO ]])#line:338
                OOOO000OOO00O0O0O =True #line:339
                for OOOOO00O0OO0O0O00 in O0OOO0O00OO00O000 :#line:340
                    if OOOOO00O0OO0O0O00 %1 !=0 :#line:341
                        OOOO000OOO00O0O0O =False #line:342
                if OOOO000OOO00O0O0O :#line:343
                    OOOO0O00O0000OOOO [OOOO0O00O0000OOOO .columns [O00O00O000OO00OOO ]]=OOOO0O00O0000OOOO [OOOO0O00O0000OOOO .columns [O00O00O000OO00OOO ]].astype (int )#line:344
                    if OO0O00OOO0OO0OOOO .verbosity ['debug']:#line:345
                        print (f"CONVERTED TO INT #{O00O00O000OO00OOO}: {OOOO0O00O0000OOOO.columns[O00O00O000OO00OOO]} : {OOOO0O00O0000OOOO.dtypes[O00O00O000OO00OOO]}.")#line:346
                OO00OOOO0O000OO00 =pd .unique (OOOO0O00O0000OOOO [OOOO0O00O0000OOOO .columns [O00O00O000OO00OOO ]])#line:347
                OO0O00OO0OOO0O0O0 =CategoricalDtype (categories =OO00OOOO0O000OO00 .sort (),ordered =True )#line:348
                OOOO0O00O0000OOOO [OOOO0O00O0000OOOO .columns [O00O00O000OO00OOO ]]=OOOO0O00O0000OOOO [OOOO0O00O0000OOOO .columns [O00O00O000OO00OOO ]].astype (OO0O00OO0OOO0O0O0 )#line:349
                if OO0O00OOO0OO0OOOO .verbosity ['debug']:#line:350
                    print (f"CONVERTED TO CATEGORY #{O00O00O000OO00OOO}: {OOOO0O00O0000OOOO.columns[O00O00O000OO00OOO]} : {OOOO0O00O0000OOOO.dtypes[O00O00O000OO00OOO]}.")#line:351
            except :#line:353
                if OO0O00OOO0OO0OOOO .verbosity ['debug']:#line:354
                    print ("...cannot be converted to int")#line:355
                try :#line:356
                    O0O00000OOOOO0OO0 =OOOO0O00O0000OOOO [OOOO0O00O0000OOOO .columns [O00O00O000OO00OOO ]].unique ()#line:357
                    if OO0O00OOO0OO0OOOO .verbosity ['debug']:#line:358
                        print (f"Values: {O0O00000OOOOO0OO0}")#line:359
                    O00OO00000O000O00 =True #line:360
                    OO00OOOO000OO0000 =[]#line:361
                    for OOOOO00O0OO0O0O00 in O0O00000OOOOO0OO0 :#line:362
                        OOOOO00OOOO0O00O0 =re .findall (r"-?\d+",OOOOO00O0OO0O0O00 )#line:363
                        if len (OOOOO00OOOO0O00O0 )>0 :#line:364
                            OO00OOOO000OO0000 .append (int (OOOOO00OOOO0O00O0 [0 ]))#line:365
                        else :#line:366
                            O00OO00000O000O00 =False #line:367
                    if OO0O00OOO0OO0OOOO .verbosity ['debug']:#line:368
                        print (f"Is ok: {O00OO00000O000O00}, extracted {OO00OOOO000OO0000}")#line:369
                    if O00OO00000O000O00 :#line:370
                        OOO0O0O0OOOOOOOOO =copy .deepcopy (OO00OOOO000OO0000 )#line:371
                        OOO0O0O0OOOOOOOOO .sort ()#line:372
                        O00OO00OOO0000000 =[]#line:373
                        for OOOO00O00OOOO0000 in OOO0O0O0OOOOOOOOO :#line:374
                            O000OO000000OO000 =OO00OOOO000OO0000 .index (OOOO00O00OOOO0000 )#line:375
                            O00OO00OOO0000000 .append (O0O00000OOOOO0OO0 [O000OO000000OO000 ])#line:376
                        if OO0O00OOO0OO0OOOO .verbosity ['debug']:#line:377
                            print (f"Sorted list: {O00OO00OOO0000000}")#line:378
                        OO0O00OO0OOO0O0O0 =CategoricalDtype (categories =O00OO00OOO0000000 ,ordered =True )#line:379
                        OOOO0O00O0000OOOO [OOOO0O00O0000OOOO .columns [O00O00O000OO00OOO ]]=OOOO0O00O0000OOOO [OOOO0O00O0000OOOO .columns [O00O00O000OO00OOO ]].astype (OO0O00OO0OOO0O0O0 )#line:380
                except :#line:381
                    if OO0O00OOO0OO0OOOO .verbosity ['debug']:#line:382
                        print ("...cannot extract numbers from all categories")#line:383
        print ("Automatically reordering numeric categories ...done")#line:385
    def _prep_data (O000OOO0OOOOOO0OO ,OO0000OOOO0O00O00 ):#line:387
        print ("Starting data preparation ...")#line:388
        O000OOO0OOOOOO0OO ._init_data ()#line:389
        O000OOO0OOOOOO0OO .stats ['start_prep_time']=time .time ()#line:390
        if O000OOO0OOOOOO0OO .options ['automatic_data_conversions']:#line:391
            O000OOO0OOOOOO0OO ._automatic_data_conversions (OO0000OOOO0O00O00 )#line:392
        O000OOO0OOOOOO0OO .data ["rows_count"]=OO0000OOOO0O00O00 .shape [0 ]#line:393
        for O0OO0OO000O0OOOOO in OO0000OOOO0O00O00 .select_dtypes (exclude =['category']).columns :#line:394
            OO0000OOOO0O00O00 [O0OO0OO000O0OOOOO ]=OO0000OOOO0O00O00 [O0OO0OO000O0OOOOO ].apply (str )#line:395
        try :#line:396
            OO0O00OOO000OO00O =pd .DataFrame .from_records ([(O000O0O0OO0000OO0 ,OO0000OOOO0O00O00 [O000O0O0OO0000OO0 ].nunique ())for O000O0O0OO0000OO0 in OO0000OOOO0O00O00 .columns ],columns =['Column_Name','Num_Unique']).sort_values (by =['Num_Unique'])#line:398
        except :#line:399
            print ("Error in input data, probably unsupported data type. Will try to scan for column with unsupported type.")#line:400
            O000O0O000O0OO000 =""#line:401
            try :#line:402
                for O0OO0OO000O0OOOOO in OO0000OOOO0O00O00 .columns :#line:403
                    O000O0O000O0OO000 =O0OO0OO000O0OOOOO #line:404
                    print (f"...column {O0OO0OO000O0OOOOO} has {int(OO0000OOOO0O00O00[O0OO0OO000O0OOOOO].nunique())} values")#line:405
            except :#line:406
                print (f"... detected : column {O000O0O000O0OO000} has unsupported type: {type(OO0000OOOO0O00O00[O0OO0OO000O0OOOOO])}.")#line:407
                exit (1 )#line:408
            print (f"Error in data profiling - attribute with unsupported type not detected. Please profile attributes manually, only simple attributes are supported.")#line:409
            exit (1 )#line:410
        if O000OOO0OOOOOO0OO .verbosity ['hint']:#line:413
            print ("Quick profile of input data: unique value counts are:")#line:414
            print (OO0O00OOO000OO00O )#line:415
            for O0OO0OO000O0OOOOO in OO0000OOOO0O00O00 .columns :#line:416
                if OO0000OOOO0O00O00 [O0OO0OO000O0OOOOO ].nunique ()<O000OOO0OOOOOO0OO .options ['max_categories']:#line:417
                    OO0000OOOO0O00O00 [O0OO0OO000O0OOOOO ]=OO0000OOOO0O00O00 [O0OO0OO000O0OOOOO ].astype ('category')#line:418
                else :#line:419
                    print (f"WARNING: attribute {O0OO0OO000O0OOOOO} has more than {O000OOO0OOOOOO0OO.options['max_categories']} values, will be ignored.\r\n If you haven't set maximum number of categories and you really need more categories and you know what you are doing, please use max_categories option to increase allowed number of categories.")#line:420
                    del OO0000OOOO0O00O00 [O0OO0OO000O0OOOOO ]#line:421
        for O0OO0OO000O0OOOOO in OO0000OOOO0O00O00 .columns :#line:423
            if OO0000OOOO0O00O00 [O0OO0OO000O0OOOOO ].nunique ()>O000OOO0OOOOOO0OO .options ['max_categories']:#line:424
                print (f"WARNING: attribute {O0OO0OO000O0OOOOO} has more than {O000OOO0OOOOOO0OO.options['max_categories']} values, will be ignored.\r\n If you haven't set maximum number of categories and you really need more categories and you know what you are doing, please use max_categories option to increase allowed number of categories.")#line:425
                del OO0000OOOO0O00O00 [O0OO0OO000O0OOOOO ]#line:426
        if O000OOO0OOOOOO0OO .options ['keep_df']:#line:427
            if O000OOO0OOOOOO0OO .verbosity ['debug']:#line:428
                print ("Keeping df.")#line:429
            O000OOO0OOOOOO0OO .df =OO0000OOOO0O00O00 #line:430
        print ("Encoding columns into bit-form...")#line:431
        O000OOO0O0OOO0OO0 =0 #line:432
        O0OOO00O0000OO00O =0 #line:433
        for O00O000000OOO0O0O in OO0000OOOO0O00O00 :#line:434
            if O000OOO0OOOOOO0OO .verbosity ['debug']:#line:435
                print ('Column: '+O00O000000OOO0O0O +' @ '+str (time .time ()))#line:436
            if O000OOO0OOOOOO0OO .verbosity ['debug']:#line:437
                print ('Column: '+O00O000000OOO0O0O )#line:438
            O000OOO0OOOOOO0OO .data ["varname"].append (O00O000000OOO0O0O )#line:439
            O0OOOO0O0OO00OOO0 =pd .get_dummies (OO0000OOOO0O00O00 [O00O000000OOO0O0O ])#line:440
            O000O0OO0000OOOO0 =0 #line:441
            if (OO0000OOOO0O00O00 .dtypes [O00O000000OOO0O0O ].name =='category'):#line:442
                O000O0OO0000OOOO0 =1 #line:443
            O000OOO0OOOOOO0OO .data ["vtypes"].append (O000O0OO0000OOOO0 )#line:444
            if O000OOO0OOOOOO0OO .verbosity ['debug']:#line:445
                print (O0OOOO0O0OO00OOO0 )#line:446
                print (OO0000OOOO0O00O00 [O00O000000OOO0O0O ])#line:447
            O0OO0O000O0O00O0O =0 #line:448
            OO0O0O0OO00O00O0O =[]#line:449
            O0OOOOO0OO00O0OO0 =[]#line:450
            if O000OOO0OOOOOO0OO .verbosity ['debug']:#line:451
                print ('...starting categories '+str (time .time ()))#line:452
            for OO000O00OOO00OOOO in O0OOOO0O0OO00OOO0 :#line:453
                if O000OOO0OOOOOO0OO .verbosity ['debug']:#line:454
                    print ('....category : '+str (OO000O00OOO00OOOO )+' @ '+str (time .time ()))#line:455
                OO0O0O0OO00O00O0O .append (OO000O00OOO00OOOO )#line:456
                OO000OOO0O0OO00O0 =int (0 )#line:457
                OO000O00OO0OO00OO =O0OOOO0O0OO00OOO0 [OO000O00OOO00OOOO ].values #line:458
                if O000OOO0OOOOOO0OO .verbosity ['debug']:#line:459
                    print (OO000O00OO0OO00OO .ndim )#line:460
                OOO0OO0OOO000O0OO =np .packbits (OO000O00OO0OO00OO ,bitorder ='little')#line:461
                OO000OOO0O0OO00O0 =int .from_bytes (OOO0OO0OOO000O0OO ,byteorder ='little')#line:462
                O0OOOOO0OO00O0OO0 .append (OO000OOO0O0OO00O0 )#line:463
                if O000OOO0OOOOOO0OO .verbosity ['debug']:#line:465
                    for OO00000O000000O0O in range (O000OOO0OOOOOO0OO .data ["rows_count"]):#line:467
                        if OO000O00OO0OO00OO [OO00000O000000O0O ]>0 :#line:468
                            OO000OOO0O0OO00O0 +=1 <<OO00000O000000O0O #line:469
                            O0OOOOO0OO00O0OO0 .append (OO000OOO0O0OO00O0 )#line:470
                    print ('....category ATTEMPT 2: '+str (OO000O00OOO00OOOO )+" @ "+str (time .time ()))#line:473
                    O0000O0O0O0O00O00 =int (0 )#line:474
                    OOO0O00OOO0OOO000 =int (1 )#line:475
                    for OO00000O000000O0O in range (O000OOO0OOOOOO0OO .data ["rows_count"]):#line:476
                        if OO000O00OO0OO00OO [OO00000O000000O0O ]>0 :#line:477
                            O0000O0O0O0O00O00 +=OOO0O00OOO0OOO000 #line:478
                            OOO0O00OOO0OOO000 *=2 #line:479
                            OOO0O00OOO0OOO000 =OOO0O00OOO0OOO000 <<1 #line:480
                            print (str (OO000OOO0O0OO00O0 ==O0000O0O0O0O00O00 )+" @ "+str (time .time ()))#line:481
                O0OO0O000O0O00O0O +=1 #line:482
                O0OOO00O0000OO00O +=1 #line:483
                if O000OOO0OOOOOO0OO .verbosity ['debug']:#line:484
                    print (OO0O0O0OO00O00O0O )#line:485
            O000OOO0OOOOOO0OO .data ["catnames"].append (OO0O0O0OO00O00O0O )#line:486
            O000OOO0OOOOOO0OO .data ["dm"].append (O0OOOOO0OO00O0OO0 )#line:487
        print ("Encoding columns into bit-form...done")#line:489
        if O000OOO0OOOOOO0OO .verbosity ['hint']:#line:490
            print (f"List of attributes for analysis is: {O000OOO0OOOOOO0OO.data['varname']}")#line:491
            print (f"List of category names for individual attributes is : {O000OOO0OOOOOO0OO.data['catnames']}")#line:492
        if O000OOO0OOOOOO0OO .verbosity ['debug']:#line:493
            print (f"List of vtypes is (all should be 1) : {O000OOO0OOOOOO0OO.data['vtypes']}")#line:494
        O000OOO0OOOOOO0OO .data ["data_prepared"]=1 #line:495
        print ("Data preparation finished.")#line:496
        if O000OOO0OOOOOO0OO .verbosity ['debug']:#line:497
            print ('Number of variables : '+str (len (O000OOO0OOOOOO0OO .data ["dm"])))#line:498
            print ('Total number of categories in all variables : '+str (O0OOO00O0000OO00O ))#line:499
        O000OOO0OOOOOO0OO .stats ['end_prep_time']=time .time ()#line:500
        if O000OOO0OOOOOO0OO .verbosity ['debug']:#line:501
            print ('Time needed for data preparation : ',str (O000OOO0OOOOOO0OO .stats ['end_prep_time']-O000OOO0OOOOOO0OO .stats ['start_prep_time']))#line:502
    def _bitcount (O00OO00O0O000OOOO ,O0O00OOOOOO0000O0 ):#line:504
        O000OO0O00O0OO0O0 =None #line:505
        if (O00OO00O0O000OOOO ._is_py310 ):#line:506
            O000OO0O00O0OO0O0 =O0O00OOOOOO0000O0 .bit_count ()#line:507
        else :#line:508
            O000OO0O00O0OO0O0 =bin (O0O00OOOOOO0000O0 ).count ("1")#line:509
        return O000OO0O00O0OO0O0 #line:510
    def _verifyCF (OOOO0000O0OO000O0 ,_O0OOOO00O0O0O0OOO ):#line:513
        OOOOOOO00OO0000OO =OOOO0000O0OO000O0 ._bitcount (_O0OOOO00O0O0O0OOO )#line:514
        OOOOOOOO0OOOO00OO =[]#line:515
        OO0OO0000OO0OOOO0 =[]#line:516
        O0OO0O0O000O00000 =0 #line:517
        OO0OO0O0OOO00O0OO =0 #line:518
        O0OOOO00OOOOOOO00 =0 #line:519
        O00OO000O0O0OO0O0 =0 #line:520
        OO000OOOO000O000O =0 #line:521
        O0OOOO0OOO0OOOOO0 =0 #line:522
        OO00000O0O0O0OO00 =0 #line:523
        OO0OOO00O0OO0O00O =0 #line:524
        O000000O0O000O000 =0 #line:525
        O0O00000OO0O00000 =None #line:526
        OOOOOOOO0OO0OOOO0 =None #line:527
        O000OOO0OOO0OOO0O =None #line:528
        if ('min_step_size'in OOOO0000O0OO000O0 .quantifiers ):#line:529
            O0O00000OO0O00000 =OOOO0000O0OO000O0 .quantifiers .get ('min_step_size')#line:530
        if ('min_rel_step_size'in OOOO0000O0OO000O0 .quantifiers ):#line:531
            OOOOOOOO0OO0OOOO0 =OOOO0000O0OO000O0 .quantifiers .get ('min_rel_step_size')#line:532
            if OOOOOOOO0OO0OOOO0 >=1 and OOOOOOOO0OO0OOOO0 <100 :#line:533
                OOOOOOOO0OO0OOOO0 =OOOOOOOO0OO0OOOO0 /100 #line:534
        OO00O0OO0000O00OO =0 #line:535
        OOO00O0OOO0O0OO00 =0 #line:536
        OOO0OOO00O0O00OOO =[]#line:537
        if ('aad_weights'in OOOO0000O0OO000O0 .quantifiers ):#line:538
            OO00O0OO0000O00OO =1 #line:539
            OO0OOOO00000O0O0O =[]#line:540
            OOO0OOO00O0O00OOO =OOOO0000O0OO000O0 .quantifiers .get ('aad_weights')#line:541
        OOOOOOO000O00O00O =OOOO0000O0OO000O0 .data ["dm"][OOOO0000O0OO000O0 .data ["varname"].index (OOOO0000O0OO000O0 .kwargs .get ('target'))]#line:542
        def OOO0O0OO0O0O0O00O (O000O0O000O0O0O00 ,O0000O00O00O0O0O0 ):#line:543
            OOO000OOOOOO0O00O =True #line:544
            if (O000O0O000O0O0O00 >O0000O00O00O0O0O0 ):#line:545
                if not (O0O00000OO0O00000 is None or O000O0O000O0O0O00 >=O0000O00O00O0O0O0 +O0O00000OO0O00000 ):#line:546
                    OOO000OOOOOO0O00O =False #line:547
                if not (OOOOOOOO0OO0OOOO0 is None or O000O0O000O0O0O00 >=O0000O00O00O0O0O0 *(1 +OOOOOOOO0OO0OOOO0 )):#line:548
                    OOO000OOOOOO0O00O =False #line:549
            if (O000O0O000O0O0O00 <O0000O00O00O0O0O0 ):#line:550
                if not (O0O00000OO0O00000 is None or O000O0O000O0O0O00 <=O0000O00O00O0O0O0 -O0O00000OO0O00000 ):#line:551
                    OOO000OOOOOO0O00O =False #line:552
                if not (OOOOOOOO0OO0OOOO0 is None or O000O0O000O0O0O00 <=O0000O00O00O0O0O0 *(1 -OOOOOOOO0OO0OOOO0 )):#line:553
                    OOO000OOOOOO0O00O =False #line:554
            return OOO000OOOOOO0O00O #line:555
        for O0O0OOOOO00000OOO in range (len (OOOOOOO000O00O00O )):#line:556
            OO0OO0O0OOO00O0OO =O0OO0O0O000O00000 #line:558
            O0OO0O0O000O00000 =OOOO0000O0OO000O0 ._bitcount (_O0OOOO00O0O0O0OOO &OOOOOOO000O00O00O [O0O0OOOOO00000OOO ])#line:559
            OOOOOOOO0OOOO00OO .append (O0OO0O0O000O00000 )#line:560
            if O0O0OOOOO00000OOO >0 :#line:561
                if (O0OO0O0O000O00000 >OO0OO0O0OOO00O0OO ):#line:562
                    if (O0OOOO00OOOOOOO00 ==1 )and (OOO0O0OO0O0O0O00O (O0OO0O0O000O00000 ,OO0OO0O0OOO00O0OO )):#line:563
                        OO0OOO00O0OO0O00O +=1 #line:564
                    else :#line:565
                        if OOO0O0OO0O0O0O00O (O0OO0O0O000O00000 ,OO0OO0O0OOO00O0OO ):#line:566
                            OO0OOO00O0OO0O00O =1 #line:567
                        else :#line:568
                            OO0OOO00O0OO0O00O =0 #line:569
                    if OO0OOO00O0OO0O00O >O00OO000O0O0OO0O0 :#line:570
                        O00OO000O0O0OO0O0 =OO0OOO00O0OO0O00O #line:571
                    O0OOOO00OOOOOOO00 =1 #line:572
                    if OOO0O0OO0O0O0O00O (O0OO0O0O000O00000 ,OO0OO0O0OOO00O0OO ):#line:573
                        O0OOOO0OOO0OOOOO0 +=1 #line:574
                if (O0OO0O0O000O00000 <OO0OO0O0OOO00O0OO ):#line:575
                    if (O0OOOO00OOOOOOO00 ==-1 )and (OOO0O0OO0O0O0O00O (O0OO0O0O000O00000 ,OO0OO0O0OOO00O0OO )):#line:576
                        O000000O0O000O000 +=1 #line:577
                    else :#line:578
                        if OOO0O0OO0O0O0O00O (O0OO0O0O000O00000 ,OO0OO0O0OOO00O0OO ):#line:579
                            O000000O0O000O000 =1 #line:580
                        else :#line:581
                            O000000O0O000O000 =0 #line:582
                    if O000000O0O000O000 >OO000OOOO000O000O :#line:583
                        OO000OOOO000O000O =O000000O0O000O000 #line:584
                    O0OOOO00OOOOOOO00 =-1 #line:585
                    if OOO0O0OO0O0O0O00O (O0OO0O0O000O00000 ,OO0OO0O0OOO00O0OO ):#line:586
                        OO00000O0O0O0OO00 +=1 #line:587
                if (O0OO0O0O000O00000 ==OO0OO0O0OOO00O0OO ):#line:588
                    O0OOOO00OOOOOOO00 =0 #line:589
                    O000000O0O000O000 =0 #line:590
                    OO0OOO00O0OO0O00O =0 #line:591
            if (OO00O0OO0000O00OO ):#line:593
                O00OO00O0OO00O0O0 =OOOO0000O0OO000O0 ._bitcount (OOOOOOO000O00O00O [O0O0OOOOO00000OOO ])#line:594
                OO0OOOO00000O0O0O .append (O00OO00O0OO00O0O0 )#line:595
        if (OO00O0OO0000O00OO &sum (OOOOOOOO0OOOO00OO )>0 ):#line:597
            for O0O0OOOOO00000OOO in range (len (OOOOOOO000O00O00O )):#line:598
                if OO0OOOO00000O0O0O [O0O0OOOOO00000OOO ]>0 :#line:599
                    if OOOOOOOO0OOOO00OO [O0O0OOOOO00000OOO ]/sum (OOOOOOOO0OOOO00OO )>OO0OOOO00000O0O0O [O0O0OOOOO00000OOO ]/sum (OO0OOOO00000O0O0O ):#line:600
                        OOO00O0OOO0O0OO00 +=OOO0OOO00O0O00OOO [O0O0OOOOO00000OOO ]*((OOOOOOOO0OOOO00OO [O0O0OOOOO00000OOO ]/sum (OOOOOOOO0OOOO00OO ))/(OO0OOOO00000O0O0O [O0O0OOOOO00000OOO ]/sum (OO0OOOO00000O0O0O ))-1 )#line:601
        OOOOO0O0OOO00OO00 =True #line:604
        for O0OO00OOOOOOOO0O0 in OOOO0000O0OO000O0 .quantifiers .keys ():#line:605
            if O0OO00OOOOOOOO0O0 .upper ()=='BASE':#line:606
                OOOOO0O0OOO00OO00 =OOOOO0O0OOO00OO00 and (OOOO0000O0OO000O0 .quantifiers .get (O0OO00OOOOOOOO0O0 )<=OOOOOOO00OO0000OO )#line:607
            if O0OO00OOOOOOOO0O0 .upper ()=='RELBASE':#line:608
                OOOOO0O0OOO00OO00 =OOOOO0O0OOO00OO00 and (OOOO0000O0OO000O0 .quantifiers .get (O0OO00OOOOOOOO0O0 )<=OOOOOOO00OO0000OO *1.0 /OOOO0000O0OO000O0 .data ["rows_count"])#line:609
            if O0OO00OOOOOOOO0O0 .upper ()=='S_UP':#line:610
                OOOOO0O0OOO00OO00 =OOOOO0O0OOO00OO00 and (OOOO0000O0OO000O0 .quantifiers .get (O0OO00OOOOOOOO0O0 )<=O00OO000O0O0OO0O0 )#line:611
            if O0OO00OOOOOOOO0O0 .upper ()=='S_DOWN':#line:612
                OOOOO0O0OOO00OO00 =OOOOO0O0OOO00OO00 and (OOOO0000O0OO000O0 .quantifiers .get (O0OO00OOOOOOOO0O0 )<=OO000OOOO000O000O )#line:613
            if O0OO00OOOOOOOO0O0 .upper ()=='S_ANY_UP':#line:614
                OOOOO0O0OOO00OO00 =OOOOO0O0OOO00OO00 and (OOOO0000O0OO000O0 .quantifiers .get (O0OO00OOOOOOOO0O0 )<=O00OO000O0O0OO0O0 )#line:615
            if O0OO00OOOOOOOO0O0 .upper ()=='S_ANY_DOWN':#line:616
                OOOOO0O0OOO00OO00 =OOOOO0O0OOO00OO00 and (OOOO0000O0OO000O0 .quantifiers .get (O0OO00OOOOOOOO0O0 )<=OO000OOOO000O000O )#line:617
            if O0OO00OOOOOOOO0O0 .upper ()=='MAX':#line:618
                OOOOO0O0OOO00OO00 =OOOOO0O0OOO00OO00 and (OOOO0000O0OO000O0 .quantifiers .get (O0OO00OOOOOOOO0O0 )<=max (OOOOOOOO0OOOO00OO ))#line:619
            if O0OO00OOOOOOOO0O0 .upper ()=='MIN':#line:620
                OOOOO0O0OOO00OO00 =OOOOO0O0OOO00OO00 and (OOOO0000O0OO000O0 .quantifiers .get (O0OO00OOOOOOOO0O0 )<=min (OOOOOOOO0OOOO00OO ))#line:621
            if O0OO00OOOOOOOO0O0 .upper ()=='RELMAX':#line:622
                if sum (OOOOOOOO0OOOO00OO )>0 :#line:623
                    OOOOO0O0OOO00OO00 =OOOOO0O0OOO00OO00 and (OOOO0000O0OO000O0 .quantifiers .get (O0OO00OOOOOOOO0O0 )<=max (OOOOOOOO0OOOO00OO )*1.0 /sum (OOOOOOOO0OOOO00OO ))#line:624
                else :#line:625
                    OOOOO0O0OOO00OO00 =False #line:626
            if O0OO00OOOOOOOO0O0 .upper ()=='RELMAX_LEQ':#line:627
                if sum (OOOOOOOO0OOOO00OO )>0 :#line:628
                    OOOOO0O0OOO00OO00 =OOOOO0O0OOO00OO00 and (OOOO0000O0OO000O0 .quantifiers .get (O0OO00OOOOOOOO0O0 )>=max (OOOOOOOO0OOOO00OO )*1.0 /sum (OOOOOOOO0OOOO00OO ))#line:629
                else :#line:630
                    OOOOO0O0OOO00OO00 =False #line:631
            if O0OO00OOOOOOOO0O0 .upper ()=='RELMIN':#line:632
                if sum (OOOOOOOO0OOOO00OO )>0 :#line:633
                    OOOOO0O0OOO00OO00 =OOOOO0O0OOO00OO00 and (OOOO0000O0OO000O0 .quantifiers .get (O0OO00OOOOOOOO0O0 )<=min (OOOOOOOO0OOOO00OO )*1.0 /sum (OOOOOOOO0OOOO00OO ))#line:634
                else :#line:635
                    OOOOO0O0OOO00OO00 =False #line:636
            if O0OO00OOOOOOOO0O0 .upper ()=='RELMIN_LEQ':#line:637
                if sum (OOOOOOOO0OOOO00OO )>0 :#line:638
                    OOOOO0O0OOO00OO00 =OOOOO0O0OOO00OO00 and (OOOO0000O0OO000O0 .quantifiers .get (O0OO00OOOOOOOO0O0 )>=min (OOOOOOOO0OOOO00OO )*1.0 /sum (OOOOOOOO0OOOO00OO ))#line:639
                else :#line:640
                    OOOOO0O0OOO00OO00 =False #line:641
            if O0OO00OOOOOOOO0O0 .upper ()=='AAD':#line:642
                OOOOO0O0OOO00OO00 =OOOOO0O0OOO00OO00 and (OOOO0000O0OO000O0 .quantifiers .get (O0OO00OOOOOOOO0O0 )<=OOO00O0OOO0O0OO00 )#line:643
            if O0OO00OOOOOOOO0O0 .upper ()=='RELRANGE_LEQ':#line:644
                O00O0OOO0OOO00O0O =OOOO0000O0OO000O0 .quantifiers .get (O0OO00OOOOOOOO0O0 )#line:645
                if O00O0OOO0OOO00O0O >=1 and O00O0OOO0OOO00O0O <100 :#line:646
                    O00O0OOO0OOO00O0O =O00O0OOO0OOO00O0O *1.0 /100 #line:647
                O0O00O0O0O00OOOOO =min (OOOOOOOO0OOOO00OO )*1.0 /sum (OOOOOOOO0OOOO00OO )#line:648
                OO0OO0OOOOOOOO000 =max (OOOOOOOO0OOOO00OO )*1.0 /sum (OOOOOOOO0OOOO00OO )#line:649
                OOOOO0O0OOO00OO00 =OOOOO0O0OOO00OO00 and (O00O0OOO0OOO00O0O >=OO0OO0OOOOOOOO000 -O0O00O0O0O00OOOOO )#line:650
        O0O00OO00O00OOOOO ={}#line:651
        if OOOOO0O0OOO00OO00 ==True :#line:652
            if OOOO0000O0OO000O0 .verbosity ['debug']:#line:653
                print ("Rule found: base: "+str (OOOOOOO00OO0000OO )+", hist: "+str (OOOOOOOO0OOOO00OO )+", max: "+str (max (OOOOOOOO0OOOO00OO ))+", min: "+str (min (OOOOOOOO0OOOO00OO ))+", s_up: "+str (O00OO000O0O0OO0O0 )+", s_down: "+str (OO000OOOO000O000O ))#line:654
            OOOO0000O0OO000O0 .stats ['total_valid']+=1 #line:655
            O0O00OO00O00OOOOO ["base"]=OOOOOOO00OO0000OO #line:656
            O0O00OO00O00OOOOO ["rel_base"]=OOOOOOO00OO0000OO *1.0 /OOOO0000O0OO000O0 .data ["rows_count"]#line:657
            O0O00OO00O00OOOOO ["s_up"]=O00OO000O0O0OO0O0 #line:658
            O0O00OO00O00OOOOO ["s_down"]=OO000OOOO000O000O #line:659
            O0O00OO00O00OOOOO ["s_any_up"]=O0OOOO0OOO0OOOOO0 #line:660
            O0O00OO00O00OOOOO ["s_any_down"]=OO00000O0O0O0OO00 #line:661
            O0O00OO00O00OOOOO ["max"]=max (OOOOOOOO0OOOO00OO )#line:662
            O0O00OO00O00OOOOO ["min"]=min (OOOOOOOO0OOOO00OO )#line:663
            if OOOO0000O0OO000O0 .verbosity ['debug']:#line:664
                O0O00OO00O00OOOOO ["rel_max"]=max (OOOOOOOO0OOOO00OO )*1.0 /OOOO0000O0OO000O0 .data ["rows_count"]#line:665
                O0O00OO00O00OOOOO ["rel_min"]=min (OOOOOOOO0OOOO00OO )*1.0 /OOOO0000O0OO000O0 .data ["rows_count"]#line:666
            if sum (OOOOOOOO0OOOO00OO )>0 :#line:667
                O0O00OO00O00OOOOO ["rel_max"]=max (OOOOOOOO0OOOO00OO )*1.0 /sum (OOOOOOOO0OOOO00OO )#line:668
                O0O00OO00O00OOOOO ["rel_min"]=min (OOOOOOOO0OOOO00OO )*1.0 /sum (OOOOOOOO0OOOO00OO )#line:669
            else :#line:670
                O0O00OO00O00OOOOO ["rel_max"]=0 #line:671
                O0O00OO00O00OOOOO ["rel_min"]=0 #line:672
            O0O00OO00O00OOOOO ["hist"]=OOOOOOOO0OOOO00OO #line:673
            if OO00O0OO0000O00OO :#line:674
                O0O00OO00O00OOOOO ["aad"]=OOO00O0OOO0O0OO00 #line:675
                O0O00OO00O00OOOOO ["hist_full"]=OO0OOOO00000O0O0O #line:676
                O0O00OO00O00OOOOO ["rel_hist"]=[OOOO0O0O0OO0000O0 /sum (OOOOOOOO0OOOO00OO )for OOOO0O0O0OO0000O0 in OOOOOOOO0OOOO00OO ]#line:677
                O0O00OO00O00OOOOO ["rel_hist_full"]=[O000000O0O000O0OO /sum (OO0OOOO00000O0O0O )for O000000O0O000O0OO in OO0OOOO00000O0O0O ]#line:678
        if OOOO0000O0OO000O0 .verbosity ['debug']:#line:679
            print ("Info: base: "+str (OOOOOOO00OO0000OO )+", hist: "+str (OOOOOOOO0OOOO00OO )+", max: "+str (max (OOOOOOOO0OOOO00OO ))+", min: "+str (min (OOOOOOOO0OOOO00OO ))+", s_up: "+str (O00OO000O0O0OO0O0 )+", s_down: "+str (OO000OOOO000O000O ))#line:680
        return OOOOO0O0OOO00OO00 ,O0O00OO00O00OOOOO #line:681
    def _verifyUIC (OOOOOOOO0O000O0O0 ,_O0OO0OO000O00O000 ):#line:683
        OOO0OOO000OO000O0 ={}#line:684
        OOOO0O00O0OO00OO0 =0 #line:685
        for OOOO0O000OO0O0000 in OOOOOOOO0O000O0O0 .task_actinfo ['cedents']:#line:686
            OOO0OOO000OO000O0 [OOOO0O000OO0O0000 ['cedent_type']]=OOOO0O000OO0O0000 ['filter_value']#line:687
            OOOO0O00O0OO00OO0 =OOOO0O00O0OO00OO0 +1 #line:688
        if OOOOOOOO0O000O0O0 .verbosity ['debug']:#line:689
            print (OOOO0O000OO0O0000 ['cedent_type']+" : "+str (OOOO0O000OO0O0000 ['filter_value']))#line:690
        O00OOOOOO000O00OO =OOOOOOOO0O000O0O0 ._bitcount (_O0OO0OO000O00O000 )#line:691
        OO0O0O0O0000O0000 =[]#line:692
        OO0O00000OOOOO000 =0 #line:693
        O0O0O0O0OOOO0OOOO =0 #line:694
        OOOOO0OO0O0OOO00O =0 #line:695
        OOO0000O00OOO0OO0 =[]#line:696
        OO0O000OO0O00OOO0 =[]#line:697
        if ('aad_weights'in OOOOOOOO0O000O0O0 .quantifiers ):#line:698
            OOO0000O00OOO0OO0 =OOOOOOOO0O000O0O0 .quantifiers .get ('aad_weights')#line:699
            O0O0O0O0OOOO0OOOO =1 #line:700
        OO00000O00000OOOO =OOOOOOOO0O000O0O0 .data ["dm"][OOOOOOOO0O000O0O0 .data ["varname"].index (OOOOOOOO0O000O0O0 .kwargs .get ('target'))]#line:701
        for O0O0O0O0000OO0000 in range (len (OO00000O00000OOOO )):#line:702
            O0OO0O00OO0O0OO0O =OO0O00000OOOOO000 #line:704
            OO0O00000OOOOO000 =OOOOOOOO0O000O0O0 ._bitcount (_O0OO0OO000O00O000 &OO00000O00000OOOO [O0O0O0O0000OO0000 ])#line:705
            OO0O0O0O0000O0000 .append (OO0O00000OOOOO000 )#line:706
            O00OOO00000OOOOO0 =OOOOOOOO0O000O0O0 ._bitcount (OOO0OOO000OO000O0 ['cond']&OO00000O00000OOOO [O0O0O0O0000OO0000 ])#line:708
            OO0O000OO0O00OOO0 .append (O00OOO00000OOOOO0 )#line:709
        O000O00OOOOOOOOO0 =0 #line:711
        OO0O0OOO00OOO0O00 =0 #line:712
        if (O0O0O0O0OOOO0OOOO &sum (OO0O0O0O0000O0000 )>0 ):#line:713
            for O0O0O0O0000OO0000 in range (len (OO00000O00000OOOO )):#line:714
                if OO0O000OO0O00OOO0 [O0O0O0O0000OO0000 ]>0 :#line:715
                    if OO0O0O0O0000O0000 [O0O0O0O0000OO0000 ]/sum (OO0O0O0O0000O0000 )>OO0O000OO0O00OOO0 [O0O0O0O0000OO0000 ]/sum (OO0O000OO0O00OOO0 ):#line:716
                        OOOOO0OO0O0OOO00O +=OOO0000O00OOO0OO0 [O0O0O0O0000OO0000 ]*((OO0O0O0O0000O0000 [O0O0O0O0000OO0000 ]/sum (OO0O0O0O0000O0000 ))/(OO0O000OO0O00OOO0 [O0O0O0O0000OO0000 ]/sum (OO0O000OO0O00OOO0 ))-1 )#line:717
                if OOO0000O00OOO0OO0 [O0O0O0O0000OO0000 ]>0 :#line:718
                    O000O00OOOOOOOOO0 +=OO0O0O0O0000O0000 [O0O0O0O0000OO0000 ]#line:719
                    OO0O0OOO00OOO0O00 +=OO0O000OO0O00OOO0 [O0O0O0O0000OO0000 ]#line:720
        OOO000OOO0O0O0000 =0 #line:721
        if sum (OO0O0O0O0000O0000 )>0 and OO0O0OOO00OOO0O00 >0 :#line:722
            OOO000OOO0O0O0000 =(O000O00OOOOOOOOO0 /sum (OO0O0O0O0000O0000 ))/(OO0O0OOO00OOO0O00 /sum (OO0O000OO0O00OOO0 ))#line:723
        O0000OOOO0OO0OOO0 =True #line:727
        for OO000O00OOOOOOOOO in OOOOOOOO0O000O0O0 .quantifiers .keys ():#line:728
            if OO000O00OOOOOOOOO .upper ()=='BASE':#line:729
                O0000OOOO0OO0OOO0 =O0000OOOO0OO0OOO0 and (OOOOOOOO0O000O0O0 .quantifiers .get (OO000O00OOOOOOOOO )<=O00OOOOOO000O00OO )#line:730
            if OO000O00OOOOOOOOO .upper ()=='RELBASE':#line:731
                O0000OOOO0OO0OOO0 =O0000OOOO0OO0OOO0 and (OOOOOOOO0O000O0O0 .quantifiers .get (OO000O00OOOOOOOOO )<=O00OOOOOO000O00OO *1.0 /OOOOOOOO0O000O0O0 .data ["rows_count"])#line:732
            if OO000O00OOOOOOOOO .upper ()=='AAD_SCORE':#line:733
                O0000OOOO0OO0OOO0 =O0000OOOO0OO0OOO0 and (OOOOOOOO0O000O0O0 .quantifiers .get (OO000O00OOOOOOOOO )<=OOOOO0OO0O0OOO00O )#line:734
            if OO000O00OOOOOOOOO .upper ()=='RELEVANT_CAT_BASE':#line:735
                O0000OOOO0OO0OOO0 =O0000OOOO0OO0OOO0 and (OOOOOOOO0O000O0O0 .quantifiers .get (OO000O00OOOOOOOOO )<=O000O00OOOOOOOOO0 )#line:736
            if OO000O00OOOOOOOOO .upper ()=='RELEVANT_BASE_LIFT':#line:737
                O0000OOOO0OO0OOO0 =O0000OOOO0OO0OOO0 and (OOOOOOOO0O000O0O0 .quantifiers .get (OO000O00OOOOOOOOO )<=OOO000OOO0O0O0000 )#line:738
        O0O000000O0OO00O0 ={}#line:739
        if O0000OOOO0OO0OOO0 ==True :#line:740
            OOOOOOOO0O000O0O0 .stats ['total_valid']+=1 #line:741
            O0O000000O0OO00O0 ["base"]=O00OOOOOO000O00OO #line:742
            O0O000000O0OO00O0 ["rel_base"]=O00OOOOOO000O00OO *1.0 /OOOOOOOO0O000O0O0 .data ["rows_count"]#line:743
            O0O000000O0OO00O0 ["hist"]=OO0O0O0O0000O0000 #line:744
            O0O000000O0OO00O0 ["aad_score"]=OOOOO0OO0O0OOO00O #line:745
            O0O000000O0OO00O0 ["hist_cond"]=OO0O000OO0O00OOO0 #line:746
            O0O000000O0OO00O0 ["rel_hist"]=[O000000OO0O00OOO0 /sum (OO0O0O0O0000O0000 )for O000000OO0O00OOO0 in OO0O0O0O0000O0000 ]#line:747
            O0O000000O0OO00O0 ["rel_hist_cond"]=[O00OO0000O0O0000O /sum (OO0O000OO0O00OOO0 )for O00OO0000O0O0000O in OO0O000OO0O00OOO0 ]#line:748
            O0O000000O0OO00O0 ["relevant_base_lift"]=OOO000OOO0O0O0000 #line:749
            O0O000000O0OO00O0 ["relevant_cat_base"]=O000O00OOOOOOOOO0 #line:750
            O0O000000O0OO00O0 ["relevant_cat_base_full"]=OO0O0OOO00OOO0O00 #line:751
        return O0000OOOO0OO0OOO0 ,O0O000000O0OO00O0 #line:752
    def _verify4ft (OOO0O0000O00OO0O0 ,_OOOOO000O0OOO00O0 ,_trace_cedent =None ,_traces =None ):#line:754
        OOOO00O0OOO00O0O0 ={}#line:755
        OOO0OO000OO0O0000 =0 #line:756
        for OO0OOOO0O000O0OOO in OOO0O0000O00OO0O0 .task_actinfo ['cedents']:#line:757
            OOOO00O0OOO00O0O0 [OO0OOOO0O000O0OOO ['cedent_type']]=OO0OOOO0O000O0OOO ['filter_value']#line:758
            OOO0OO000OO0O0000 =OOO0OO000OO0O0000 +1 #line:759
        OOO00OO000OO0OO0O =OOO0O0000O00OO0O0 ._bitcount (OOOO00O0OOO00O0O0 ['ante']&OOOO00O0OOO00O0O0 ['succ']&OOOO00O0OOO00O0O0 ['cond'])#line:760
        OO0O0OOO0O000OO0O =None #line:761
        OO0O0OOO0O000OO0O =0 #line:762
        if OOO00OO000OO0OO0O >0 :#line:763
            OO0O0OOO0O000OO0O =OOO0O0000O00OO0O0 ._bitcount (OOOO00O0OOO00O0O0 ['ante']&OOOO00O0OOO00O0O0 ['succ']&OOOO00O0OOO00O0O0 ['cond'])*1.0 /OOO0O0000O00OO0O0 ._bitcount (OOOO00O0OOO00O0O0 ['ante']&OOOO00O0OOO00O0O0 ['cond'])#line:764
        O0OO0OOO00OOO000O =1 <<OOO0O0000O00OO0O0 .data ["rows_count"]#line:766
        O0OO0OO00O0OO000O =OOO0O0000O00OO0O0 ._bitcount (OOOO00O0OOO00O0O0 ['ante']&OOOO00O0OOO00O0O0 ['succ']&OOOO00O0OOO00O0O0 ['cond'])#line:767
        O0O0000O0O0OO0O0O =OOO0O0000O00OO0O0 ._bitcount (OOOO00O0OOO00O0O0 ['ante']&~(O0OO0OOO00OOO000O |OOOO00O0OOO00O0O0 ['succ'])&OOOO00O0OOO00O0O0 ['cond'])#line:768
        OO0OOOO0O000O0OOO =OOO0O0000O00OO0O0 ._bitcount (~(O0OO0OOO00OOO000O |OOOO00O0OOO00O0O0 ['ante'])&OOOO00O0OOO00O0O0 ['succ']&OOOO00O0OOO00O0O0 ['cond'])#line:769
        O0OO00000O00OO000 =OOO0O0000O00OO0O0 ._bitcount (~(O0OO0OOO00OOO000O |OOOO00O0OOO00O0O0 ['ante'])&~(O0OO0OOO00OOO000O |OOOO00O0OOO00O0O0 ['succ'])&OOOO00O0OOO00O0O0 ['cond'])#line:770
        O000OO000OOOO0OO0 =0 #line:771
        OOOOO000OOOO00OO0 =0 #line:772
        if (O0OO0OO00O0OO000O +O0O0000O0O0OO0O0O )*(O0OO0OO00O0OO000O +OO0OOOO0O000O0OOO )>0 :#line:773
            O000OO000OOOO0OO0 =O0OO0OO00O0OO000O *(O0OO0OO00O0OO000O +O0O0000O0O0OO0O0O +OO0OOOO0O000O0OOO +O0OO00000O00OO000 )/(O0OO0OO00O0OO000O +O0O0000O0O0OO0O0O )/(O0OO0OO00O0OO000O +OO0OOOO0O000O0OOO )-1 #line:774
            OOOOO000OOOO00OO0 =O000OO000OOOO0OO0 +1 #line:775
        else :#line:776
            O000OO000OOOO0OO0 =None #line:777
            OOOOO000OOOO00OO0 =None #line:778
        OO00O00O0O0O0OOOO =0 #line:779
        if (O0OO0OO00O0OO000O +O0O0000O0O0OO0O0O )*(O0OO0OO00O0OO000O +OO0OOOO0O000O0OOO )>0 :#line:780
            OO00O00O0O0O0OOOO =1 -O0OO0OO00O0OO000O *(O0OO0OO00O0OO000O +O0O0000O0O0OO0O0O +OO0OOOO0O000O0OOO +O0OO00000O00OO000 )/(O0OO0OO00O0OO000O +O0O0000O0O0OO0O0O )/(O0OO0OO00O0OO000O +OO0OOOO0O000O0OOO )#line:781
        else :#line:782
            OO00O00O0O0O0OOOO =None #line:783
        OOOO0O00OO0000O0O =True #line:784
        for OO00OO0O00000OO0O in OOO0O0000O00OO0O0 .quantifiers .keys ():#line:785
            if OO00OO0O00000OO0O .upper ()=='BASE':#line:786
                OOOO0O00OO0000O0O =OOOO0O00OO0000O0O and (OOO0O0000O00OO0O0 .quantifiers .get (OO00OO0O00000OO0O )<=OOO00OO000OO0OO0O )#line:787
            if OO00OO0O00000OO0O .upper ()=='RELBASE':#line:788
                OOOO0O00OO0000O0O =OOOO0O00OO0000O0O and (OOO0O0000O00OO0O0 .quantifiers .get (OO00OO0O00000OO0O )<=OOO00OO000OO0OO0O *1.0 /OOO0O0000O00OO0O0 .data ["rows_count"])#line:789
            if (OO00OO0O00000OO0O .upper ()=='PIM')or (OO00OO0O00000OO0O .upper ()=='CONF'):#line:790
                OOOO0O00OO0000O0O =OOOO0O00OO0000O0O and (OOO0O0000O00OO0O0 .quantifiers .get (OO00OO0O00000OO0O )<=OO0O0OOO0O000OO0O )#line:791
            if OO00OO0O00000OO0O .upper ()=='AAD':#line:792
                if O000OO000OOOO0OO0 !=None :#line:793
                    OOOO0O00OO0000O0O =OOOO0O00OO0000O0O and (OOO0O0000O00OO0O0 .quantifiers .get (OO00OO0O00000OO0O )<=O000OO000OOOO0OO0 )#line:794
                else :#line:795
                    OOOO0O00OO0000O0O =False #line:796
            if OO00OO0O00000OO0O .upper ()=='BAD':#line:797
                if OO00O00O0O0O0OOOO !=None :#line:798
                    OOOO0O00OO0000O0O =OOOO0O00OO0000O0O and (OOO0O0000O00OO0O0 .quantifiers .get (OO00OO0O00000OO0O )<=OO00O00O0O0O0OOOO )#line:799
                else :#line:800
                    OOOO0O00OO0000O0O =False #line:801
            if OO00OO0O00000OO0O .upper ()=='LAMBDA'or OO00OO0O00000OO0O .upper ()=='FN':#line:802
                O000O00O0OO0OOOOO =OOO0O0000O00OO0O0 .quantifiers .get (OO00OO0O00000OO0O )#line:803
                OOOOO0000O00O0OOO =[O0OO0OO00O0OO000O ,O0O0000O0O0OO0O0O ,OO0OOOO0O000O0OOO ,O0OO00000O00OO000 ]#line:804
                O0OO0OOOO00OO0O00 =O000O00O0OO0OOOOO .__code__ .co_argcount #line:805
                if O0OO0OOOO00OO0O00 ==1 :#line:807
                    OOOO0O00OO0000O0O =OOOO0O00OO0000O0O and O000O00O0OO0OOOOO (OOOOO0000O00O0OOO )#line:808
                elif O0OO0OOOO00OO0O00 ==2 :#line:809
                    OO0OOO0O00O0O000O ={}#line:810
                    OOOO0O0O00000OOOO ={}#line:811
                    OOOO0O0O00000OOOO ["varname"]=OOO0O0000O00OO0O0 .data ["varname"]#line:812
                    OOOO0O0O00000OOOO ["catnames"]=OOO0O0000O00OO0O0 .data ["catnames"]#line:813
                    OO0OOO0O00O0O000O ['datalabels']=OOOO0O0O00000OOOO #line:814
                    OO0OOO0O00O0O000O ['trace_cedent']=_trace_cedent #line:815
                    OO0OOO0O00O0O000O ['traces']=_traces #line:816
                    OOOO0O00OO0000O0O =OOOO0O00OO0000O0O and O000O00O0OO0OOOOO (OOOOO0000O00O0OOO ,OO0OOO0O00O0O000O )#line:817
                else :#line:818
                    print (f"Unsupported number of arguments for lambda function ({O0OO0OOOO00OO0O00} for procedure SD4ft-Miner")#line:819
            O00000O0OOOOO0O00 ={}#line:820
        if OOOO0O00OO0000O0O ==True :#line:821
            OOO0O0000O00OO0O0 .stats ['total_valid']+=1 #line:822
            O00000O0OOOOO0O00 ["base"]=OOO00OO000OO0OO0O #line:823
            O00000O0OOOOO0O00 ["rel_base"]=OOO00OO000OO0OO0O *1.0 /OOO0O0000O00OO0O0 .data ["rows_count"]#line:824
            O00000O0OOOOO0O00 ["conf"]=OO0O0OOO0O000OO0O #line:825
            O00000O0OOOOO0O00 ["aad"]=O000OO000OOOO0OO0 #line:826
            O00000O0OOOOO0O00 ["bad"]=OO00O00O0O0O0OOOO #line:827
            O00000O0OOOOO0O00 ["fourfold"]=[O0OO0OO00O0OO000O ,O0O0000O0O0OO0O0O ,OO0OOOO0O000O0OOO ,O0OO00000O00OO000 ]#line:828
        return OOOO0O00OO0000O0O ,O00000O0OOOOO0O00 #line:829
    def _verifysd4ft (O0OOOOOOOOO00OOOO ,_O00OOOOO0O0OOO0OO ):#line:831
        O0000OOO0000OO0O0 ={}#line:832
        OOO0O0OOO0OOO0OOO =0 #line:833
        for OOO0O0O0O000OO000 in O0OOOOOOOOO00OOOO .task_actinfo ['cedents']:#line:834
            O0000OOO0000OO0O0 [OOO0O0O0O000OO000 ['cedent_type']]=OOO0O0O0O000OO000 ['filter_value']#line:835
            OOO0O0OOO0OOO0OOO =OOO0O0OOO0OOO0OOO +1 #line:836
        OO0O0O0OO0O0000OO =O0OOOOOOOOO00OOOO ._bitcount (O0000OOO0000OO0O0 ['ante']&O0000OOO0000OO0O0 ['succ']&O0000OOO0000OO0O0 ['cond']&O0000OOO0000OO0O0 ['frst'])#line:837
        OO0O00OO0O0OOOO0O =O0OOOOOOOOO00OOOO ._bitcount (O0000OOO0000OO0O0 ['ante']&O0000OOO0000OO0O0 ['succ']&O0000OOO0000OO0O0 ['cond']&O0000OOO0000OO0O0 ['scnd'])#line:838
        O0O0O00OO0O00O000 =None #line:839
        O0O0O0000OOOOOO0O =0 #line:840
        O000OOO0OOO00O0O0 =0 #line:841
        if OO0O0O0OO0O0000OO >0 :#line:842
            O0O0O0000OOOOOO0O =O0OOOOOOOOO00OOOO ._bitcount (O0000OOO0000OO0O0 ['ante']&O0000OOO0000OO0O0 ['succ']&O0000OOO0000OO0O0 ['cond']&O0000OOO0000OO0O0 ['frst'])*1.0 /O0OOOOOOOOO00OOOO ._bitcount (O0000OOO0000OO0O0 ['ante']&O0000OOO0000OO0O0 ['cond']&O0000OOO0000OO0O0 ['frst'])#line:843
        if OO0O00OO0O0OOOO0O >0 :#line:844
            O000OOO0OOO00O0O0 =O0OOOOOOOOO00OOOO ._bitcount (O0000OOO0000OO0O0 ['ante']&O0000OOO0000OO0O0 ['succ']&O0000OOO0000OO0O0 ['cond']&O0000OOO0000OO0O0 ['scnd'])*1.0 /O0OOOOOOOOO00OOOO ._bitcount (O0000OOO0000OO0O0 ['ante']&O0000OOO0000OO0O0 ['cond']&O0000OOO0000OO0O0 ['scnd'])#line:845
        O0O000OO00OOOOOO0 =1 <<O0OOOOOOOOO00OOOO .data ["rows_count"]#line:847
        OOO00O00OO0OOOOOO =O0OOOOOOOOO00OOOO ._bitcount (O0000OOO0000OO0O0 ['ante']&O0000OOO0000OO0O0 ['succ']&O0000OOO0000OO0O0 ['cond']&O0000OOO0000OO0O0 ['frst'])#line:848
        OO0O000OOOO000000 =O0OOOOOOOOO00OOOO ._bitcount (O0000OOO0000OO0O0 ['ante']&~(O0O000OO00OOOOOO0 |O0000OOO0000OO0O0 ['succ'])&O0000OOO0000OO0O0 ['cond']&O0000OOO0000OO0O0 ['frst'])#line:849
        OOOO000OO0O000OO0 =O0OOOOOOOOO00OOOO ._bitcount (~(O0O000OO00OOOOOO0 |O0000OOO0000OO0O0 ['ante'])&O0000OOO0000OO0O0 ['succ']&O0000OOO0000OO0O0 ['cond']&O0000OOO0000OO0O0 ['frst'])#line:850
        O0OOO0OO0O0OOOO0O =O0OOOOOOOOO00OOOO ._bitcount (~(O0O000OO00OOOOOO0 |O0000OOO0000OO0O0 ['ante'])&~(O0O000OO00OOOOOO0 |O0000OOO0000OO0O0 ['succ'])&O0000OOO0000OO0O0 ['cond']&O0000OOO0000OO0O0 ['frst'])#line:851
        OO0OO0OO0O0OOOOOO =O0OOOOOOOOO00OOOO ._bitcount (O0000OOO0000OO0O0 ['ante']&O0000OOO0000OO0O0 ['succ']&O0000OOO0000OO0O0 ['cond']&O0000OOO0000OO0O0 ['scnd'])#line:852
        O0OO00O0O00OO000O =O0OOOOOOOOO00OOOO ._bitcount (O0000OOO0000OO0O0 ['ante']&~(O0O000OO00OOOOOO0 |O0000OOO0000OO0O0 ['succ'])&O0000OOO0000OO0O0 ['cond']&O0000OOO0000OO0O0 ['scnd'])#line:853
        OOOO00000OO00OO0O =O0OOOOOOOOO00OOOO ._bitcount (~(O0O000OO00OOOOOO0 |O0000OOO0000OO0O0 ['ante'])&O0000OOO0000OO0O0 ['succ']&O0000OOO0000OO0O0 ['cond']&O0000OOO0000OO0O0 ['scnd'])#line:854
        O00O0OOO00000O0O0 =O0OOOOOOOOO00OOOO ._bitcount (~(O0O000OO00OOOOOO0 |O0000OOO0000OO0O0 ['ante'])&~(O0O000OO00OOOOOO0 |O0000OOO0000OO0O0 ['succ'])&O0000OOO0000OO0O0 ['cond']&O0000OOO0000OO0O0 ['scnd'])#line:855
        O0O00O0O0000OOO00 =True #line:856
        for OO0O00O0O0OO00OO0 in O0OOOOOOOOO00OOOO .quantifiers .keys ():#line:857
            if (OO0O00O0O0OO00OO0 .upper ()=='FRSTBASE')|(OO0O00O0O0OO00OO0 .upper ()=='BASE1'):#line:858
                O0O00O0O0000OOO00 =O0O00O0O0000OOO00 and (O0OOOOOOOOO00OOOO .quantifiers .get (OO0O00O0O0OO00OO0 )<=OO0O0O0OO0O0000OO )#line:859
            if (OO0O00O0O0OO00OO0 .upper ()=='SCNDBASE')|(OO0O00O0O0OO00OO0 .upper ()=='BASE2'):#line:860
                O0O00O0O0000OOO00 =O0O00O0O0000OOO00 and (O0OOOOOOOOO00OOOO .quantifiers .get (OO0O00O0O0OO00OO0 )<=OO0O00OO0O0OOOO0O )#line:861
            if (OO0O00O0O0OO00OO0 .upper ()=='FRSTRELBASE')|(OO0O00O0O0OO00OO0 .upper ()=='RELBASE1'):#line:862
                O0O00O0O0000OOO00 =O0O00O0O0000OOO00 and (O0OOOOOOOOO00OOOO .quantifiers .get (OO0O00O0O0OO00OO0 )<=OO0O0O0OO0O0000OO *1.0 /O0OOOOOOOOO00OOOO .data ["rows_count"])#line:863
            if (OO0O00O0O0OO00OO0 .upper ()=='SCNDRELBASE')|(OO0O00O0O0OO00OO0 .upper ()=='RELBASE2'):#line:864
                O0O00O0O0000OOO00 =O0O00O0O0000OOO00 and (O0OOOOOOOOO00OOOO .quantifiers .get (OO0O00O0O0OO00OO0 )<=OO0O00OO0O0OOOO0O *1.0 /O0OOOOOOOOO00OOOO .data ["rows_count"])#line:865
            if (OO0O00O0O0OO00OO0 .upper ()=='FRSTPIM')|(OO0O00O0O0OO00OO0 .upper ()=='PIM1')|(OO0O00O0O0OO00OO0 .upper ()=='FRSTCONF')|(OO0O00O0O0OO00OO0 .upper ()=='CONF1'):#line:866
                O0O00O0O0000OOO00 =O0O00O0O0000OOO00 and (O0OOOOOOOOO00OOOO .quantifiers .get (OO0O00O0O0OO00OO0 )<=O0O0O0000OOOOOO0O )#line:867
            if (OO0O00O0O0OO00OO0 .upper ()=='SCNDPIM')|(OO0O00O0O0OO00OO0 .upper ()=='PIM2')|(OO0O00O0O0OO00OO0 .upper ()=='SCNDCONF')|(OO0O00O0O0OO00OO0 .upper ()=='CONF2'):#line:868
                O0O00O0O0000OOO00 =O0O00O0O0000OOO00 and (O0OOOOOOOOO00OOOO .quantifiers .get (OO0O00O0O0OO00OO0 )<=O000OOO0OOO00O0O0 )#line:869
            if (OO0O00O0O0OO00OO0 .upper ()=='DELTAPIM')|(OO0O00O0O0OO00OO0 .upper ()=='DELTACONF'):#line:870
                O0O00O0O0000OOO00 =O0O00O0O0000OOO00 and (O0OOOOOOOOO00OOOO .quantifiers .get (OO0O00O0O0OO00OO0 )<=O0O0O0000OOOOOO0O -O000OOO0OOO00O0O0 )#line:871
            if (OO0O00O0O0OO00OO0 .upper ()=='RATIOPIM')|(OO0O00O0O0OO00OO0 .upper ()=='RATIOCONF'):#line:872
                if (O000OOO0OOO00O0O0 >0 ):#line:873
                    O0O00O0O0000OOO00 =O0O00O0O0000OOO00 and (O0OOOOOOOOO00OOOO .quantifiers .get (OO0O00O0O0OO00OO0 )<=O0O0O0000OOOOOO0O *1.0 /O000OOO0OOO00O0O0 )#line:874
                else :#line:875
                    O0O00O0O0000OOO00 =False #line:876
            if (OO0O00O0O0OO00OO0 .upper ()=='RATIOPIM_LEQ')|(OO0O00O0O0OO00OO0 .upper ()=='RATIOCONF_LEQ'):#line:877
                if (O000OOO0OOO00O0O0 >0 ):#line:878
                    O0O00O0O0000OOO00 =O0O00O0O0000OOO00 and (O0OOOOOOOOO00OOOO .quantifiers .get (OO0O00O0O0OO00OO0 )>=O0O0O0000OOOOOO0O *1.0 /O000OOO0OOO00O0O0 )#line:879
                else :#line:880
                    O0O00O0O0000OOO00 =False #line:881
            if OO0O00O0O0OO00OO0 .upper ()=='LAMBDA'or OO0O00O0O0OO00OO0 .upper ()=='FN':#line:882
                OO0O00O0000OOO00O =O0OOOOOOOOO00OOOO .quantifiers .get (OO0O00O0O0OO00OO0 )#line:883
                OO000OOOO000000OO =OO0O00O0000OOO00O .func_code .co_argcount #line:884
                O0000O0OOO00OO000 =[OOO00O00OO0OOOOOO ,OO0O000OOOO000000 ,OOOO000OO0O000OO0 ,O0OOO0OO0O0OOOO0O ]#line:885
                OOO0000O0O00OO0O0 =[OO0OO0OO0O0OOOOOO ,O0OO00O0O00OO000O ,OOOO00000OO00OO0O ,O00O0OOO00000O0O0 ]#line:886
                if OO000OOOO000000OO ==2 :#line:887
                    O0O00O0O0000OOO00 =O0O00O0O0000OOO00 and OO0O00O0000OOO00O (O0000O0OOO00OO000 ,OOO0000O0O00OO0O0 )#line:888
                elif OO000OOOO000000OO ==3 :#line:889
                    O0O00O0O0000OOO00 =O0O00O0O0000OOO00 and OO0O00O0000OOO00O (O0000O0OOO00OO000 ,OOO0000O0O00OO0O0 ,None )#line:890
                else :#line:891
                    print (f"Unsupported number of arguments for lambda function ({OO000OOOO000000OO} for procedure SD4ft-Miner")#line:892
        OOOO0OO000OO0OO00 ={}#line:893
        if O0O00O0O0000OOO00 ==True :#line:894
            O0OOOOOOOOO00OOOO .stats ['total_valid']+=1 #line:895
            OOOO0OO000OO0OO00 ["base1"]=OO0O0O0OO0O0000OO #line:896
            OOOO0OO000OO0OO00 ["base2"]=OO0O00OO0O0OOOO0O #line:897
            OOOO0OO000OO0OO00 ["rel_base1"]=OO0O0O0OO0O0000OO *1.0 /O0OOOOOOOOO00OOOO .data ["rows_count"]#line:898
            OOOO0OO000OO0OO00 ["rel_base2"]=OO0O00OO0O0OOOO0O *1.0 /O0OOOOOOOOO00OOOO .data ["rows_count"]#line:899
            OOOO0OO000OO0OO00 ["conf1"]=O0O0O0000OOOOOO0O #line:900
            OOOO0OO000OO0OO00 ["conf2"]=O000OOO0OOO00O0O0 #line:901
            OOOO0OO000OO0OO00 ["deltaconf"]=O0O0O0000OOOOOO0O -O000OOO0OOO00O0O0 #line:902
            if (O000OOO0OOO00O0O0 >0 ):#line:903
                OOOO0OO000OO0OO00 ["ratioconf"]=O0O0O0000OOOOOO0O *1.0 /O000OOO0OOO00O0O0 #line:904
            else :#line:905
                OOOO0OO000OO0OO00 ["ratioconf"]=None #line:906
            OOOO0OO000OO0OO00 ["fourfold1"]=[OOO00O00OO0OOOOOO ,OO0O000OOOO000000 ,OOOO000OO0O000OO0 ,O0OOO0OO0O0OOOO0O ]#line:907
            OOOO0OO000OO0OO00 ["fourfold2"]=[OO0OO0OO0O0OOOOOO ,O0OO00O0O00OO000O ,OOOO00000OO00OO0O ,O00O0OOO00000O0O0 ]#line:908
        return O0O00O0O0000OOO00 ,OOOO0OO000OO0OO00 #line:909
    def _verify_opt (O0OOO00000O0OO0OO ,O0OOOO0O00OO000OO ,OO00000000O0OOOOO ):#line:912
        O0OOO00000O0OO0OO .stats ['total_ver']+=1 #line:913
        O0O0OOO000OOOOOOO =False #line:914
        if not (O0OOOO0O00OO000OO ['optim'].get ('only_con')):#line:915
            return False #line:916
        if O0OOO00000O0OO0OO .verbosity ['debug']:#line:917
            print (O0OOO00000O0OO0OO .options ['optimizations'])#line:918
        if not (O0OOO00000O0OO0OO .options ['optimizations']):#line:919
            if O0OOO00000O0OO0OO .verbosity ['debug']:#line:920
                print ("NO OPTS")#line:921
            return False #line:922
        if O0OOO00000O0OO0OO .verbosity ['debug']:#line:923
            print ("OPTS")#line:924
        O000O0O0O0O0OOOOO ={}#line:925
        for OO00OOOOOO0O0O0O0 in O0OOO00000O0OO0OO .task_actinfo ['cedents']:#line:926
            if O0OOO00000O0OO0OO .verbosity ['debug']:#line:927
                print (OO00OOOOOO0O0O0O0 ['cedent_type'])#line:928
            O000O0O0O0O0OOOOO [OO00OOOOOO0O0O0O0 ['cedent_type']]=OO00OOOOOO0O0O0O0 ['filter_value']#line:929
            if O0OOO00000O0OO0OO .verbosity ['debug']:#line:930
                print (OO00OOOOOO0O0O0O0 ['cedent_type']+" : "+str (OO00OOOOOO0O0O0O0 ['filter_value']))#line:931
        OO0000O000OO0O0O0 =1 <<O0OOO00000O0OO0OO .data ["rows_count"]#line:932
        O0O00OO000OOOO0OO =OO0000O000OO0O0O0 -1 #line:933
        O000O00OO000000O0 =""#line:934
        OOOOO0OO0O00000OO =0 #line:935
        if (O000O0O0O0O0OOOOO .get ('ante')!=None ):#line:936
            O0O00OO000OOOO0OO =O0O00OO000OOOO0OO &O000O0O0O0O0OOOOO ['ante']#line:937
        if (O000O0O0O0O0OOOOO .get ('succ')!=None ):#line:938
            O0O00OO000OOOO0OO =O0O00OO000OOOO0OO &O000O0O0O0O0OOOOO ['succ']#line:939
        if (O000O0O0O0O0OOOOO .get ('cond')!=None ):#line:940
            O0O00OO000OOOO0OO =O0O00OO000OOOO0OO &O000O0O0O0O0OOOOO ['cond']#line:941
        O00O00OOOO0O0O000 =None #line:942
        if (O0OOO00000O0OO0OO .proc =='CFMiner')|(O0OOO00000O0OO0OO .proc =='4ftMiner')|(O0OOO00000O0OO0OO .proc =='UICMiner'):#line:943
            OOO00O000OOO00O00 =O0OOO00000O0OO0OO ._bitcount (O0O00OO000OOOO0OO )#line:944
            if not (O0OOO00000O0OO0OO ._opt_base ==None ):#line:945
                if not (O0OOO00000O0OO0OO ._opt_base <=OOO00O000OOO00O00 ):#line:946
                    O0O0OOO000OOOOOOO =True #line:947
            if not (O0OOO00000O0OO0OO ._opt_relbase ==None ):#line:948
                if not (O0OOO00000O0OO0OO ._opt_relbase <=OOO00O000OOO00O00 *1.0 /O0OOO00000O0OO0OO .data ["rows_count"]):#line:949
                    O0O0OOO000OOOOOOO =True #line:950
        if (O0OOO00000O0OO0OO .proc =='SD4ftMiner'):#line:951
            OOO00O000OOO00O00 =O0OOO00000O0OO0OO ._bitcount (O0O00OO000OOOO0OO )#line:952
            if (not (O0OOO00000O0OO0OO ._opt_base1 ==None ))&(not (O0OOO00000O0OO0OO ._opt_base2 ==None )):#line:953
                if not (max (O0OOO00000O0OO0OO ._opt_base1 ,O0OOO00000O0OO0OO ._opt_base2 )<=OOO00O000OOO00O00 ):#line:954
                    O0O0OOO000OOOOOOO =True #line:955
            if (not (O0OOO00000O0OO0OO ._opt_relbase1 ==None ))&(not (O0OOO00000O0OO0OO ._opt_relbase2 ==None )):#line:956
                if not (max (O0OOO00000O0OO0OO ._opt_relbase1 ,O0OOO00000O0OO0OO ._opt_relbase2 )<=OOO00O000OOO00O00 *1.0 /O0OOO00000O0OO0OO .data ["rows_count"]):#line:957
                    O0O0OOO000OOOOOOO =True #line:958
        return O0O0OOO000OOOOOOO #line:960
    def _print (OO0OO0000OOOOOO0O ,O00OOOOOO0O0OOOO0 ,_OO0OO0OOOO000O0OO ,_OOO0O0O0OOOO00O00 ):#line:963
        if (len (_OO0OO0OOOO000O0OO ))!=len (_OOO0O0O0OOOO00O00 ):#line:964
            print ("DIFF IN LEN for following cedent : "+str (len (_OO0OO0OOOO000O0OO ))+" vs "+str (len (_OOO0O0O0OOOO00O00 )))#line:965
            print ("trace cedent : "+str (_OO0OO0OOOO000O0OO )+", traces "+str (_OOO0O0O0OOOO00O00 ))#line:966
        OOOOO00O0O00000OO =''#line:967
        O0OOOOOO00OO00000 ={}#line:968
        O0OOO00OOO0OO0O00 =[]#line:969
        for OO0000O0000000OOO in range (len (_OO0OO0OOOO000O0OO )):#line:970
            OO0OOOO00O000OOO0 =OO0OO0000OOOOOO0O .data ["varname"].index (O00OOOOOO0O0OOOO0 ['defi'].get ('attributes')[_OO0OO0OOOO000O0OO [OO0000O0000000OOO ]].get ('name'))#line:971
            OOOOO00O0O00000OO =OOOOO00O0O00000OO +OO0OO0000OOOOOO0O .data ["varname"][OO0OOOO00O000OOO0 ]+'('#line:972
            O0OOO00OOO0OO0O00 .append (OO0OOOO00O000OOO0 )#line:973
            OO00000OOO0O0O00O =[]#line:974
            for O00O0O0O0OO0O0O0O in _OOO0O0O0OOOO00O00 [OO0000O0000000OOO ]:#line:975
                OOOOO00O0O00000OO =OOOOO00O0O00000OO +str (OO0OO0000OOOOOO0O .data ["catnames"][OO0OOOO00O000OOO0 ][O00O0O0O0OO0O0O0O ])+" "#line:976
                OO00000OOO0O0O00O .append (str (OO0OO0000OOOOOO0O .data ["catnames"][OO0OOOO00O000OOO0 ][O00O0O0O0OO0O0O0O ]))#line:977
            OOOOO00O0O00000OO =OOOOO00O0O00000OO [:-1 ]+')'#line:978
            O0OOOOOO00OO00000 [OO0OO0000OOOOOO0O .data ["varname"][OO0OOOO00O000OOO0 ]]=OO00000OOO0O0O00O #line:979
            if OO0000O0000000OOO +1 <len (_OO0OO0OOOO000O0OO ):#line:980
                OOOOO00O0O00000OO =OOOOO00O0O00000OO +' & '#line:981
        return OOOOO00O0O00000OO ,O0OOOOOO00OO00000 ,O0OOO00OOO0OO0O00 #line:982
    def _print_hypo (O0OO00OOOOO0OOO00 ,OO00O00O000OO000O ):#line:984
        O0OO00OOOOO0OOO00 .print_rule (OO00O00O000OO000O )#line:985
    def _print_rule (OO000O0OOOO0OOOOO ,OO000O000OOOO0O00 ):#line:987
        if OO000O0OOOO0OOOOO .verbosity ['print_rules']:#line:988
            print ('Rules info : '+str (OO000O000OOOO0O00 ['params']))#line:989
            for OO0000O0OOOOOOOOO in OO000O0OOOO0OOOOO .task_actinfo ['cedents']:#line:990
                print (OO0000O0OOOOOOOOO ['cedent_type']+' = '+OO0000O0OOOOOOOOO ['generated_string'])#line:991
    def _genvar (O00O00O000000000O ,O00OOOO0OO00O000O ,OOOOOOO00000O000O ,_OOOOOOOOO000OO00O ,_OOOO000O0O0000O0O ,_O0000OOO00OOO0OO0 ,_OOOOOO000O00000OO ,_O0O000OO0OOO0O00O ,_OO000O0O00OOOOO0O ,_OO0OOOO00O000O0O0 ):#line:993
        _O0OO00OOO000OOOO0 =0 #line:994
        _O0O0O0O0O0OO0000O =[]#line:995
        for OO0OOO0O0O0000OO0 in range (OOOOOOO00000O000O ['num_cedent']):#line:996
            if ('force'in OOOOOOO00000O000O ['defi'].get ('attributes')[OO0OOO0O0O0000OO0 ]and OOOOOOO00000O000O ['defi'].get ('attributes')[OO0OOO0O0O0000OO0 ].get ('force')):#line:998
                _O0O0O0O0O0OO0000O .append (OO0OOO0O0O0000OO0 )#line:999
        if OOOOOOO00000O000O ['num_cedent']>0 :#line:1000
            _O0OO00OOO000OOOO0 =(_OO0OOOO00O000O0O0 -_OO000O0O00OOOOO0O )/OOOOOOO00000O000O ['num_cedent']#line:1001
        if OOOOOOO00000O000O ['num_cedent']==0 :#line:1002
            if len (O00OOOO0OO00O000O ['cedents_to_do'])>len (O00OOOO0OO00O000O ['cedents']):#line:1003
                O0O0OOO00O00000O0 ,O0OO0OOO0O0OOO000 ,OOOOOO000OOO000OO =O00O00O000000000O ._print (OOOOOOO00000O000O ,_OOOOOOOOO000OO00O ,_OOOO000O0O0000O0O )#line:1004
                OOOOOOO00000O000O ['generated_string']=O0O0OOO00O00000O0 #line:1005
                OOOOOOO00000O000O ['rule']=O0OO0OOO0O0OOO000 #line:1006
                OOOOOOO00000O000O ['filter_value']=(1 <<O00O00O000000000O .data ["rows_count"])-1 #line:1007
                OOOOOOO00000O000O ['traces']=[]#line:1008
                OOOOOOO00000O000O ['trace_cedent']=[]#line:1009
                OOOOOOO00000O000O ['trace_cedent_asindata']=[]#line:1010
                O00OOOO0OO00O000O ['cedents'].append (OOOOOOO00000O000O )#line:1011
                _OOOOOOOOO000OO00O .append (None )#line:1012
                O00O00O000000000O ._start_cedent (O00OOOO0OO00O000O ,_OO000O0O00OOOOO0O ,_OO0OOOO00O000O0O0 )#line:1013
                O00OOOO0OO00O000O ['cedents'].pop ()#line:1014
        for OO0OOO0O0O0000OO0 in range (OOOOOOO00000O000O ['num_cedent']):#line:1017
            _O0O00000OO0OOOOOO =True #line:1018
            for OO000O0O00O0O0OOO in range (len (_O0O0O0O0O0OO0000O )):#line:1019
                if OO000O0O00O0O0OOO <OO0OOO0O0O0000OO0 and OO000O0O00O0O0OOO not in _OOOOOOOOO000OO00O and OO000O0O00O0O0OOO in _O0O0O0O0O0OO0000O :#line:1020
                    _O0O00000OO0OOOOOO =False #line:1021
            if (len (_OOOOOOOOO000OO00O )==0 or OO0OOO0O0O0000OO0 >_OOOOOOOOO000OO00O [-1 ])and _O0O00000OO0OOOOOO :#line:1023
                _OOOOOOOOO000OO00O .append (OO0OOO0O0O0000OO0 )#line:1024
                O0OO0OO000O0O0000 =O00O00O000000000O .data ["varname"].index (OOOOOOO00000O000O ['defi'].get ('attributes')[OO0OOO0O0O0000OO0 ].get ('name'))#line:1025
                _O000OO00000O0OOO0 =OOOOOOO00000O000O ['defi'].get ('attributes')[OO0OOO0O0O0000OO0 ].get ('minlen')#line:1026
                _OOO0OOO000O0OO0OO =OOOOOOO00000O000O ['defi'].get ('attributes')[OO0OOO0O0O0000OO0 ].get ('maxlen')#line:1027
                _OO00OOOOO0O00OOO0 =OOOOOOO00000O000O ['defi'].get ('attributes')[OO0OOO0O0O0000OO0 ].get ('type')#line:1028
                OO0000OOO00O00OO0 =len (O00O00O000000000O .data ["dm"][O0OO0OO000O0O0000 ])#line:1029
                _O0O0O0O00000OOOO0 =[]#line:1030
                _OOOO000O0O0000O0O .append (_O0O0O0O00000OOOO0 )#line:1031
                _OOOO0O00O0OOOOO00 =int (0 )#line:1032
                O00O00O000000000O ._gencomb (O00OOOO0OO00O000O ,OOOOOOO00000O000O ,_OOOOOOOOO000OO00O ,_OOOO000O0O0000O0O ,_O0O0O0O00000OOOO0 ,_O0000OOO00OOO0OO0 ,_OOOO0O00O0OOOOO00 ,OO0000OOO00O00OO0 ,_OO00OOOOO0O00OOO0 ,_OOOOOO000O00000OO ,_O0O000OO0OOO0O00O ,_O000OO00000O0OOO0 ,_OOO0OOO000O0OO0OO ,_OO000O0O00OOOOO0O +OO0OOO0O0O0000OO0 *_O0OO00OOO000OOOO0 ,_OO000O0O00OOOOO0O +(OO0OOO0O0O0000OO0 +1 )*_O0OO00OOO000OOOO0 )#line:1033
                _OOOO000O0O0000O0O .pop ()#line:1034
                _OOOOOOOOO000OO00O .pop ()#line:1035
    def _gencomb (OO0O0OOOOOO00OO00 ,OO00O00OO0000O00O ,O00O000O00000O0O0 ,_O000OOOOOOO0OOO0O ,_O0000OOOOO00OO000 ,_O00OO0OOO00OO000O ,_OO0OOO0O0O0O00O0O ,_OO00O0OOOOOOOO000 ,O0O0O0000O0O00000 ,_O00OOOO00OO0O0OOO ,_OOOOO00O0O0O00O0O ,_O0OO00O0O0OO00000 ,_OOO0O0O0000OO00O0 ,_OO000OO00OO000O00 ,_O0O0O0000OOO0OO00 ,_O00OOO000OOO0000O ,val_list =None ):#line:1037
        _O0O0O0O0OOO0O0O0O =[]#line:1038
        _O0OO00000OO0000O0 =val_list #line:1039
        if _O00OOOO00OO0O0OOO =="subset":#line:1040
            if len (_O00OO0OOO00OO000O )==0 :#line:1041
                _O0O0O0O0OOO0O0O0O =range (O0O0O0000O0O00000 )#line:1042
            else :#line:1043
                _O0O0O0O0OOO0O0O0O =range (_O00OO0OOO00OO000O [-1 ]+1 ,O0O0O0000O0O00000 )#line:1044
        elif _O00OOOO00OO0O0OOO =="seq":#line:1045
            if len (_O00OO0OOO00OO000O )==0 :#line:1046
                _O0O0O0O0OOO0O0O0O =range (O0O0O0000O0O00000 -_OOO0O0O0000OO00O0 +1 )#line:1047
            else :#line:1048
                if _O00OO0OOO00OO000O [-1 ]+1 ==O0O0O0000O0O00000 :#line:1049
                    return #line:1050
                O000OOOOO0OOO000O =_O00OO0OOO00OO000O [-1 ]+1 #line:1051
                _O0O0O0O0OOO0O0O0O .append (O000OOOOO0OOO000O )#line:1052
        elif _O00OOOO00OO0O0OOO =="lcut":#line:1053
            if len (_O00OO0OOO00OO000O )==0 :#line:1054
                O000OOOOO0OOO000O =0 ;#line:1055
            else :#line:1056
                if _O00OO0OOO00OO000O [-1 ]+1 ==O0O0O0000O0O00000 :#line:1057
                    return #line:1058
                O000OOOOO0OOO000O =_O00OO0OOO00OO000O [-1 ]+1 #line:1059
            _O0O0O0O0OOO0O0O0O .append (O000OOOOO0OOO000O )#line:1060
        elif _O00OOOO00OO0O0OOO =="rcut":#line:1061
            if len (_O00OO0OOO00OO000O )==0 :#line:1062
                O000OOOOO0OOO000O =O0O0O0000O0O00000 -1 ;#line:1063
            else :#line:1064
                if _O00OO0OOO00OO000O [-1 ]==0 :#line:1065
                    return #line:1066
                O000OOOOO0OOO000O =_O00OO0OOO00OO000O [-1 ]-1 #line:1067
                if OO0O0OOOOOO00OO00 .verbosity ['debug']:#line:1068
                    print ("Olditem: "+str (_O00OO0OOO00OO000O [-1 ])+", Newitem : "+str (O000OOOOO0OOO000O ))#line:1069
            _O0O0O0O0OOO0O0O0O .append (O000OOOOO0OOO000O )#line:1070
        elif _O00OOOO00OO0O0OOO =="one":#line:1071
            if len (_O00OO0OOO00OO000O )==0 :#line:1072
                OOOO0O0O0OO0O0OO0 =OO0O0OOOOOO00OO00 .data ["varname"].index (O00O000O00000O0O0 ['defi'].get ('attributes')[_O000OOOOOOO0OOO0O [-1 ]].get ('name'))#line:1073
                try :#line:1074
                    O000OOOOO0OOO000O =OO0O0OOOOOO00OO00 .data ["catnames"][OOOO0O0O0OO0O0OO0 ].index (O00O000O00000O0O0 ['defi'].get ('attributes')[_O000OOOOOOO0OOO0O [-1 ]].get ('value'))#line:1075
                except :#line:1076
                    print (f"ERROR: attribute '{O00O000O00000O0O0['defi'].get('attributes')[_O000OOOOOOO0OOO0O[-1]].get('name')}' has not value '{O00O000O00000O0O0['defi'].get('attributes')[_O000OOOOOOO0OOO0O[-1]].get('value')}'")#line:1077
                    exit (1 )#line:1078
                _O0O0O0O0OOO0O0O0O .append (O000OOOOO0OOO000O )#line:1079
                _OOO0O0O0000OO00O0 =1 #line:1080
                _OO000OO00OO000O00 =1 #line:1081
            else :#line:1082
                print ("DEBUG: one category should not have more categories")#line:1083
                return #line:1084
        elif _O00OOOO00OO0O0OOO =="list":#line:1086
            if _O0OO00000OO0000O0 is None :#line:1087
                OOOO0O0O0OO0O0OO0 =OO0O0OOOOOO00OO00 .data ["varname"].index (O00O000O00000O0O0 ['defi'].get ('attributes')[_O000OOOOOOO0OOO0O [-1 ]].get ('name'))#line:1088
                OO00O0O000O0O0OOO =None #line:1089
                _O000000OOOO00000O =[]#line:1090
                try :#line:1091
                    O0OOOOO000OO0O0OO =O00O000O00000O0O0 ['defi'].get ('attributes')[_O000OOOOOOO0OOO0O [-1 ]].get ('value')#line:1092
                    for O0O000OOO00OOO000 in O0OOOOO000OO0O0OO :#line:1093
                        OO00O0O000O0O0OOO =O0O000OOO00OOO000 #line:1094
                        O000OOOOO0OOO000O =OO0O0OOOOOO00OO00 .data ["catnames"][OOOO0O0O0OO0O0OO0 ].index (O0O000OOO00OOO000 )#line:1095
                        _O000000OOOO00000O .append (O000OOOOO0OOO000O )#line:1096
                except :#line:1097
                    print (f"ERROR: attribute '{O00O000O00000O0O0['defi'].get('attributes')[_O000OOOOOOO0OOO0O[-1]].get('name')}' has not value '{O0O000OOO00OOO000}'")#line:1099
                    exit (1 )#line:1100
                _O0OO00000OO0000O0 =_O000000OOOO00000O #line:1101
                _OOO0O0O0000OO00O0 =len (_O0OO00000OO0000O0 )#line:1102
                _OO000OO00OO000O00 =len (_O0OO00000OO0000O0 )#line:1103
            _O0O0O0O0OOO0O0O0O .append (_O0OO00000OO0000O0 [len (_O00OO0OOO00OO000O )])#line:1104
        else :#line:1106
            print ("Attribute type "+_O00OOOO00OO0O0OOO +" not supported.")#line:1107
            return #line:1108
        if len (_O0O0O0O0OOO0O0O0O )>0 :#line:1110
            _O00OOO0OOO0000OOO =(_O00OOO000OOO0000O -_O0O0O0000OOO0OO00 )/len (_O0O0O0O0OOO0O0O0O )#line:1111
        else :#line:1112
            _O00OOO0OOO0000OOO =0 #line:1113
        _OOO0OOO0OO0O00OO0 =0 #line:1115
        for OO0O0O00O0O000OO0 in _O0O0O0O0OOO0O0O0O :#line:1117
                _O00OO0OOO00OO000O .append (OO0O0O00O0O000OO0 )#line:1118
                _O0000OOOOO00OO000 .pop ()#line:1119
                _O0000OOOOO00OO000 .append (_O00OO0OOO00OO000O )#line:1120
                _OOO0O0O00OO0O0OOO =_OO00O0OOOOOOOO000 |OO0O0OOOOOO00OO00 .data ["dm"][OO0O0OOOOOO00OO00 .data ["varname"].index (O00O000O00000O0O0 ['defi'].get ('attributes')[_O000OOOOOOO0OOO0O [-1 ]].get ('name'))][OO0O0O00O0O000OO0 ]#line:1121
                _O000O00OO00O0000O =1 #line:1122
                if (len (_O000OOOOOOO0OOO0O )<_OOOOO00O0O0O00O0O ):#line:1123
                    _O000O00OO00O0000O =-1 #line:1124
                    if OO0O0OOOOOO00OO00 .verbosity ['debug']:#line:1125
                        print ("DEBUG: will not verify, low cedent length")#line:1126
                if (len (_O0000OOOOO00OO000 [-1 ])<_OOO0O0O0000OO00O0 ):#line:1127
                    _O000O00OO00O0000O =0 #line:1128
                    if OO0O0OOOOOO00OO00 .verbosity ['debug']:#line:1129
                        print ("DEBUG: will not verify, low attribute length")#line:1130
                _O0O0OOOO0O00OO000 =0 #line:1131
                if O00O000O00000O0O0 ['defi'].get ('type')=='con':#line:1132
                    _O0O0OOOO0O00OO000 =_OO0OOO0O0O0O00O0O &_OOO0O0O00OO0O0OOO #line:1133
                else :#line:1134
                    _O0O0OOOO0O00OO000 =_OO0OOO0O0O0O00O0O |_OOO0O0O00OO0O0OOO #line:1135
                O00O000O00000O0O0 ['trace_cedent']=_O000OOOOOOO0OOO0O #line:1136
                O00O000O00000O0O0 ['traces']=_O0000OOOOO00OO000 #line:1137
                O000OOOO0000OO00O ,OOOO0OOOO00O0O00O ,OO0O0OOO000000OO0 =OO0O0OOOOOO00OO00 ._print (O00O000O00000O0O0 ,_O000OOOOOOO0OOO0O ,_O0000OOOOO00OO000 )#line:1138
                O00O000O00000O0O0 ['generated_string']=O000OOOO0000OO00O #line:1139
                O00O000O00000O0O0 ['rule']=OOOO0OOOO00O0O00O #line:1140
                O00O000O00000O0O0 ['filter_value']=_O0O0OOOO0O00OO000 #line:1141
                O00O000O00000O0O0 ['traces']=copy .deepcopy (_O0000OOOOO00OO000 )#line:1142
                O00O000O00000O0O0 ['trace_cedent']=copy .deepcopy (_O000OOOOOOO0OOO0O )#line:1143
                O00O000O00000O0O0 ['trace_cedent_asindata']=copy .deepcopy (OO0O0OOO000000OO0 )#line:1144
                if OO0O0OOOOOO00OO00 .verbosity ['debug']:#line:1145
                    print (f"TC :{O00O000O00000O0O0['trace_cedent_asindata']}")#line:1146
                OO00O00OO0000O00O ['cedents'].append (O00O000O00000O0O0 )#line:1147
                OO000OO000O0O00O0 =OO0O0OOOOOO00OO00 ._verify_opt (OO00O00OO0000O00O ,O00O000O00000O0O0 )#line:1148
                if OO0O0OOOOOO00OO00 .verbosity ['debug']:#line:1149
                    print (f"DEBUG: {O00O000O00000O0O0['generated_string']}.")#line:1150
                    print (f"DEBUG: {_O000OOOOOOO0OOO0O},{_OOOOO00O0O0O00O0O}.")#line:1151
                    if OO000OO000O0O00O0 :#line:1152
                        print ("DEBUG: Optimization: cutting")#line:1153
                if not (OO000OO000O0O00O0 ):#line:1154
                    if _O000O00OO00O0000O ==1 :#line:1155
                        if OO0O0OOOOOO00OO00 .verbosity ['debug']:#line:1156
                            print ("DEBUG: verifying")#line:1157
                        if len (OO00O00OO0000O00O ['cedents_to_do'])==len (OO00O00OO0000O00O ['cedents']):#line:1158
                            if OO0O0OOOOOO00OO00 .proc =='CFMiner':#line:1159
                                O0OO0O000000OOO00 ,O00OOO000OOOOO0OO =OO0O0OOOOOO00OO00 ._verifyCF (_O0O0OOOO0O00OO000 )#line:1160
                            elif OO0O0OOOOOO00OO00 .proc =='UICMiner':#line:1161
                                O0OO0O000000OOO00 ,O00OOO000OOOOO0OO =OO0O0OOOOOO00OO00 ._verifyUIC (_O0O0OOOO0O00OO000 )#line:1162
                            elif OO0O0OOOOOO00OO00 .proc =='4ftMiner':#line:1163
                                O0OO0O000000OOO00 ,O00OOO000OOOOO0OO =OO0O0OOOOOO00OO00 ._verify4ft (_OOO0O0O00OO0O0OOO ,_O000OOOOOOO0OOO0O ,_O0000OOOOO00OO000 )#line:1164
                            elif OO0O0OOOOOO00OO00 .proc =='SD4ftMiner':#line:1165
                                O0OO0O000000OOO00 ,O00OOO000OOOOO0OO =OO0O0OOOOOO00OO00 ._verifysd4ft (_OOO0O0O00OO0O0OOO )#line:1166
                            else :#line:1167
                                print ("Unsupported procedure : "+OO0O0OOOOOO00OO00 .proc )#line:1168
                                exit (0 )#line:1169
                            if O0OO0O000000OOO00 ==True :#line:1170
                                O0OO0000O0OOO00OO ={}#line:1171
                                O0OO0000O0OOO00OO ["rule_id"]=OO0O0OOOOOO00OO00 .stats ['total_valid']#line:1172
                                O0OO0000O0OOO00OO ["cedents_str"]={}#line:1173
                                O0OO0000O0OOO00OO ["cedents_struct"]={}#line:1174
                                O0OO0000O0OOO00OO ['traces']={}#line:1175
                                O0OO0000O0OOO00OO ['trace_cedent_taskorder']={}#line:1176
                                O0OO0000O0OOO00OO ['trace_cedent_dataorder']={}#line:1177
                                for OOOO00OOO000OOOO0 in OO00O00OO0000O00O ['cedents']:#line:1178
                                    if OO0O0OOOOOO00OO00 .verbosity ['debug']:#line:1179
                                        print (OOOO00OOO000OOOO0 )#line:1180
                                    O0OO0000O0OOO00OO ['cedents_str'][OOOO00OOO000OOOO0 ['cedent_type']]=OOOO00OOO000OOOO0 ['generated_string']#line:1181
                                    O0OO0000O0OOO00OO ['cedents_struct'][OOOO00OOO000OOOO0 ['cedent_type']]=OOOO00OOO000OOOO0 ['rule']#line:1182
                                    O0OO0000O0OOO00OO ['traces'][OOOO00OOO000OOOO0 ['cedent_type']]=OOOO00OOO000OOOO0 ['traces']#line:1183
                                    O0OO0000O0OOO00OO ['trace_cedent_taskorder'][OOOO00OOO000OOOO0 ['cedent_type']]=OOOO00OOO000OOOO0 ['trace_cedent']#line:1184
                                    O0OO0000O0OOO00OO ['trace_cedent_dataorder'][OOOO00OOO000OOOO0 ['cedent_type']]=OOOO00OOO000OOOO0 ['trace_cedent_asindata']#line:1185
                                O0OO0000O0OOO00OO ["params"]=O00OOO000OOOOO0OO #line:1186
                                if OO0O0OOOOOO00OO00 .verbosity ['debug']:#line:1187
                                    O0OO0000O0OOO00OO ["trace_cedent"]=copy .deepcopy (_O000OOOOOOO0OOO0O )#line:1188
                                OO0O0OOOOOO00OO00 ._print_rule (O0OO0000O0OOO00OO )#line:1189
                                OO0O0OOOOOO00OO00 .rulelist .append (O0OO0000O0OOO00OO )#line:1190
                            OO0O0OOOOOO00OO00 .stats ['total_cnt']+=1 #line:1191
                            OO0O0OOOOOO00OO00 .stats ['total_ver']+=1 #line:1192
                    if _O000O00OO00O0000O >=1 :#line:1193
                        if len (OO00O00OO0000O00O ['cedents_to_do'])>len (OO00O00OO0000O00O ['cedents']):#line:1194
                            OO0O0OOOOOO00OO00 ._start_cedent (OO00O00OO0000O00O ,_O0O0O0000OOO0OO00 +_OOO0OOO0OO0O00OO0 *_O00OOO0OOO0000OOO ,_O0O0O0000OOO0OO00 +(_OOO0OOO0OO0O00OO0 +0.33 )*_O00OOO0OOO0000OOO )#line:1195
                    OO00O00OO0000O00O ['cedents'].pop ()#line:1196
                    if (not (_O000O00OO00O0000O ==0 ))and (len (_O000OOOOOOO0OOO0O )<_O0OO00O0O0OO00000 ):#line:1197
                        OO0O0OOOOOO00OO00 ._genvar (OO00O00OO0000O00O ,O00O000O00000O0O0 ,_O000OOOOOOO0OOO0O ,_O0000OOOOO00OO000 ,_O0O0OOOO0O00OO000 ,_OOOOO00O0O0O00O0O ,_O0OO00O0O0OO00000 ,_O0O0O0000OOO0OO00 +(_OOO0OOO0OO0O00OO0 +0.33 )*_O00OOO0OOO0000OOO ,_O0O0O0000OOO0OO00 +(_OOO0OOO0OO0O00OO0 +0.66 )*_O00OOO0OOO0000OOO )#line:1198
                else :#line:1199
                    OO00O00OO0000O00O ['cedents'].pop ()#line:1200
                if len (_O00OO0OOO00OO000O )<_OO000OO00OO000O00 :#line:1201
                    OO0O0OOOOOO00OO00 ._gencomb (OO00O00OO0000O00O ,O00O000O00000O0O0 ,_O000OOOOOOO0OOO0O ,_O0000OOOOO00OO000 ,_O00OO0OOO00OO000O ,_OO0OOO0O0O0O00O0O ,_OOO0O0O00OO0O0OOO ,O0O0O0000O0O00000 ,_O00OOOO00OO0O0OOO ,_OOOOO00O0O0O00O0O ,_O0OO00O0O0OO00000 ,_OOO0O0O0000OO00O0 ,_OO000OO00OO000O00 ,_O0O0O0000OOO0OO00 +_O00OOO0OOO0000OOO *(_OOO0OOO0OO0O00OO0 +0.66 ),_O0O0O0000OOO0OO00 +_O00OOO0OOO0000OOO *(_OOO0OOO0OO0O00OO0 +1 ),_O0OO00000OO0000O0 )#line:1202
                _O00OO0OOO00OO000O .pop ()#line:1203
                _OOO0OOO0OO0O00OO0 +=1 #line:1204
                if OO0O0OOOOOO00OO00 .options ['progressbar']:#line:1205
                    OO0O0OOOOOO00OO00 .bar .update (min (100 ,_O0O0O0000OOO0OO00 +_O00OOO0OOO0000OOO *_OOO0OOO0OO0O00OO0 ))#line:1206
                if OO0O0OOOOOO00OO00 .verbosity ['debug']:#line:1207
                    print (f"Progress : lower: {_O0O0O0000OOO0OO00}, step: {_O00OOO0OOO0000OOO}, step_no: {_OOO0OOO0OO0O00OO0} overall: {_O0O0O0000OOO0OO00+_O00OOO0OOO0000OOO*_OOO0OOO0OO0O00OO0}")#line:1208
    def _start_cedent (OOO00OO00000O0OO0 ,O0000O0O0O00O0000 ,_O0OO0OOO0OO0OOO0O ,_O0O00O0OOOOOO0O0O ):#line:1210
        if len (O0000O0O0O00O0000 ['cedents_to_do'])>len (O0000O0O0O00O0000 ['cedents']):#line:1211
            _OOOO0O0O00O0OOOO0 =[]#line:1212
            _OOO00O0OOOOO0O000 =[]#line:1213
            OOOOO00OO0O00OOOO ={}#line:1214
            OOOOO00OO0O00OOOO ['cedent_type']=O0000O0O0O00O0000 ['cedents_to_do'][len (O0000O0O0O00O0000 ['cedents'])]#line:1215
            OOOOOOOOO0O0OO0O0 =OOOOO00OO0O00OOOO ['cedent_type']#line:1216
            if ((OOOOOOOOO0O0OO0O0 [-1 ]=='-')|(OOOOOOOOO0O0OO0O0 [-1 ]=='+')):#line:1217
                OOOOOOOOO0O0OO0O0 =OOOOOOOOO0O0OO0O0 [:-1 ]#line:1218
            OOOOO00OO0O00OOOO ['defi']=OOO00OO00000O0OO0 .kwargs .get (OOOOOOOOO0O0OO0O0 )#line:1220
            if (OOOOO00OO0O00OOOO ['defi']==None ):#line:1221
                print ("Error getting cedent ",OOOOO00OO0O00OOOO ['cedent_type'])#line:1222
            _OOOO00OO0O00OO0O0 =int (0 )#line:1223
            OOOOO00OO0O00OOOO ['num_cedent']=len (OOOOO00OO0O00OOOO ['defi'].get ('attributes'))#line:1224
            if (OOOOO00OO0O00OOOO ['defi'].get ('type')=='con'):#line:1225
                _OOOO00OO0O00OO0O0 =(1 <<OOO00OO00000O0OO0 .data ["rows_count"])-1 #line:1226
            OOO00OO00000O0OO0 ._genvar (O0000O0O0O00O0000 ,OOOOO00OO0O00OOOO ,_OOOO0O0O00O0OOOO0 ,_OOO00O0OOOOO0O000 ,_OOOO00OO0O00OO0O0 ,OOOOO00OO0O00OOOO ['defi'].get ('minlen'),OOOOO00OO0O00OOOO ['defi'].get ('maxlen'),_O0OO0OOO0OO0OOO0O ,_O0O00O0OOOOOO0O0O )#line:1227
    def _calc_all (OOOOOO000OOO0OOO0 ,**OO0000OO0O00OOOO0 ):#line:1230
        if "df"in OO0000OO0O00OOOO0 :#line:1231
            OOOOOO000OOO0OOO0 ._prep_data (OOOOOO000OOO0OOO0 .kwargs .get ("df"))#line:1232
        if not (OOOOOO000OOO0OOO0 ._initialized ):#line:1233
            print ("ERROR: dataframe is missing and not initialized with dataframe")#line:1234
        else :#line:1235
            OOOOOO000OOO0OOO0 ._calculate (**OO0000OO0O00OOOO0 )#line:1236
    def _check_cedents (O0OOOO00O00O0000O ,OOO00OO0O0O0000O0 ,**O00OO00OO0O00OOO0 ):#line:1238
        OOOO0OOO0O00000OO =True #line:1239
        if (O00OO00OO0O00OOO0 .get ('quantifiers',None )==None ):#line:1240
            print (f"Error: missing quantifiers.")#line:1241
            OOOO0OOO0O00000OO =False #line:1242
            return OOOO0OOO0O00000OO #line:1243
        if (type (O00OO00OO0O00OOO0 .get ('quantifiers'))!=dict ):#line:1244
            print (f"Error: quantifiers are not dictionary type.")#line:1245
            OOOO0OOO0O00000OO =False #line:1246
            return OOOO0OOO0O00000OO #line:1247
        for OOO0000O0O0000O00 in OOO00OO0O0O0000O0 :#line:1249
            if (O00OO00OO0O00OOO0 .get (OOO0000O0O0000O00 ,None )==None ):#line:1250
                print (f"Error: cedent {OOO0000O0O0000O00} is missing in parameters.")#line:1251
                OOOO0OOO0O00000OO =False #line:1252
                return OOOO0OOO0O00000OO #line:1253
            OOOO0000O0O00OOOO =O00OO00OO0O00OOO0 .get (OOO0000O0O0000O00 )#line:1254
            if (OOOO0000O0O00OOOO .get ('minlen'),None )==None :#line:1255
                print (f"Error: cedent {OOO0000O0O0000O00} has no minimal length specified.")#line:1256
                OOOO0OOO0O00000OO =False #line:1257
                return OOOO0OOO0O00000OO #line:1258
            if not (type (OOOO0000O0O00OOOO .get ('minlen'))is int ):#line:1259
                print (f"Error: cedent {OOO0000O0O0000O00} has invalid type of minimal length ({type(OOOO0000O0O00OOOO.get('minlen'))}).")#line:1260
                OOOO0OOO0O00000OO =False #line:1261
                return OOOO0OOO0O00000OO #line:1262
            if (OOOO0000O0O00OOOO .get ('maxlen'),None )==None :#line:1263
                print (f"Error: cedent {OOO0000O0O0000O00} has no maximal length specified.")#line:1264
                OOOO0OOO0O00000OO =False #line:1265
                return OOOO0OOO0O00000OO #line:1266
            if not (type (OOOO0000O0O00OOOO .get ('maxlen'))is int ):#line:1267
                print (f"Error: cedent {OOO0000O0O0000O00} has invalid type of maximal length.")#line:1268
                OOOO0OOO0O00000OO =False #line:1269
                return OOOO0OOO0O00000OO #line:1270
            if (OOOO0000O0O00OOOO .get ('type'),None )==None :#line:1271
                print (f"Error: cedent {OOO0000O0O0000O00} has no type specified.")#line:1272
                OOOO0OOO0O00000OO =False #line:1273
                return OOOO0OOO0O00000OO #line:1274
            if not ((OOOO0000O0O00OOOO .get ('type'))in (['con','dis'])):#line:1275
                print (f"Error: cedent {OOO0000O0O0000O00} has invalid type. Allowed values are 'con' and 'dis'.")#line:1276
                OOOO0OOO0O00000OO =False #line:1277
                return OOOO0OOO0O00000OO #line:1278
            if (OOOO0000O0O00OOOO .get ('attributes'),None )==None :#line:1279
                print (f"Error: cedent {OOO0000O0O0000O00} has no attributes specified.")#line:1280
                OOOO0OOO0O00000OO =False #line:1281
                return OOOO0OOO0O00000OO #line:1282
            for OO0O00O00OO00OO0O in OOOO0000O0O00OOOO .get ('attributes'):#line:1283
                if (OO0O00O00OO00OO0O .get ('name'),None )==None :#line:1284
                    print (f"Error: cedent {OOO0000O0O0000O00} / attribute {OO0O00O00OO00OO0O} has no 'name' attribute specified.")#line:1285
                    OOOO0OOO0O00000OO =False #line:1286
                    return OOOO0OOO0O00000OO #line:1287
                if not ((OO0O00O00OO00OO0O .get ('name'))in O0OOOO00O00O0000O .data ["varname"]):#line:1288
                    print (f"Error: cedent {OOO0000O0O0000O00} / attribute {OO0O00O00OO00OO0O.get('name')} not in variable list. Please check spelling.")#line:1289
                    OOOO0OOO0O00000OO =False #line:1290
                    return OOOO0OOO0O00000OO #line:1291
                if (OO0O00O00OO00OO0O .get ('type'),None )==None :#line:1292
                    print (f"Error: cedent {OOO0000O0O0000O00} / attribute {OO0O00O00OO00OO0O.get('name')} has no 'type' attribute specified.")#line:1293
                    OOOO0OOO0O00000OO =False #line:1294
                    return OOOO0OOO0O00000OO #line:1295
                if not ((OO0O00O00OO00OO0O .get ('type'))in (['rcut','lcut','seq','subset','one','list'])):#line:1296
                    print (f"Error: cedent {OOO0000O0O0000O00} / attribute {OO0O00O00OO00OO0O.get('name')} has unsupported type {OO0O00O00OO00OO0O.get('type')}. Supported types are 'subset','seq','lcut','rcut','one','list'.")#line:1297
                    OOOO0OOO0O00000OO =False #line:1298
                    return OOOO0OOO0O00000OO #line:1299
                if (OO0O00O00OO00OO0O .get ('minlen'),None )==None :#line:1300
                    print (f"Error: cedent {OOO0000O0O0000O00} / attribute {OO0O00O00OO00OO0O.get('name')} has no minimal length specified.")#line:1301
                    OOOO0OOO0O00000OO =False #line:1302
                    return OOOO0OOO0O00000OO #line:1303
                if not (type (OO0O00O00OO00OO0O .get ('minlen'))is int ):#line:1304
                    if not (OO0O00O00OO00OO0O .get ('type')=='one'or OO0O00O00OO00OO0O .get ('type')=='list'):#line:1305
                        print (f"Error: cedent {OOO0000O0O0000O00} / attribute {OO0O00O00OO00OO0O.get('name')} has invalid type of minimal length.")#line:1306
                        OOOO0OOO0O00000OO =False #line:1307
                        return OOOO0OOO0O00000OO #line:1308
                if (OO0O00O00OO00OO0O .get ('maxlen'),None )==None :#line:1309
                    print (f"Error: cedent {OOO0000O0O0000O00} / attribute {OO0O00O00OO00OO0O.get('name')} has no maximal length specified.")#line:1310
                    OOOO0OOO0O00000OO =False #line:1311
                    return OOOO0OOO0O00000OO #line:1312
                if not (type (OO0O00O00OO00OO0O .get ('maxlen'))is int ):#line:1313
                    if not (OO0O00O00OO00OO0O .get ('type')=='one'or OO0O00O00OO00OO0O .get ('type')=='list'):#line:1314
                        print (f"Error: cedent {OOO0000O0O0000O00} / attribute {OO0O00O00OO00OO0O.get('name')} has invalid type of maximal length.")#line:1315
                        OOOO0OOO0O00000OO =False #line:1316
                        return OOOO0OOO0O00000OO #line:1317
        return OOOO0OOO0O00000OO #line:1318

    def _calculate (OO0O0OO00OOOO00OO ,**O000OO0000OOOO000 ):#line:3
        if OO0O0OO00OOOO00OO .data ["data_prepared"]==0 :#line:4
            print ("Error: data not prepared")#line:5
            return #line:6
        OO0O0OO00OOOO00OO .kwargs =O000OO0000OOOO000 #line:7
        OO0O0OO00OOOO00OO .proc =O000OO0000OOOO000 .get ('proc')#line:8
        OO0O0OO00OOOO00OO .quantifiers =O000OO0000OOOO000 .get ('quantifiers')#line:9
        OO0O0OO00OOOO00OO ._init_task ()#line:11
        OO0O0OO00OOOO00OO .stats ['start_proc_time']=time .time ()#line:12
        OO0O0OO00OOOO00OO .task_actinfo ['cedents_to_do']=[]#line:13
        OO0O0OO00OOOO00OO .task_actinfo ['cedents']=[]#line:14
        if O000OO0000OOOO000 .get ("proc")=='UICMiner':#line:17
            if not (OO0O0OO00OOOO00OO ._check_cedents (['ante'],**O000OO0000OOOO000 )):#line:18
                return #line:19
            _OO0OOO0O0OO000O00 =O000OO0000OOOO000 .get ("cond")#line:21
            if _OO0OOO0O0OO000O00 !=None :#line:22
                OO0O0OO00OOOO00OO .task_actinfo ['cedents_to_do'].append ('cond')#line:23
            else :#line:24
                O0O00O0OOO0O0OOO0 =OO0O0OO00OOOO00OO .cedent #line:25
                O0O00O0OOO0O0OOO0 ['cedent_type']='cond'#line:26
                O0O00O0OOO0O0OOO0 ['filter_value']=(1 <<OO0O0OO00OOOO00OO .data ["rows_count"])-1 #line:27
                O0O00O0OOO0O0OOO0 ['generated_string']='---'#line:28
                if OO0O0OO00OOOO00OO .verbosity ['debug']:#line:29
                    print (O0O00O0OOO0O0OOO0 ['filter_value'])#line:30
                OO0O0OO00OOOO00OO .task_actinfo ['cedents_to_do'].append ('cond')#line:31
                OO0O0OO00OOOO00OO .task_actinfo ['cedents'].append (O0O00O0OOO0O0OOO0 )#line:32
            OO0O0OO00OOOO00OO .task_actinfo ['cedents_to_do'].append ('ante')#line:33
            if O000OO0000OOOO000 .get ('target',None )==None :#line:34
                print ("ERROR: no succedent/target variable defined for UIC Miner")#line:35
                return #line:36
            if not (O000OO0000OOOO000 .get ('target')in OO0O0OO00OOOO00OO .data ["varname"]):#line:37
                print ("ERROR: target parameter is not variable. Please check spelling of variable name in parameter 'target'.")#line:38
                return #line:39
            if ("aad_score"in OO0O0OO00OOOO00OO .quantifiers ):#line:40
                if not ("aad_weights"in OO0O0OO00OOOO00OO .quantifiers ):#line:41
                    print ("ERROR: for aad quantifier you need to specify aad weights.")#line:42
                    return #line:43
                if not (len (OO0O0OO00OOOO00OO .quantifiers .get ("aad_weights"))==len (OO0O0OO00OOOO00OO .data ["dm"][OO0O0OO00OOOO00OO .data ["varname"].index (OO0O0OO00OOOO00OO .kwargs .get ('target'))])):#line:44
                    print ("ERROR: aad weights has different number of weights than classes of target variable.")#line:45
                    return #line:46
        elif O000OO0000OOOO000 .get ("proc")=='CFMiner':#line:47
            OO0O0OO00OOOO00OO .task_actinfo ['cedents_to_do']=['cond']#line:48
            if O000OO0000OOOO000 .get ('target',None )==None :#line:49
                print ("ERROR: no target variable defined for CF Miner")#line:50
                return #line:51
            O0O0OOOO00O0OOO00 =O000OO0000OOOO000 .get ('target',None )#line:52
            OO0O0OO00OOOO00OO .profiles ['hist_target_entire_dataset_labels']=OO0O0OO00OOOO00OO .data ["catnames"][OO0O0OO00OOOO00OO .data ["varname"].index (OO0O0OO00OOOO00OO .kwargs .get ('target'))]#line:53
            O0O0O000O00OOOO00 =OO0O0OO00OOOO00OO .data ["dm"][OO0O0OO00OOOO00OO .data ["varname"].index (OO0O0OO00OOOO00OO .kwargs .get ('target'))]#line:54
            OOO0O0O0000OO0O0O =[]#line:56
            for OO0OOO00000OO0O00 in range (len (O0O0O000O00OOOO00 )):#line:57
                OO00O0OO00000O00O =OO0O0OO00OOOO00OO ._bitcount (O0O0O000O00OOOO00 [OO0OOO00000OO0O00 ])#line:58
                OOO0O0O0000OO0O0O .append (OO00O0OO00000O00O )#line:59
            OO0O0OO00OOOO00OO .profiles ['hist_target_entire_dataset_values']=OOO0O0O0000OO0O0O #line:60
            if not (OO0O0OO00OOOO00OO ._check_cedents (['cond'],**O000OO0000OOOO000 )):#line:61
                return #line:62
            if not (O000OO0000OOOO000 .get ('target')in OO0O0OO00OOOO00OO .data ["varname"]):#line:63
                print ("ERROR: target parameter is not variable. Please check spelling of variable name in parameter 'target'.")#line:64
                return #line:65
            if ("aad"in OO0O0OO00OOOO00OO .quantifiers ):#line:66
                if not ("aad_weights"in OO0O0OO00OOOO00OO .quantifiers ):#line:67
                    print ("ERROR: for aad quantifier you need to specify aad weights.")#line:68
                    return #line:69
                if not (len (OO0O0OO00OOOO00OO .quantifiers .get ("aad_weights"))==len (OO0O0OO00OOOO00OO .data ["dm"][OO0O0OO00OOOO00OO .data ["varname"].index (OO0O0OO00OOOO00OO .kwargs .get ('target'))])):#line:70
                    print ("ERROR: aad weights has different number of weights than classes of target variable.")#line:71
                    return #line:72
        elif O000OO0000OOOO000 .get ("proc")=='4ftMiner':#line:75
            if not (OO0O0OO00OOOO00OO ._check_cedents (['ante','succ'],**O000OO0000OOOO000 )):#line:76
                return #line:77
            _OO0OOO0O0OO000O00 =O000OO0000OOOO000 .get ("cond")#line:79
            if _OO0OOO0O0OO000O00 !=None :#line:80
                OO0O0OO00OOOO00OO .task_actinfo ['cedents_to_do'].append ('cond')#line:81
            else :#line:82
                O0O00O0OOO0O0OOO0 =OO0O0OO00OOOO00OO .cedent #line:83
                O0O00O0OOO0O0OOO0 ['cedent_type']='cond'#line:84
                O0O00O0OOO0O0OOO0 ['filter_value']=(1 <<OO0O0OO00OOOO00OO .data ["rows_count"])-1 #line:85
                O0O00O0OOO0O0OOO0 ['generated_string']='---'#line:86
                OO0O0OO00OOOO00OO .task_actinfo ['cedents_to_do'].append ('cond')#line:87
                OO0O0OO00OOOO00OO .task_actinfo ['cedents'].append (O0O00O0OOO0O0OOO0 )#line:88
            OO0O0OO00OOOO00OO .task_actinfo ['cedents_to_do'].append ('ante')#line:89
            OO0O0OO00OOOO00OO .task_actinfo ['cedents_to_do'].append ('succ')#line:90
        elif O000OO0000OOOO000 .get ("proc")=='SD4ftMiner':#line:91
            if not (OO0O0OO00OOOO00OO ._check_cedents (['ante','succ','frst','scnd'],**O000OO0000OOOO000 )):#line:94
                return #line:95
            _OO0OOO0O0OO000O00 =O000OO0000OOOO000 .get ("cond")#line:96
            if _OO0OOO0O0OO000O00 !=None :#line:97
                OO0O0OO00OOOO00OO .task_actinfo ['cedents_to_do'].append ('cond')#line:98
            else :#line:99
                O0O00O0OOO0O0OOO0 =OO0O0OO00OOOO00OO .cedent #line:100
                O0O00O0OOO0O0OOO0 ['cedent_type']='cond'#line:101
                O0O00O0OOO0O0OOO0 ['filter_value']=(1 <<OO0O0OO00OOOO00OO .data ["rows_count"])-1 #line:102
                O0O00O0OOO0O0OOO0 ['generated_string']='---'#line:103
                OO0O0OO00OOOO00OO .task_actinfo ['cedents_to_do'].append ('cond')#line:104
                OO0O0OO00OOOO00OO .task_actinfo ['cedents'].append (O0O00O0OOO0O0OOO0 )#line:105
            OO0O0OO00OOOO00OO .task_actinfo ['cedents_to_do'].append ('frst')#line:106
            OO0O0OO00OOOO00OO .task_actinfo ['cedents_to_do'].append ('scnd')#line:107
            OO0O0OO00OOOO00OO .task_actinfo ['cedents_to_do'].append ('ante')#line:108
            OO0O0OO00OOOO00OO .task_actinfo ['cedents_to_do'].append ('succ')#line:109
        else :#line:110
            print ("Unsupported procedure")#line:111
            return #line:112
        print ("Will go for ",O000OO0000OOOO000 .get ("proc"))#line:113
        OO0O0OO00OOOO00OO .task_actinfo ['optim']={}#line:116
        O0O00000OOOOO0000 =True #line:117
        for O00OO0O0O00O0OOOO in OO0O0OO00OOOO00OO .task_actinfo ['cedents_to_do']:#line:118
            try :#line:119
                O0O00O00O0O0O0000 =OO0O0OO00OOOO00OO .kwargs .get (O00OO0O0O00O0OOOO )#line:120
                if OO0O0OO00OOOO00OO .verbosity ['debug']:#line:121
                    print (O0O00O00O0O0O0000 )#line:122
                    print (f"...cedent {O00OO0O0O00O0OOOO} is type {O0O00O00O0O0O0000.get('type')}")#line:123
                    print (f"Will check cedent type {O00OO0O0O00O0OOOO} : {O0O00O00O0O0O0000.get('type')}")#line:124
                if O0O00O00O0O0O0000 .get ('type')!='con':#line:125
                    O0O00000OOOOO0000 =False #line:126
                    if OO0O0OO00OOOO00OO .verbosity ['debug']:#line:127
                        print (f"Cannot optim due to cedent type {O00OO0O0O00O0OOOO} : {O0O00O00O0O0O0000.get('type')}")#line:128
            except :#line:129
                O0000O00OOOOOO0O0 =1 <2 #line:130
        if OO0O0OO00OOOO00OO .options ['optimizations']==False :#line:132
            O0O00000OOOOO0000 =False #line:133
        OO00OO00O0000O0OO ={}#line:134
        OO00OO00O0000O0OO ['only_con']=O0O00000OOOOO0000 #line:135
        OO0O0OO00OOOO00OO .task_actinfo ['optim']=OO00OO00O0000O0OO #line:136
        if OO0O0OO00OOOO00OO .verbosity ['debug']:#line:140
            print ("Starting to prepare data.")#line:141
            OO0O0OO00OOOO00OO ._prep_data (OO0O0OO00OOOO00OO .data .df )#line:142
            OO0O0OO00OOOO00OO .stats ['mid1_time']=time .time ()#line:143
            OO0O0OO00OOOO00OO .quantifiers =O000OO0000OOOO000 .get ('self.quantifiers')#line:144
        print ("Starting to mine rules.")#line:145
        sys .stdout .flush ()#line:146
        time .sleep (0.01 )#line:147
        if OO0O0OO00OOOO00OO .options ['progressbar']:#line:148
            OO0O0000OOO00OOO0 =[progressbar .Percentage (),progressbar .Bar (),progressbar .Timer ()]#line:149
            OO0O0OO00OOOO00OO .bar =progressbar .ProgressBar (widgets =OO0O0000OOO00OOO0 ,max_value =100 ,fd =sys .stdout ).start ()#line:150
            OO0O0OO00OOOO00OO .bar .update (0 )#line:151
        OO0O0OO00OOOO00OO .progress_lower =0 #line:152
        OO0O0OO00OOOO00OO .progress_upper =100 #line:153
        OO0O0OO00OOOO00OO ._start_cedent (OO0O0OO00OOOO00OO .task_actinfo ,OO0O0OO00OOOO00OO .progress_lower ,OO0O0OO00OOOO00OO .progress_upper )#line:154
        if OO0O0OO00OOOO00OO .options ['progressbar']:#line:155
            OO0O0OO00OOOO00OO .bar .update (100 )#line:156
            OO0O0OO00OOOO00OO .bar .finish ()#line:157
        OO0O0OO00OOOO00OO .stats ['end_proc_time']=time .time ()#line:158
        print ("Done. Total verifications : "+str (OO0O0OO00OOOO00OO .stats ['total_cnt'])+", rules "+str (OO0O0OO00OOOO00OO .stats ['total_valid'])+", times: prep "+"{:.2f}".format (OO0O0OO00OOOO00OO .stats ['end_prep_time']-OO0O0OO00OOOO00OO .stats ['start_prep_time'])+"sec, processing "+"{:.2f}".format (OO0O0OO00OOOO00OO .stats ['end_proc_time']-OO0O0OO00OOOO00OO .stats ['start_proc_time'])+"sec")#line:161
        OO00O0OO0OO000O0O ={}#line:162
        O0000OO0OOOOOO00O ={}#line:163
        O0000OO0OOOOOO00O ["guid"]=OO0O0OO00OOOO00OO .guid #line:164
        O0000OO0OOOOOO00O ["task_type"]=O000OO0000OOOO000 .get ('proc')#line:165
        O0000OO0OOOOOO00O ["target"]=O000OO0000OOOO000 .get ('target')#line:166
        O0000OO0OOOOOO00O ["self.quantifiers"]=OO0O0OO00OOOO00OO .quantifiers #line:167
        if O000OO0000OOOO000 .get ('cond')!=None :#line:168
            O0000OO0OOOOOO00O ['cond']=O000OO0000OOOO000 .get ('cond')#line:169
        if O000OO0000OOOO000 .get ('ante')!=None :#line:170
            O0000OO0OOOOOO00O ['ante']=O000OO0000OOOO000 .get ('ante')#line:171
        if O000OO0000OOOO000 .get ('succ')!=None :#line:172
            O0000OO0OOOOOO00O ['succ']=O000OO0000OOOO000 .get ('succ')#line:173
        if O000OO0000OOOO000 .get ('opts')!=None :#line:174
            O0000OO0OOOOOO00O ['opts']=O000OO0000OOOO000 .get ('opts')#line:175
        if OO0O0OO00OOOO00OO .df is None :#line:176
            O0000OO0OOOOOO00O ['rowcount']=OO0O0OO00OOOO00OO .data ["rows_count"]#line:177
        else :#line:178
            O0000OO0OOOOOO00O ['rowcount']=len (OO0O0OO00OOOO00OO .df .index )#line:179
        OO00O0OO0OO000O0O ["taskinfo"]=O0000OO0OOOOOO00O #line:180
        OOO0O00000O00OO0O ={}#line:181
        OOO0O00000O00OO0O ["total_verifications"]=OO0O0OO00OOOO00OO .stats ['total_cnt']#line:182
        OOO0O00000O00OO0O ["valid_rules"]=OO0O0OO00OOOO00OO .stats ['total_valid']#line:183
        OOO0O00000O00OO0O ["total_verifications_with_opt"]=OO0O0OO00OOOO00OO .stats ['total_ver']#line:184
        OOO0O00000O00OO0O ["time_prep"]=OO0O0OO00OOOO00OO .stats ['end_prep_time']-OO0O0OO00OOOO00OO .stats ['start_prep_time']#line:185
        OOO0O00000O00OO0O ["time_processing"]=OO0O0OO00OOOO00OO .stats ['end_proc_time']-OO0O0OO00OOOO00OO .stats ['start_proc_time']#line:186
        OOO0O00000O00OO0O ["time_total"]=OO0O0OO00OOOO00OO .stats ['end_prep_time']-OO0O0OO00OOOO00OO .stats ['start_prep_time']+OO0O0OO00OOOO00OO .stats ['end_proc_time']-OO0O0OO00OOOO00OO .stats ['start_proc_time']#line:187
        OO00O0OO0OO000O0O ["summary_statistics"]=OOO0O00000O00OO0O #line:188
        OO00O0OO0OO000O0O ["rules"]=OO0O0OO00OOOO00OO .rulelist #line:189
        OOOO0OO000O0OOOOO ={}#line:190
        OOOO0OO000O0OOOOO ["varname"]=OO0O0OO00OOOO00OO .data ["varname"]#line:191
        OOOO0OO000O0OOOOO ["catnames"]=OO0O0OO00OOOO00OO .data ["catnames"]#line:192
        OO00O0OO0OO000O0O ["datalabels"]=OOOO0OO000O0OOOOO #line:193
        OO0O0OO00OOOO00OO .result =OO00O0OO0OO000O0O #line:194
    def print_summary (O0OO000000OOO0000 ):#line:196
        ""#line:199
        if not (O0OO000000OOO0000 ._is_calculated ()):#line:200
            print ("ERROR: Task has not been calculated.")#line:201
            return #line:202
        print ("")#line:203
        print ("CleverMiner task processing summary:")#line:204
        print ("")#line:205
        print (f"Task type : {O0OO000000OOO0000.result['taskinfo']['task_type']}")#line:206
        print (f"Number of verifications : {O0OO000000OOO0000.result['summary_statistics']['total_verifications']}")#line:207
        print (f"Number of rules : {O0OO000000OOO0000.result['summary_statistics']['valid_rules']}")#line:208
        print (f"Total time needed : {strftime('%Hh %Mm %Ss', gmtime(O0OO000000OOO0000.result['summary_statistics']['time_total']))}")#line:209
        if O0OO000000OOO0000 .verbosity ['debug']:#line:210
            print (f"Total time needed : {O0OO000000OOO0000.result['summary_statistics']['time_total']}")#line:211
        print (f"Time of data preparation : {strftime('%Hh %Mm %Ss', gmtime(O0OO000000OOO0000.result['summary_statistics']['time_prep']))}")#line:212
        print (f"Time of rule mining : {strftime('%Hh %Mm %Ss', gmtime(O0OO000000OOO0000.result['summary_statistics']['time_processing']))}")#line:213
        print ("")#line:214
    def print_hypolist (O00OO0O0000O0O00O ):#line:216
        ""#line:219
        O00OO0O0000O0O00O .print_rulelist ();#line:220
    def print_rulelist (OO000000O000O0O0O ,sortby =None ,storesorted =False ):#line:222
        ""#line:227
        if not (OO000000O000O0O0O ._is_calculated ()):#line:228
            print ("ERROR: Task has not been calculated.")#line:229
            return #line:230
        def O00O0O0OO0OOO0OO0 (OO000OO00OO00O0O0 ):#line:232
            OO0OOOOOOO0O0OO00 =OO000OO00OO00O0O0 ["params"]#line:233
            return OO0OOOOOOO0O0OO00 .get (sortby ,0 )#line:234
        print ("")#line:236
        print ("List of rules:")#line:237
        if OO000000O000O0O0O .result ['taskinfo']['task_type']=="4ftMiner":#line:238
            print ("RULEID BASE  CONF  AAD    Rule")#line:239
        elif OO000000O000O0O0O .result ['taskinfo']['task_type']=="UICMiner":#line:240
            print ("RULEID BASE  AAD_SCORE  Rule")#line:241
        elif OO000000O000O0O0O .result ['taskinfo']['task_type']=="CFMiner":#line:242
            print ("RULEID BASE  S_UP  S_DOWN Condition")#line:243
        elif OO000000O000O0O0O .result ['taskinfo']['task_type']=="SD4ftMiner":#line:244
            print ("RULEID BASE1 BASE2 RatioConf DeltaConf Rule")#line:245
        else :#line:246
            print ("Unsupported task type for rulelist")#line:247
            return #line:248
        O0OO0OOO0000000OO =OO000000O000O0O0O .result ["rules"]#line:249
        if sortby is not None :#line:250
            O0OO0OOO0000000OO =sorted (O0OO0OOO0000000OO ,key =O00O0O0OO0OOO0OO0 ,reverse =True )#line:251
            if storesorted :#line:252
                OO000000O000O0O0O .result ["rules"]=O0OO0OOO0000000OO #line:253
        for O000OO0OOO000O000 in O0OO0OOO0000000OO :#line:255
            O00O00O00O0O0OO0O ="{:6d}".format (O000OO0OOO000O000 ["rule_id"])#line:256
            if OO000000O000O0O0O .result ['taskinfo']['task_type']=="4ftMiner":#line:257
                if OO000000O000O0O0O .verbosity ['debug']:#line:258
                   print (f"{O000OO0OOO000O000['params']}")#line:259
                O00O00O00O0O0OO0O =O00O00O00O0O0OO0O +" "+"{:5d}".format (O000OO0OOO000O000 ["params"]["base"])+" "+"{:.3f}".format (O000OO0OOO000O000 ["params"]["conf"])+" "+"{:+.3f}".format (O000OO0OOO000O000 ["params"]["aad"])#line:260
                O00O00O00O0O0OO0O =O00O00O00O0O0OO0O +" "+O000OO0OOO000O000 ["cedents_str"]["ante"]+" => "+O000OO0OOO000O000 ["cedents_str"]["succ"]+" | "+O000OO0OOO000O000 ["cedents_str"]["cond"]#line:261
            elif OO000000O000O0O0O .result ['taskinfo']['task_type']=="UICMiner":#line:262
                O00O00O00O0O0OO0O =O00O00O00O0O0OO0O +" "+"{:5d}".format (O000OO0OOO000O000 ["params"]["base"])+" "+"{:.3f}".format (O000OO0OOO000O000 ["params"]["aad_score"])#line:263
                O00O00O00O0O0OO0O =O00O00O00O0O0OO0O +"     "+O000OO0OOO000O000 ["cedents_str"]["ante"]+" => "+OO000000O000O0O0O .result ['taskinfo']['target']+"(*) | "+O000OO0OOO000O000 ["cedents_str"]["cond"]#line:264
            elif OO000000O000O0O0O .result ['taskinfo']['task_type']=="CFMiner":#line:265
                O00O00O00O0O0OO0O =O00O00O00O0O0OO0O +" "+"{:5d}".format (O000OO0OOO000O000 ["params"]["base"])+" "+"{:5d}".format (O000OO0OOO000O000 ["params"]["s_up"])+" "+"{:5d}".format (O000OO0OOO000O000 ["params"]["s_down"])#line:266
                O00O00O00O0O0OO0O =O00O00O00O0O0OO0O +" "+O000OO0OOO000O000 ["cedents_str"]["cond"]#line:267
            elif OO000000O000O0O0O .result ['taskinfo']['task_type']=="SD4ftMiner":#line:268
                O00O00O00O0O0OO0O =O00O00O00O0O0OO0O +" "+"{:5d}".format (O000OO0OOO000O000 ["params"]["base1"])+" "+"{:5d}".format (O000OO0OOO000O000 ["params"]["base2"])+"    "+"{:.3f}".format (O000OO0OOO000O000 ["params"]["ratioconf"])+"    "+"{:+.3f}".format (O000OO0OOO000O000 ["params"]["deltaconf"])#line:269
                O00O00O00O0O0OO0O =O00O00O00O0O0OO0O +"  "+O000OO0OOO000O000 ["cedents_str"]["ante"]+" => "+O000OO0OOO000O000 ["cedents_str"]["succ"]+" | "+O000OO0OOO000O000 ["cedents_str"]["cond"]+" : "+O000OO0OOO000O000 ["cedents_str"]["frst"]+" x "+O000OO0OOO000O000 ["cedents_str"]["scnd"]#line:270
            print (O00O00O00O0O0OO0O )#line:272
        print ("")#line:273
    def print_hypo (OO00O0O0O00OOOO0O ,O0O0OOOOO00O00OO0 ):#line:275
        ""#line:279
        OO00O0O0O00OOOO0O .print_rule (O0O0OOOOO00O00OO0 )#line:280
    def print_rule (O000O0O00OOOO0000 ,O0OO0OOO0OOOOOO0O ):#line:283
        ""#line:287
        if not (O000O0O00OOOO0000 ._is_calculated ()):#line:288
            print ("ERROR: Task has not been calculated.")#line:289
            return #line:290
        print ("")#line:291
        if (O0OO0OOO0OOOOOO0O <=len (O000O0O00OOOO0000 .result ["rules"])):#line:292
            if O000O0O00OOOO0000 .result ['taskinfo']['task_type']=="4ftMiner":#line:293
                print ("")#line:294
                OOOO0O000OOOOOO00 =O000O0O00OOOO0000 .result ["rules"][O0OO0OOO0OOOOOO0O -1 ]#line:295
                print (f"Rule id : {OOOO0O000OOOOOO00['rule_id']}")#line:296
                print ("")#line:297
                print (f"Base : {'{:5d}'.format(OOOO0O000OOOOOO00['params']['base'])}  Relative base : {'{:.3f}'.format(OOOO0O000OOOOOO00['params']['rel_base'])}  CONF : {'{:.3f}'.format(OOOO0O000OOOOOO00['params']['conf'])}  AAD : {'{:+.3f}'.format(OOOO0O000OOOOOO00['params']['aad'])}  BAD : {'{:+.3f}'.format(OOOO0O000OOOOOO00['params']['bad'])}")#line:298
                print ("")#line:299
                print ("Cedents:")#line:300
                print (f"  antecedent : {OOOO0O000OOOOOO00['cedents_str']['ante']}")#line:301
                print (f"  succcedent : {OOOO0O000OOOOOO00['cedents_str']['succ']}")#line:302
                print (f"  condition  : {OOOO0O000OOOOOO00['cedents_str']['cond']}")#line:303
                print ("")#line:304
                print ("Fourfold table")#line:305
                print (f"    |  S  |  ¬S |")#line:306
                print (f"----|-----|-----|")#line:307
                print (f" A  |{'{:5d}'.format(OOOO0O000OOOOOO00['params']['fourfold'][0])}|{'{:5d}'.format(OOOO0O000OOOOOO00['params']['fourfold'][1])}|")#line:308
                print (f"----|-----|-----|")#line:309
                print (f"¬A  |{'{:5d}'.format(OOOO0O000OOOOOO00['params']['fourfold'][2])}|{'{:5d}'.format(OOOO0O000OOOOOO00['params']['fourfold'][3])}|")#line:310
                print (f"----|-----|-----|")#line:311
            elif O000O0O00OOOO0000 .result ['taskinfo']['task_type']=="CFMiner":#line:312
                print ("")#line:313
                OOOO0O000OOOOOO00 =O000O0O00OOOO0000 .result ["rules"][O0OO0OOO0OOOOOO0O -1 ]#line:314
                print (f"Rule id : {OOOO0O000OOOOOO00['rule_id']}")#line:315
                print ("")#line:316
                OOOO0OOOO0OO0O0O0 =""#line:317
                if ('aad'in OOOO0O000OOOOOO00 ['params']):#line:318
                    OOOO0OOOO0OO0O0O0 ="aad : "+str (OOOO0O000OOOOOO00 ['params']['aad'])#line:319
                print (f"Base : {'{:5d}'.format(OOOO0O000OOOOOO00['params']['base'])}  Relative base : {'{:.3f}'.format(OOOO0O000OOOOOO00['params']['rel_base'])}  Steps UP (consecutive) : {'{:5d}'.format(OOOO0O000OOOOOO00['params']['s_up'])}  Steps DOWN (consecutive) : {'{:5d}'.format(OOOO0O000OOOOOO00['params']['s_down'])}  Steps UP (any) : {'{:5d}'.format(OOOO0O000OOOOOO00['params']['s_any_up'])}  Steps DOWN (any) : {'{:5d}'.format(OOOO0O000OOOOOO00['params']['s_any_down'])}  Histogram maximum : {'{:5d}'.format(OOOO0O000OOOOOO00['params']['max'])}  Histogram minimum : {'{:5d}'.format(OOOO0O000OOOOOO00['params']['min'])}  Histogram relative maximum : {'{:.3f}'.format(OOOO0O000OOOOOO00['params']['rel_max'])} Histogram relative minimum : {'{:.3f}'.format(OOOO0O000OOOOOO00['params']['rel_min'])} {OOOO0OOOO0OO0O0O0}")#line:321
                print ("")#line:322
                print (f"Condition  : {OOOO0O000OOOOOO00['cedents_str']['cond']}")#line:323
                print ("")#line:324
                OOO0O0O00OO0OOOOO =O000O0O00OOOO0000 .get_category_names (O000O0O00OOOO0000 .result ["taskinfo"]["target"])#line:325
                print (f"Categories in target variable  {OOO0O0O00OO0OOOOO}")#line:326
                print (f"Histogram                      {OOOO0O000OOOOOO00['params']['hist']}")#line:327
                if ('aad'in OOOO0O000OOOOOO00 ['params']):#line:328
                    print (f"Histogram on full set          {OOOO0O000OOOOOO00['params']['hist_full']}")#line:329
                    print (f"Relative histogram             {OOOO0O000OOOOOO00['params']['rel_hist']}")#line:330
                    print (f"Relative histogram on full set {OOOO0O000OOOOOO00['params']['rel_hist_full']}")#line:331
            elif O000O0O00OOOO0000 .result ['taskinfo']['task_type']=="UICMiner":#line:332
                print ("")#line:333
                OOOO0O000OOOOOO00 =O000O0O00OOOO0000 .result ["rules"][O0OO0OOO0OOOOOO0O -1 ]#line:334
                print (f"Rule id : {OOOO0O000OOOOOO00['rule_id']}")#line:335
                print ("")#line:336
                OOOO0OOOO0OO0O0O0 =""#line:337
                if ('aad_score'in OOOO0O000OOOOOO00 ['params']):#line:338
                    OOOO0OOOO0OO0O0O0 ="aad score : "+str (OOOO0O000OOOOOO00 ['params']['aad_score'])#line:339
                print (f"Base : {'{:5d}'.format(OOOO0O000OOOOOO00['params']['base'])}  Relative base : {'{:.3f}'.format(OOOO0O000OOOOOO00['params']['rel_base'])}   {OOOO0OOOO0OO0O0O0}")#line:341
                print ("")#line:342
                print (f"Condition  : {OOOO0O000OOOOOO00['cedents_str']['cond']}")#line:343
                print (f"Antecedent : {OOOO0O000OOOOOO00['cedents_str']['ante']}")#line:344
                print ("")#line:345
                print (f"Histogram                                        {OOOO0O000OOOOOO00['params']['hist']}")#line:346
                if ('aad_score'in OOOO0O000OOOOOO00 ['params']):#line:347
                    print (f"Histogram on full set with condition             {OOOO0O000OOOOOO00['params']['hist_cond']}")#line:348
                    print (f"Relative histogram                               {OOOO0O000OOOOOO00['params']['rel_hist']}")#line:349
                    print (f"Relative histogram on full set with condition    {OOOO0O000OOOOOO00['params']['rel_hist_cond']}")#line:350
                OO0O0OOOOO00OO0O0 =O000O0O00OOOO0000 .result ['datalabels']['catnames'][O000O0O00OOOO0000 .result ['datalabels']['varname'].index (O000O0O00OOOO0000 .result ['taskinfo']['target'])]#line:351
                print (" ")#line:352
                print ("Interpretation:")#line:353
                for OO0O0O00O000OO0O0 in range (len (OO0O0OOOOO00OO0O0 )):#line:354
                  O00000O0O00OO0OOO =0 #line:355
                  if OOOO0O000OOOOOO00 ['params']['rel_hist'][OO0O0O00O000OO0O0 ]>0 :#line:356
                      O00000O0O00OO0OOO =OOOO0O000OOOOOO00 ['params']['rel_hist'][OO0O0O00O000OO0O0 ]/OOOO0O000OOOOOO00 ['params']['rel_hist_cond'][OO0O0O00O000OO0O0 ]#line:357
                  OOO0O0O00OO0000OO =''#line:358
                  if not (OOOO0O000OOOOOO00 ['cedents_str']['cond']=='---'):#line:359
                      OOO0O0O00OO0000OO ="For "+OOOO0O000OOOOOO00 ['cedents_str']['cond']+": "#line:360
                  print (f"    {OOO0O0O00OO0000OO}{O000O0O00OOOO0000.result['taskinfo']['target']}({OO0O0OOOOO00OO0O0[OO0O0O00O000OO0O0]}) has occurence {'{:.1%}'.format(OOOO0O000OOOOOO00['params']['rel_hist_cond'][OO0O0O00O000OO0O0])}, with antecedent it has occurence {'{:.1%}'.format(OOOO0O000OOOOOO00['params']['rel_hist'][OO0O0O00O000OO0O0])}, that is {'{:.3f}'.format(O00000O0O00OO0OOO)} times more.")#line:362
            elif O000O0O00OOOO0000 .result ['taskinfo']['task_type']=="SD4ftMiner":#line:363
                print ("")#line:364
                OOOO0O000OOOOOO00 =O000O0O00OOOO0000 .result ["rules"][O0OO0OOO0OOOOOO0O -1 ]#line:365
                print (f"Rule id : {OOOO0O000OOOOOO00['rule_id']}")#line:366
                print ("")#line:367
                print (f"Base1 : {'{:5d}'.format(OOOO0O000OOOOOO00['params']['base1'])} Base2 : {'{:5d}'.format(OOOO0O000OOOOOO00['params']['base2'])}  Relative base 1 : {'{:.3f}'.format(OOOO0O000OOOOOO00['params']['rel_base1'])} Relative base 2 : {'{:.3f}'.format(OOOO0O000OOOOOO00['params']['rel_base2'])} CONF1 : {'{:.3f}'.format(OOOO0O000OOOOOO00['params']['conf1'])}  CONF2 : {'{:+.3f}'.format(OOOO0O000OOOOOO00['params']['conf2'])}  Delta Conf : {'{:+.3f}'.format(OOOO0O000OOOOOO00['params']['deltaconf'])} Ratio Conf : {'{:+.3f}'.format(OOOO0O000OOOOOO00['params']['ratioconf'])}")#line:368
                print ("")#line:369
                print ("Cedents:")#line:370
                print (f"  antecedent : {OOOO0O000OOOOOO00['cedents_str']['ante']}")#line:371
                print (f"  succcedent : {OOOO0O000OOOOOO00['cedents_str']['succ']}")#line:372
                print (f"  condition  : {OOOO0O000OOOOOO00['cedents_str']['cond']}")#line:373
                print (f"  first set  : {OOOO0O000OOOOOO00['cedents_str']['frst']}")#line:374
                print (f"  second set : {OOOO0O000OOOOOO00['cedents_str']['scnd']}")#line:375
                print ("")#line:376
                print ("Fourfold tables:")#line:377
                print (f"FRST|  S  |  ¬S |  SCND|  S  |  ¬S |");#line:378
                print (f"----|-----|-----|  ----|-----|-----| ")#line:379
                print (f" A  |{'{:5d}'.format(OOOO0O000OOOOOO00['params']['fourfold1'][0])}|{'{:5d}'.format(OOOO0O000OOOOOO00['params']['fourfold1'][1])}|   A  |{'{:5d}'.format(OOOO0O000OOOOOO00['params']['fourfold2'][0])}|{'{:5d}'.format(OOOO0O000OOOOOO00['params']['fourfold2'][1])}|")#line:380
                print (f"----|-----|-----|  ----|-----|-----|")#line:381
                print (f"¬A  |{'{:5d}'.format(OOOO0O000OOOOOO00['params']['fourfold1'][2])}|{'{:5d}'.format(OOOO0O000OOOOOO00['params']['fourfold1'][3])}|  ¬A  |{'{:5d}'.format(OOOO0O000OOOOOO00['params']['fourfold2'][2])}|{'{:5d}'.format(OOOO0O000OOOOOO00['params']['fourfold2'][3])}|")#line:382
                print (f"----|-----|-----|  ----|-----|-----|")#line:383
            else :#line:384
                print ("Unsupported task type for rule details")#line:385
            print ("")#line:389
        else :#line:390
            print ("No such rule.")#line:391
    def get_ruletext (O0OOO0O0O00OOOO00 ,OO00OO00000000000 ):#line:393
        ""#line:399
        if not (O0OOO0O0O00OOOO00 ._is_calculated ()):#line:400
            print ("ERROR: Task has not been calculated.")#line:401
            return #line:402
        if OO00OO00000000000 <=0 or OO00OO00000000000 >O0OOO0O0O00OOOO00 .get_rulecount ():#line:403
            if O0OOO0O0O00OOOO00 .get_rulecount ()==0 :#line:404
                print ("No such rule. There are no rules in result.")#line:405
            else :#line:406
                print (f"No such rule ({OO00OO00000000000}). Available rules are 1 to {O0OOO0O0O00OOOO00.get_rulecount()}")#line:407
            return None #line:408
        OOO0OO0OO0O000O00 =""#line:409
        OO00O0OO0O0OOOO00 =O0OOO0O0O00OOOO00 .result ["rules"][OO00OO00000000000 -1 ]#line:410
        if O0OOO0O0O00OOOO00 .result ['taskinfo']['task_type']=="4ftMiner":#line:411
            OOO0OO0OO0O000O00 =OOO0OO0OO0O000O00 +" "+OO00O0OO0O0OOOO00 ["cedents_str"]["ante"]+" => "+OO00O0OO0O0OOOO00 ["cedents_str"]["succ"]+" | "+OO00O0OO0O0OOOO00 ["cedents_str"]["cond"]#line:413
        elif O0OOO0O0O00OOOO00 .result ['taskinfo']['task_type']=="UICMiner":#line:414
            OOO0OO0OO0O000O00 =OOO0OO0OO0O000O00 +"     "+OO00O0OO0O0OOOO00 ["cedents_str"]["ante"]+" => "+O0OOO0O0O00OOOO00 .result ['taskinfo']['target']+"(*) | "+OO00O0OO0O0OOOO00 ["cedents_str"]["cond"]#line:416
        elif O0OOO0O0O00OOOO00 .result ['taskinfo']['task_type']=="CFMiner":#line:417
            OOO0OO0OO0O000O00 =OOO0OO0OO0O000O00 +" "+OO00O0OO0O0OOOO00 ["cedents_str"]["cond"]#line:418
        elif O0OOO0O0O00OOOO00 .result ['taskinfo']['task_type']=="SD4ftMiner":#line:419
            OOO0OO0OO0O000O00 =OOO0OO0OO0O000O00 +"  "+OO00O0OO0O0OOOO00 ["cedents_str"]["ante"]+" => "+OO00O0OO0O0OOOO00 ["cedents_str"]["succ"]+" | "+OO00O0OO0O0OOOO00 ["cedents_str"]["cond"]+" : "+OO00O0OO0O0OOOO00 ["cedents_str"]["frst"]+" x "+OO00O0OO0O0OOOO00 ["cedents_str"]["scnd"]#line:421
        return OOO0OO0OO0O000O00 #line:422
    def _annotate_chart (OOOOO000OOOOO00O0 ,O0O0000OO000O00OO ,OOO0O00OOO000O00O ,cnt =2 ):#line:424
        ""#line:431
        OOO0O0OOO0O00000O =O0O0000OO000O00OO .axes .get_ylim ()#line:432
        for OOO0O0O0OO0O00O00 in O0O0000OO000O00OO .patches :#line:433
            OO0O0OOOOOO00000O ='{:.1f}%'.format (100 *OOO0O0O0OO0O00O00 .get_height ()/OOO0O00OOO000O00O )#line:434
            O0000O000O0O0O000 =OOO0O0O0OO0O00O00 .get_x ()+OOO0O0O0OO0O00O00 .get_width ()/4 #line:435
            OO0000OO00O00OOOO =OOO0O0O0OO0O00O00 .get_y ()+OOO0O0O0OO0O00O00 .get_height ()-OOO0O0OOO0O00000O [1 ]/8 #line:436
            if OOO0O0O0OO0O00O00 .get_height ()<OOO0O0OOO0O00000O [1 ]/8 :#line:437
                OO0000OO00O00OOOO =OOO0O0O0OO0O00O00 .get_y ()+OOO0O0O0OO0O00O00 .get_height ()+OOO0O0OOO0O00000O [1 ]*0.02 #line:438
            O0O0000OO000O00OO .annotate (OO0O0OOOOOO00000O ,(O0000O000O0O0O000 ,OO0000OO00O00OOOO ),size =23 /cnt )#line:439
    def draw_rule (O0O00OO000OOOO0O0 ,OO0000O0OOO00O0O0 ,show =True ,filename =None ):#line:441
        ""#line:447
        if not (O0O00OO000OOOO0O0 ._is_calculated ()):#line:448
            print ("ERROR: Task has not been calculated.")#line:449
            return #line:450
        print ("")#line:451
        if (OO0000O0OOO00O0O0 <=len (O0O00OO000OOOO0O0 .result ["rules"])):#line:452
            if O0O00OO000OOOO0O0 .result ['taskinfo']['task_type']=="4ftMiner":#line:453
                OO00OO00O00OOOO00 ,OOOO0O000OO000O0O =plt .subplots (2 ,2 )#line:455
                OO000000OOO0000OO =['S','not S']#line:456
                O00O0O0OOO00O0OOO =['A','not A']#line:457
                O0OOO0OO00O00O0O0 =O0O00OO000OOOO0O0 .get_fourfold (OO0000O0OOO00O0O0 )#line:458
                OO000000O00O0OO0O =[O0OOO0OO00O00O0O0 [0 ],O0OOO0OO00O00O0O0 [1 ]]#line:460
                O0OOOO0OO00O0OOO0 =[O0OOO0OO00O00O0O0 [2 ],O0OOO0OO00O00O0O0 [3 ]]#line:461
                O0OO00O0OO0O0OO00 =[O0OOO0OO00O00O0O0 [0 ]+O0OOO0OO00O00O0O0 [2 ],O0OOO0OO00O00O0O0 [1 ]+O0OOO0OO00O00O0O0 [3 ]]#line:462
                OOOO0O000OO000O0O [0 ,0 ]=sns .barplot (ax =OOOO0O000OO000O0O [0 ,0 ],x =OO000000OOO0000OO ,y =OO000000O00O0OO0O ,color ='lightsteelblue')#line:463
                O0O00OO000OOOO0O0 ._annotate_chart (OOOO0O000OO000O0O [0 ,0 ],O0OOO0OO00O00O0O0 [0 ]+O0OOO0OO00O00O0O0 [1 ])#line:465
                OOOO0O000OO000O0O [0 ,1 ]=sns .barplot (ax =OOOO0O000OO000O0O [0 ,1 ],x =OO000000OOO0000OO ,y =O0OO00O0OO0O0OO00 ,color ="gray",edgecolor ="black")#line:467
                O0O00OO000OOOO0O0 ._annotate_chart (OOOO0O000OO000O0O [0 ,1 ],sum (O0OOO0OO00O00O0O0 ))#line:469
                OOOO0O000OO000O0O [0 ,0 ].set (xlabel =None ,ylabel ='Count')#line:471
                OOOO0O000OO000O0O [0 ,1 ].set (xlabel =None ,ylabel ='Count')#line:472
                O000O0OO0O0OOO0O0 =sns .color_palette ("Blues",as_cmap =True )#line:474
                O000O0OOO00000OO0 =sns .color_palette ("Greys",as_cmap =True )#line:475
                OOOO0O000OO000O0O [1 ,0 ]=sns .heatmap (ax =OOOO0O000OO000O0O [1 ,0 ],data =[OO000000O00O0OO0O ,O0OOOO0OO00O0OOO0 ],xticklabels =OO000000OOO0000OO ,yticklabels =O00O0O0OOO00O0OOO ,annot =True ,cbar =False ,fmt =".0f",cmap =O000O0OO0O0OOO0O0 )#line:479
                OOOO0O000OO000O0O [1 ,0 ].set (xlabel =None ,ylabel ='Count')#line:481
                OOOO0O000OO000O0O [1 ,1 ]=sns .heatmap (ax =OOOO0O000OO000O0O [1 ,1 ],data =np .asarray ([O0OO00O0OO0O0OO00 ]),xticklabels =OO000000OOO0000OO ,yticklabels =False ,annot =True ,cbar =False ,fmt =".0f",cmap =O000O0OOO00000OO0 )#line:485
                OOOO0O000OO000O0O [1 ,1 ].set (xlabel =None ,ylabel ='Count')#line:487
                O0O0000O00000O0O0 =O0O00OO000OOOO0O0 .result ["rules"][OO0000O0OOO00O0O0 -1 ]['cedents_str']['ante']#line:489
                OOOO0O000OO000O0O [0 ,0 ].set (title ="\n".join (wrap (O0O0000O00000O0O0 ,30 )))#line:490
                OOOO0O000OO000O0O [0 ,1 ].set (title ='Entire dataset')#line:491
                O0000OO00OO0O00OO =O0O00OO000OOOO0O0 .result ["rules"][OO0000O0OOO00O0O0 -1 ]['cedents_str']#line:493
                OO00OO00O00OOOO00 .suptitle ("Antecedent : "+O0000OO00OO0O00OO ['ante']+"\nSuccedent : "+O0000OO00OO0O00OO ['succ']+"\nCondition : "+O0000OO00OO0O00OO ['cond'],x =0 ,ha ='left',size ='small')#line:497
                OO00OO00O00OOOO00 .tight_layout ()#line:498
            elif O0O00OO000OOOO0O0 .result ['taskinfo']['task_type']=="SD4ftMiner":#line:500
                OO00OO00O00OOOO00 ,OOOO0O000OO000O0O =plt .subplots (2 ,2 )#line:502
                OO000000OOO0000OO =['S','not S']#line:503
                O00O0O0OOO00O0OOO =['A','not A']#line:504
                OOO0O00OO0O00000O =O0O00OO000OOOO0O0 .get_fourfold (OO0000O0OOO00O0O0 ,order =1 )#line:506
                OO0O0O0OO000O0O0O =O0O00OO000OOOO0O0 .get_fourfold (OO0000O0OOO00O0O0 ,order =2 )#line:507
                OOO0O00OOO0O0O00O =[OOO0O00OO0O00000O [0 ],OOO0O00OO0O00000O [1 ]]#line:509
                OO00O000O0OOOO000 =[OOO0O00OO0O00000O [2 ],OOO0O00OO0O00000O [3 ]]#line:510
                OOO0O00O00OOOO00O =[OOO0O00OO0O00000O [0 ]+OOO0O00OO0O00000O [2 ],OOO0O00OO0O00000O [1 ]+OOO0O00OO0O00000O [3 ]]#line:511
                OO00OOOO0OOOO000O =[OO0O0O0OO000O0O0O [0 ],OO0O0O0OO000O0O0O [1 ]]#line:512
                O0O0000O000OOO0O0 =[OO0O0O0OO000O0O0O [2 ],OO0O0O0OO000O0O0O [3 ]]#line:513
                OOO0O00OOOOO0OO0O =[OO0O0O0OO000O0O0O [0 ]+OO0O0O0OO000O0O0O [2 ],OO0O0O0OO000O0O0O [1 ]+OO0O0O0OO000O0O0O [3 ]]#line:514
                OOOO0O000OO000O0O [0 ,0 ]=sns .barplot (ax =OOOO0O000OO000O0O [0 ,0 ],x =OO000000OOO0000OO ,y =OOO0O00OOO0O0O00O ,color ='orange')#line:515
                O0O00OO000OOOO0O0 ._annotate_chart (OOOO0O000OO000O0O [0 ,0 ],OOO0O00OO0O00000O [0 ]+OOO0O00OO0O00000O [1 ])#line:517
                OOOO0O000OO000O0O [0 ,1 ]=sns .barplot (ax =OOOO0O000OO000O0O [0 ,1 ],x =OO000000OOO0000OO ,y =OO00OOOO0OOOO000O ,color ="green")#line:519
                O0O00OO000OOOO0O0 ._annotate_chart (OOOO0O000OO000O0O [0 ,1 ],OO0O0O0OO000O0O0O [0 ]+OO0O0O0OO000O0O0O [1 ])#line:521
                OOOO0O000OO000O0O [0 ,0 ].set (xlabel =None ,ylabel ='Count')#line:523
                OOOO0O000OO000O0O [0 ,1 ].set (xlabel =None ,ylabel ='Count')#line:524
                O000O0OO0O0OOO0O0 =sns .color_palette ("Oranges",as_cmap =True )#line:526
                O000O0OOO00000OO0 =sns .color_palette ("Greens",as_cmap =True )#line:527
                OOOO0O000OO000O0O [1 ,0 ]=sns .heatmap (ax =OOOO0O000OO000O0O [1 ,0 ],data =[OOO0O00OOO0O0O00O ,OO00O000O0OOOO000 ],xticklabels =OO000000OOO0000OO ,yticklabels =O00O0O0OOO00O0OOO ,annot =True ,cbar =False ,fmt =".0f",cmap =O000O0OO0O0OOO0O0 )#line:530
                OOOO0O000OO000O0O [1 ,0 ].set (xlabel =None ,ylabel ='Count')#line:532
                OOOO0O000OO000O0O [1 ,1 ]=sns .heatmap (ax =OOOO0O000OO000O0O [1 ,1 ],data =[OO00OOOO0OOOO000O ,O0O0000O000OOO0O0 ],xticklabels =OO000000OOO0000OO ,yticklabels =False ,annot =True ,cbar =False ,fmt =".0f",cmap =O000O0OOO00000OO0 )#line:536
                OOOO0O000OO000O0O [1 ,1 ].set (xlabel =None ,ylabel ='Count')#line:538
                O0O0000O00000O0O0 =O0O00OO000OOOO0O0 .result ["rules"][OO0000O0OOO00O0O0 -1 ]['cedents_str']['frst']#line:540
                OOOO0O000OO000O0O [0 ,0 ].set (title ="\n".join (wrap (O0O0000O00000O0O0 ,30 )))#line:541
                O0O0OOO0O00O0000O =O0O00OO000OOOO0O0 .result ["rules"][OO0000O0OOO00O0O0 -1 ]['cedents_str']['scnd']#line:542
                OOOO0O000OO000O0O [0 ,1 ].set (title ="\n".join (wrap (O0O0OOO0O00O0000O ,30 )))#line:543
                O0000OO00OO0O00OO =O0O00OO000OOOO0O0 .result ["rules"][OO0000O0OOO00O0O0 -1 ]['cedents_str']#line:545
                OO00OO00O00OOOO00 .suptitle ("Antecedent : "+O0000OO00OO0O00OO ['ante']+"\nSuccedent : "+O0000OO00OO0O00OO ['succ']+"\nCondition : "+O0000OO00OO0O00OO ['cond']+"\nFirst : "+O0000OO00OO0O00OO ['frst']+"\nSecond : "+O0000OO00OO0O00OO ['scnd'],x =0 ,ha ='left',size ='small')#line:550
                OO00OO00O00OOOO00 .tight_layout ()#line:552
            elif (O0O00OO000OOOO0O0 .result ['taskinfo']['task_type']=="CFMiner")or (O0O00OO000OOOO0O0 .result ['taskinfo']['task_type']=="UICMiner"):#line:555
                OO0OOOOOOOOOO0OOO =O0O00OO000OOOO0O0 .result ['taskinfo']['task_type']=="UICMiner"#line:556
                OO00OO00O00OOOO00 ,OOOO0O000OO000O0O =plt .subplots (2 ,2 ,gridspec_kw ={'height_ratios':[3 ,1 ]})#line:557
                OO0O0OOO000O00OOO =O0O00OO000OOOO0O0 .result ['taskinfo']['target']#line:558
                OO000000OOO0000OO =O0O00OO000OOOO0O0 .result ['datalabels']['catnames'][O0O00OO000OOOO0O0 .result ['datalabels']['varname'].index (O0O00OO000OOOO0O0 .result ['taskinfo']['target'])]#line:560
                O0OO000O0OO0OO0O0 =O0O00OO000OOOO0O0 .result ["rules"][OO0000O0OOO00O0O0 -1 ]#line:561
                OOOOO0OOO0O0O0OO0 =O0O00OO000OOOO0O0 .get_hist (OO0000O0OOO00O0O0 )#line:562
                if OO0OOOOOOOOOO0OOO :#line:563
                    OOOOO0OOO0O0O0OO0 =O0OO000O0OO0OO0O0 ['params']['hist']#line:564
                else :#line:565
                    OOOOO0OOO0O0O0OO0 =O0O00OO000OOOO0O0 .get_hist (OO0000O0OOO00O0O0 )#line:566
                OOOO0O000OO000O0O [0 ,0 ]=sns .barplot (ax =OOOO0O000OO000O0O [0 ,0 ],x =OO000000OOO0000OO ,y =OOOOO0OOO0O0O0OO0 ,color ='lightsteelblue')#line:567
                OOO00O00OO0OO0O0O =[]#line:569
                OOO0OOOO0OO0O0O0O =[]#line:570
                if OO0OOOOOOOOOO0OOO :#line:571
                    OOO00O00OO0OO0O0O =OO000000OOO0000OO #line:572
                    OOO0OOOO0OO0O0O0O =O0O00OO000OOOO0O0 .get_hist (OO0000O0OOO00O0O0 ,fullCond =True )#line:573
                else :#line:574
                    OOO00O00OO0OO0O0O =O0O00OO000OOOO0O0 .profiles ['hist_target_entire_dataset_labels']#line:575
                    OOO0OOOO0OO0O0O0O =O0O00OO000OOOO0O0 .profiles ['hist_target_entire_dataset_values']#line:576
                OOOO0O000OO000O0O [0 ,1 ]=sns .barplot (ax =OOOO0O000OO000O0O [0 ,1 ],x =OOO00O00OO0OO0O0O ,y =OOO0OOOO0OO0O0O0O ,color ="gray",edgecolor ="black")#line:577
                O0O00OO000OOOO0O0 ._annotate_chart (OOOO0O000OO000O0O [0 ,0 ],sum (OOOOO0OOO0O0O0OO0 ),len (OOOOO0OOO0O0O0OO0 ))#line:579
                O0O00OO000OOOO0O0 ._annotate_chart (OOOO0O000OO000O0O [0 ,1 ],sum (OOO0OOOO0OO0O0O0O ),len (OOO0OOOO0OO0O0O0O ))#line:580
                OOOO0O000OO000O0O [0 ,0 ].set (xlabel =None ,ylabel ='Count')#line:582
                OOOO0O000OO000O0O [0 ,1 ].set (xlabel =None ,ylabel ='Count')#line:583
                OOO0OO0OO000000O0 =[OO000000OOO0000OO ,OOOOO0OOO0O0O0OO0 ]#line:585
                OOO0O0O0OOO00O0OO =pd .DataFrame (OOO0OO0OO000000O0 ).transpose ()#line:586
                OOO0O0O0OOO00O0OO .columns =[OO0O0OOO000O00OOO ,'No of observatios']#line:587
                O000O0OO0O0OOO0O0 =sns .color_palette ("Blues",as_cmap =True )#line:589
                O000O0OOO00000OO0 =sns .color_palette ("Greys",as_cmap =True )#line:590
                OOOO0O000OO000O0O [1 ,0 ]=sns .heatmap (ax =OOOO0O000OO000O0O [1 ,0 ],data =np .asarray ([OOOOO0OOO0O0O0OO0 ]),xticklabels =OO000000OOO0000OO ,yticklabels =False ,annot =True ,cbar =False ,fmt =".0f",cmap =O000O0OO0O0OOO0O0 )#line:594
                OOOO0O000OO000O0O [1 ,0 ].set (xlabel =OO0O0OOO000O00OOO ,ylabel ='Count')#line:596
                OOOO0O000OO000O0O [1 ,1 ]=sns .heatmap (ax =OOOO0O000OO000O0O [1 ,1 ],data =np .asarray ([OOO0OOOO0OO0O0O0O ]),xticklabels =OOO00O00OO0OO0O0O ,yticklabels =False ,annot =True ,cbar =False ,fmt =".0f",cmap =O000O0OOO00000OO0 )#line:600
                OOOO0O000OO000O0O [1 ,1 ].set (xlabel =OO0O0OOO000O00OOO ,ylabel ='Count')#line:602
                OO0O0O00000OOOOO0 =""#line:603
                O0OO00O0OOOOOOOO0 ='Entire dataset'#line:604
                if OO0OOOOOOOOOO0OOO :#line:605
                    if len (O0OO000O0OO0OO0O0 ['cedents_struct']['cond'])>0 :#line:606
                        O0OO00O0OOOOOOOO0 =O0OO000O0OO0OO0O0 ['cedents_str']['cond']#line:607
                        OO0O0O00000OOOOO0 =" & "+O0OO000O0OO0OO0O0 ['cedents_str']['cond']#line:608
                OOOO0O000OO000O0O [0 ,1 ].set (title =O0OO00O0OOOOOOOO0 )#line:609
                if OO0OOOOOOOOOO0OOO :#line:610
                    O0O0000O00000O0O0 =O0O00OO000OOOO0O0 .result ["rules"][OO0000O0OOO00O0O0 -1 ]['cedents_str']['ante']+OO0O0O00000OOOOO0 #line:611
                else :#line:612
                    O0O0000O00000O0O0 =O0O00OO000OOOO0O0 .result ["rules"][OO0000O0OOO00O0O0 -1 ]['cedents_str']['cond']#line:613
                OOOO0O000OO000O0O [0 ,0 ].set (title ="\n".join (wrap (O0O0000O00000O0O0 ,30 )))#line:614
                O0000OO00OO0O00OO =O0O00OO000OOOO0O0 .result ["rules"][OO0000O0OOO00O0O0 -1 ]['cedents_str']#line:616
                O0OO00O0OOOOOOOO0 ="Condition : "+O0000OO00OO0O00OO ['cond']#line:617
                if OO0OOOOOOOOOO0OOO :#line:618
                    O0OO00O0OOOOOOOO0 =O0OO00O0OOOOOOOO0 +"\nAntecedent : "+O0000OO00OO0O00OO ['ante']#line:619
                OO00OO00O00OOOO00 .suptitle (O0OO00O0OOOOOOOO0 ,x =0 ,ha ='left',size ='small')#line:620
                OO00OO00O00OOOO00 .tight_layout ()#line:622
            else :#line:623
                print ("Unsupported task type for rule details")#line:624
                return #line:625
            if filename is not None :#line:626
                plt .savefig (filename =filename )#line:627
            if show :#line:628
                plt .show ()#line:629
            print ("")#line:631
        else :#line:632
            print ("No such rule.")#line:633
    def get_rulecount (O0O00OO0000O0O00O ):#line:635
        ""#line:640
        if not (O0O00OO0000O0O00O ._is_calculated ()):#line:641
            print ("ERROR: Task has not been calculated.")#line:642
            return #line:643
        return len (O0O00OO0000O0O00O .result ["rules"])#line:644
    def get_fourfold (O0O0O0OOO0000OOOO ,OO0000O00000O0O0O ,order =0 ):#line:646
        ""#line:653
        if not (O0O0O0OOO0000OOOO ._is_calculated ()):#line:654
            print ("ERROR: Task has not been calculated.")#line:655
            return #line:656
        if (OO0000O00000O0O0O <=len (O0O0O0OOO0000OOOO .result ["rules"])):#line:657
            if O0O0O0OOO0000OOOO .result ['taskinfo']['task_type']=="4ftMiner":#line:658
                OOOOOO0O000OOOOO0 =O0O0O0OOO0000OOOO .result ["rules"][OO0000O00000O0O0O -1 ]#line:659
                return OOOOOO0O000OOOOO0 ['params']['fourfold']#line:660
            elif O0O0O0OOO0000OOOO .result ['taskinfo']['task_type']=="CFMiner":#line:661
                print ("Error: fourfold for CFMiner is not defined")#line:662
                return None #line:663
            elif O0O0O0OOO0000OOOO .result ['taskinfo']['task_type']=="SD4ftMiner":#line:664
                OOOOOO0O000OOOOO0 =O0O0O0OOO0000OOOO .result ["rules"][OO0000O00000O0O0O -1 ]#line:665
                if order ==1 :#line:666
                    return OOOOOO0O000OOOOO0 ['params']['fourfold1']#line:667
                if order ==2 :#line:668
                    return OOOOOO0O000OOOOO0 ['params']['fourfold2']#line:669
                print ("Error: for SD4ft-Miner, you need to provide order of fourfold table in order= parameter (valid values are 1,2).")#line:670
                return None #line:671
            else :#line:672
                print ("Unsupported task type for rule details")#line:673
        else :#line:674
            print ("No such rule.")#line:675
    def get_hist (OOOOOO0O0O00O0O0O ,OOO000O0OO0000O00 ,fullCond =True ):#line:677
        ""#line:684
        if not (OOOOOO0O0O00O0O0O ._is_calculated ()):#line:685
            print ("ERROR: Task has not been calculated.")#line:686
            return #line:687
        if (OOO000O0OO0000O00 <=len (OOOOOO0O0O00O0O0O .result ["rules"])):#line:688
            if OOOOOO0O0O00O0O0O .result ['taskinfo']['task_type']=="CFMiner":#line:689
                O00O00OOO00OOO00O =OOOOOO0O0O00O0O0O .result ["rules"][OOO000O0OO0000O00 -1 ]#line:690
                return O00O00OOO00OOO00O ['params']['hist']#line:691
            elif OOOOOO0O0O00O0O0O .result ['taskinfo']['task_type']=="UICMiner":#line:692
                O00O00OOO00OOO00O =OOOOOO0O0O00O0O0O .result ["rules"][OOO000O0OO0000O00 -1 ]#line:693
                OOOO00OOO00000O0O =None #line:694
                if fullCond :#line:695
                    OOOO00OOO00000O0O =O00O00OOO00OOO00O ['params']['hist_cond']#line:696
                else :#line:697
                    OOOO00OOO00000O0O =O00O00OOO00OOO00O ['params']['hist']#line:698
                return OOOO00OOO00000O0O #line:699
            elif OOOOOO0O0O00O0O0O .result ['taskinfo']['task_type']=="SD4ftMiner":#line:700
                print ("Error: SD4ft-Miner has no histogram")#line:701
                return None #line:702
            elif OOOOOO0O0O00O0O0O .result ['taskinfo']['task_type']=="4ftMiner":#line:703
                print ("Error: 4ft-Miner has no histogram")#line:704
                return None #line:705
            else :#line:706
                print ("Unsupported task type for rule details")#line:707
        else :#line:708
            print ("No such rule.")#line:709
    def get_hist_cond (O0O0OOO00O0O000OO ,OO0O0O0O000O00OO0 ):#line:712
        ""#line:718
        if not (O0O0OOO00O0O000OO ._is_calculated ()):#line:719
            print ("ERROR: Task has not been calculated.")#line:720
            return #line:721
        if (OO0O0O0O000O00OO0 <=len (O0O0OOO00O0O000OO .result ["rules"])):#line:723
            if O0O0OOO00O0O000OO .result ['taskinfo']['task_type']=="UICMiner":#line:724
                O0OOO00OO0OOO00OO =O0O0OOO00O0O000OO .result ["rules"][OO0O0O0O000O00OO0 -1 ]#line:725
                return O0OOO00OO0OOO00OO ['params']['hist_cond']#line:726
            elif O0O0OOO00O0O000OO .result ['taskinfo']['task_type']=="CFMiner":#line:727
                O0OOO00OO0OOO00OO =O0O0OOO00O0O000OO .result ["rules"][OO0O0O0O000O00OO0 -1 ]#line:728
                return O0OOO00OO0OOO00OO ['params']['hist']#line:729
            elif O0O0OOO00O0O000OO .result ['taskinfo']['task_type']=="SD4ftMiner":#line:730
                print ("Error: SD4ft-Miner has no histogram")#line:731
                return None #line:732
            elif O0O0OOO00O0O000OO .result ['taskinfo']['task_type']=="4ftMiner":#line:733
                print ("Error: 4ft-Miner has no histogram")#line:734
                return None #line:735
            else :#line:736
                print ("Unsupported task type for rule details")#line:737
        else :#line:738
            print ("No such rule.")#line:739
    def get_quantifiers (OOOOOO000O0O0O0O0 ,OO0OOOOOOO000000O ,order =0 ):#line:741
        ""#line:750
        if not (OOOOOO000O0O0O0O0 ._is_calculated ()):#line:751
            print ("ERROR: Task has not been calculated.")#line:752
            return None #line:753
        if (OO0OOOOOOO000000O <=len (OOOOOO000O0O0O0O0 .result ["rules"])):#line:755
            OOO0OO000O0O00O0O =OOOOOO000O0O0O0O0 .result ["rules"][OO0OOOOOOO000000O -1 ]#line:756
            if OOOOOO000O0O0O0O0 .result ['taskinfo']['task_type']=="4ftMiner":#line:757
                return OOO0OO000O0O00O0O ['params']#line:758
            elif OOOOOO000O0O0O0O0 .result ['taskinfo']['task_type']=="CFMiner":#line:759
                return OOO0OO000O0O00O0O ['params']#line:760
            elif OOOOOO000O0O0O0O0 .result ['taskinfo']['task_type']=="SD4ftMiner":#line:761
                return OOO0OO000O0O00O0O ['params']#line:762
            else :#line:763
                print ("Unsupported task type for rule details")#line:764
        else :#line:765
            print ("No such rule.")#line:766
    def get_varlist (O0OOO0O00O0000OO0 ):#line:768
        ""#line:772
        return O0OOO0O00O0000OO0 .result ["datalabels"]["varname"]#line:774
    def get_category_names (OO0OOO0000O000000 ,varname =None ,varindex =None ):#line:776
        ""#line:783
        OO00O000000OO000O =0 #line:784
        if varindex is not None :#line:785
            if OO00O000000OO000O >=0 &OO00O000000OO000O <len (OO0OOO0000O000000 .get_varlist ()):#line:786
                OO00O000000OO000O =varindex #line:787
            else :#line:788
                print ("Error: no such variable.")#line:789
                return #line:790
        if (varname is not None ):#line:791
            OOO0O00000O0O0000 =OO0OOO0000O000000 .get_varlist ()#line:792
            OO00O000000OO000O =OOO0O00000O0O0000 .index (varname )#line:793
            if OO00O000000OO000O ==-1 |OO00O000000OO000O <0 |OO00O000000OO000O >=len (OO0OOO0000O000000 .get_varlist ()):#line:794
                print ("Error: no such variable.")#line:795
                return #line:796
        return OO0OOO0000O000000 .result ["datalabels"]["catnames"][OO00O000000OO000O ]#line:797
    def print_data_definition (O0O0OO0OOO000OO0O ):#line:799
        ""#line:802
        OO00O00OO0OOOOO0O =O0O0OO0OOO000OO0O .get_varlist ()#line:803
        print (f"Dataset has {len(OO00O00OO0OOOOO0O)} variables.")#line:804
        for OO00O0OO000000OOO in OO00O00OO0OOOOO0O :#line:805
            OOO0000OO0OOO000O =O0O0OO0OOO000OO0O .get_category_names (OO00O0OO000000OOO )#line:806
            O0O0O00OOOOO0O0OO =""#line:807
            for O00O0O00O0O0000O0 in OOO0000OO0OOO000O :#line:808
                O0O0O00OOOOO0O0OO =O0O0O00OOOOO0O0OO +str (O00O0O00O0O0000O0 )+" "#line:809
            O0O0O00OOOOO0O0OO =O0O0O00OOOOO0O0OO [:-1 ]#line:810
            print (f"Variable {OO00O0OO000000OOO} has {len(OOO0000OO0OOO000O)} categories: {O0O0O00OOOOO0O0OO}")#line:811
    def _is_calculated (OOOO00OO0000000O0 ):#line:813
        ""#line:818
        OO00O0OO0OOOO0O0O =False #line:819
        if 'taskinfo'in OOOO00OO0000000O0 .result :#line:820
            OO00O0OO0OOOO0O0O =True #line:821
        return OO00O0OO0OOOO0O0O #line:822
    def save (OOO0000O000O000O0 ,O00OOO0OOO00O0O0O ,savedata =False ,embeddata =True ,fmt ='pickle'):#line:824
        if not (OOO0000O000O000O0 ._is_calculated ()):#line:825
            print ("ERROR: Task has not been calculated.")#line:826
            return None #line:827
        O000000O0O000O000 ={'program':'CleverMiner','version':OOO0000O000O000O0 .get_version_string ()}#line:828
        O00O0OOO0O000O0OO ={}#line:829
        O00O0OOO0O000O0OO ['control']=O000000O0O000O000 #line:830
        O00O0OOO0O000O0OO ['result']=OOO0000O000O000O0 .result #line:831
        O00O0OOO0O000O0OO ['stats']=OOO0000O000O000O0 .stats #line:832
        O00O0OOO0O000O0OO ['options']=OOO0000O000O000O0 .options #line:833
        O00O0OOO0O000O0OO ['profiles']=OOO0000O000O000O0 .profiles #line:834
        if savedata :#line:835
            if embeddata :#line:836
                O00O0OOO0O000O0OO ['data']=OOO0000O000O000O0 .data #line:837
                O00O0OOO0O000O0OO ['df']=OOO0000O000O000O0 .df #line:838
            else :#line:839
                O0O0OOO0OO0OO00OO ={}#line:840
                O0O0OOO0OO0OO00OO ['data']=OOO0000O000O000O0 .data #line:841
                O0O0OOO0OO0OO00OO ['df']=OOO0000O000O000O0 .df #line:842
                print (f"CALC HASH {datetime.now()}")#line:843
                O0OOOOO00O00OO00O =OOO0000O000O000O0 ._get_fast_hash (O0O0OOO0OO0OO00OO )#line:844
                print (f"CALC HASH ...done {datetime.now()}")#line:845
                O0OOO000OOO00O0OO =os .path .join (OOO0000O000O000O0 .cache_dir ,O0OOOOO00O00OO00O +'.clmdata')#line:846
                OOOO0OO00000000OO =open (O0OOO000OOO00O0OO ,'wb')#line:847
                pickle .dump (O0O0OOO0OO0OO00OO ,OOOO0OO00000000OO ,protocol =pickle .HIGHEST_PROTOCOL )#line:848
                O00O0OOO0O000O0OO ['datafile']=O0OOO000OOO00O0OO #line:849
        if fmt =='pickle':#line:850
            O00000O00O000O0O0 =open (O00OOO0OOO00O0O0O ,'wb')#line:851
            pickle .dump (O00O0OOO0O000O0OO ,O00000O00O000O0O0 ,protocol =pickle .HIGHEST_PROTOCOL )#line:852
        elif fmt =='json':#line:853
            O00000O00O000O0O0 =open (O00OOO0OOO00O0O0O ,'w')#line:854
            json .dump (O00O0OOO0O000O0OO ,O00000O00O000O0O0 )#line:855
        else :#line:856
            print (f"Unsupported format - {fmt}. Supported formats are pickle, json.")#line:857
    def load (OOO00O00O0OOO0O0O ,O00OOO000OOO000O0 ,fmt ='pickle'):#line:859
        O000OOO000OO0O0OO =False #line:860
        if '://'in O00OOO000OOO000O0 :#line:861
            O000OOO000OO0O0OO =True #line:862
        if fmt =='pickle':#line:863
            if O000OOO000OO0O0OO :#line:864
                OOOO0000O000O0000 =pickle .load (urllib .request .urlopen (O00OOO000OOO000O0 ))#line:865
            else :#line:866
                OOO0OOOO0O0OO0O0O =open (O00OOO000OOO000O0 ,'rb')#line:867
                OOOO0000O000O0000 =pickle .load (OOO0OOOO0O0OO0O0O )#line:868
        elif fmt =='json':#line:869
            if O000OOO000OO0O0OO :#line:870
                OOOO0000O000O0000 =json .load (urllib .request .urlopen (O00OOO000OOO000O0 ))#line:871
            else :#line:872
                OOO0OOOO0O0OO0O0O =open (O00OOO000OOO000O0 ,'r')#line:873
                OOOO0000O000O0000 =json .load (OOO0OOOO0O0OO0O0O )#line:874
        else :#line:875
            print (f"Unsupported format - {fmt}. Supported formats are pickle, json.")#line:876
            return #line:877
        if not 'control'in OOOO0000O000O0000 :#line:878
            print ('Error: not a CleverMiner save file (1)')#line:879
            return None #line:880
        O00OO000OO00O0OO0 =OOOO0000O000O0000 ['control']#line:881
        if not ('program'in O00OO000OO00O0OO0 )or not ('version'in O00OO000OO00O0OO0 ):#line:882
            print ('Error: not a CleverMiner save file (2)')#line:883
            return None #line:884
        if not (O00OO000OO00O0OO0 ['program']=='CleverMiner'):#line:885
            print ('Error: not a CleverMiner save file (3)')#line:886
            return None #line:887
        OOO00O00O0OOO0O0O .result =OOOO0000O000O0000 ['result']#line:888
        OOO00O00O0OOO0O0O .stats =OOOO0000O000O0000 ['stats']#line:889
        OOO00O00O0OOO0O0O .options =OOOO0000O000O0000 ['options']#line:890
        if 'profiles'in OOOO0000O000O0000 :#line:891
            OOO00O00O0OOO0O0O .profiles =OOOO0000O000O0000 ['profiles']#line:892
        if 'data'in OOOO0000O000O0000 :#line:893
            OOO00O00O0OOO0O0O .data =OOOO0000O000O0000 ['data']#line:894
            OOO00O00O0OOO0O0O ._initialized =True #line:895
        if 'df'in OOOO0000O000O0000 :#line:896
            OOO00O00O0OOO0O0O .df =OOOO0000O000O0000 ['df']#line:897
        if 'datafile'in OOOO0000O000O0000 :#line:898
            try :#line:899
                O000O0OO0O000OOOO =open (OOOO0000O000O0000 ['datafile'],'rb')#line:900
                OO0OOOOOO00000O00 =pickle .load (O000O0OO0O000OOOO )#line:901
                OOO00O00O0OOO0O0O .data =OO0OOOOOO00000O00 ['data']#line:902
                OOO00O00O0OOO0O0O .df =OO0OOOOOO00000O00 ['df']#line:903
                print (f"...data loaded from file {OOOO0000O000O0000['datafile']}.")#line:904
            except :#line:905
                print (f"Error loading saved file. Linked data file does not exists or it is in incorrect structure or path. If you are transferring saved file to another computer, please embed also data.")#line:907
                exit (1 )#line:908
        print (f"File {O00OOO000OOO000O0} loaded ok.")#line:909
    def get_version_string (O00000OO0O00OOOOO ):#line:911
        ""#line:916
        return O00000OO0O00OOOOO .version_string #line:917
    def get_rule_cedent_list (O000OO0O00O0O0OO0 ,O00000000OO00O000 ):#line:919
        ""#line:925
        if not (O000OO0O00O0O0OO0 ._is_calculated ()):#line:926
            print ("ERROR: Task has not been calculated.")#line:927
            return #line:928
        if O00000000OO00O000 <=0 or O00000000OO00O000 >O000OO0O00O0O0OO0 .get_rulecount ():#line:929
            if O000OO0O00O0O0OO0 .get_rulecount ()==0 :#line:930
                print ("No such rule. There are no rules in result.")#line:931
            else :#line:932
                print (f"No such rule ({O00000000OO00O000}). Available rules are 1 to {O000OO0O00O0O0OO0.get_rulecount()}")#line:933
            return None #line:934
        OOOOO00OO00O0O000 =[]#line:935
        O000O0000OOOO0O0O =O000OO0O00O0O0OO0 .result ["rules"][O00000000OO00O000 -1 ]#line:936
        OOOOO00OO00O0O000 =list (O000O0000OOOO0O0O ['trace_cedent_dataorder'].keys ())#line:937
        return OOOOO00OO00O0O000 #line:939
    def get_rule_variables (OOO0OOOO0OO00OO00 ,O000OO0O00OOO0OOO ,O0O000O000OOOOOOO ,get_names =True ):#line:942
        ""#line:950
        if not (OOO0OOOO0OO00OO00 ._is_calculated ()):#line:951
            print ("ERROR: Task has not been calculated.")#line:952
            return #line:953
        if O000OO0O00OOO0OOO <=0 or O000OO0O00OOO0OOO >OOO0OOOO0OO00OO00 .get_rulecount ():#line:954
            if OOO0OOOO0OO00OO00 .get_rulecount ()==0 :#line:955
                print ("No such rule. There are no rules in result.")#line:956
            else :#line:957
                print (f"No such rule ({O000OO0O00OOO0OOO}). Available rules are 1 to {OOO0OOOO0OO00OO00.get_rulecount()}")#line:958
            return None #line:959
        O00OOO0O0OO00000O =[]#line:960
        OO00O0O00OOO00OOO =OOO0OOOO0OO00OO00 .result ["rules"][O000OO0O00OOO0OOO -1 ]#line:961
        O000OOO0O0OO0O00O =OOO0OOOO0OO00OO00 .result ["datalabels"]['varname']#line:962
        if not (O0O000O000OOOOOOO in OO00O0O00OOO00OOO ['trace_cedent_dataorder']):#line:963
            print (f"ERROR: cedent {O0O000O000OOOOOOO} not in result.")#line:964
            exit (1 )#line:965
        for O00OO000O000O0OOO in OO00O0O00OOO00OOO ['trace_cedent_dataorder'][O0O000O000OOOOOOO ]:#line:966
            if get_names :#line:967
                O00OOO0O0OO00000O .append (O000OOO0O0OO0O00O [O00OO000O000O0OOO ])#line:968
            else :#line:969
                O00OOO0O0OO00000O .append (O00OO000O000O0OOO )#line:970
        return O00OOO0O0OO00000O #line:972
    def get_rule_categories (O0OOO00O0000OOOOO ,OO0O00O0O0O000OOO ,O0O0OO00O0OOO00O0 ,OOOOO00000000OOO0 ,get_names =True ):#line:975
        ""#line:984
        if not (O0OOO00O0000OOOOO ._is_calculated ()):#line:985
            print ("ERROR: Task has not been calculated.")#line:986
            return #line:987
        if OO0O00O0O0O000OOO <=0 or OO0O00O0O0O000OOO >O0OOO00O0000OOOOO .get_rulecount ():#line:988
            if O0OOO00O0000OOOOO .get_rulecount ()==0 :#line:989
                print ("No such rule. There are no rules in result.")#line:990
            else :#line:991
                print (f"No such rule ({OO0O00O0O0O000OOO}). Available rules are 1 to {O0OOO00O0000OOOOO.get_rulecount()}")#line:992
            return None #line:993
        O00OOOO0O0O0OOO0O =[]#line:994
        OO0O000O0OOO00O00 =O0OOO00O0000OOOOO .result ["rules"][OO0O00O0O0O000OOO -1 ]#line:995
        O0O000O00O000OO00 =O0OOO00O0000OOOOO .result ["datalabels"]['varname']#line:996
        if OOOOO00000000OOO0 in O0O000O00O000OO00 :#line:997
            O00O0OO0O00O0OO0O =O0O000O00O000OO00 .index (OOOOO00000000OOO0 )#line:998
            O00O00O0OO0OO0000 =O0OOO00O0000OOOOO .result ['datalabels']['catnames'][O00O0OO0O00O0OO0O ]#line:999
            if not (O0O0OO00O0OOO00O0 in OO0O000O0OOO00O00 ['trace_cedent_dataorder']):#line:1000
                print (f"ERROR: cedent {O0O0OO00O0OOO00O0} not in result.")#line:1001
                exit (1 )#line:1002
            OO00O00OOO0OO00O0 =OO0O000O0OOO00O00 ['trace_cedent_dataorder'][O0O0OO00O0OOO00O0 ].index (O00O0OO0O00O0OO0O )#line:1003
            for O00O00O000O000000 in OO0O000O0OOO00O00 ['traces'][O0O0OO00O0OOO00O0 ][OO00O00OOO0OO00O0 ]:#line:1004
                if get_names :#line:1005
                    O00OOOO0O0O0OOO0O .append (O00O00O0OO0OO0000 [O00O00O000O000000 ])#line:1006
                else :#line:1007
                    O00OOOO0O0O0OOO0O .append (O00O00O000O000000 )#line:1008
        else :#line:1009
            print (f"ERROR: variable not found: {O0O0OO00O0OOO00O0},{OOOOO00000000OOO0}. Possible variables are {O0O000O00O000OO00}")#line:1010
            exit (1 )#line:1011
        return O00OOOO0O0O0OOO0O #line:1012
    def get_dataset_variable_count (O0O0O00O0OO00OOO0 ):#line:1015
        ""#line:1020
        if not (O0O0O00O0OO00OOO0 ._is_calculated ()):#line:1021
            print ("ERROR: Task has not been calculated.")#line:1022
            return #line:1023
        O0OOO0O0OOO0OOOOO =O0O0O00O0OO00OOO0 .result ["datalabels"]['varname']#line:1024
        return len (O0OOO0O0OOO0OOOOO )#line:1025
    def get_dataset_variable_list (OO0OOO00OOOOOO00O ):#line:1028
        ""#line:1033
        if not (OO0OOO00OOOOOO00O ._is_calculated ()):#line:1034
            print ("ERROR: Task has not been calculated.")#line:1035
            return #line:1036
        O0OOO0O0000O00OOO =OO0OOO00OOOOOO00O .result ["datalabels"]['varname']#line:1037
        return O0OOO0O0000O00OOO #line:1038
    def get_dataset_variable_name (O00OOOO000OOO00OO ,OOO0OOOOO0OO0O0O0 ):#line:1041
        ""#line:1047
        if not (O00OOOO000OOO00OO ._is_calculated ()):#line:1048
            print ("ERROR: Task has not been calculated.")#line:1049
            return #line:1050
        OO0OOO0OO0OO0000O =O00OOOO000OOO00OO .get_dataset_variable_list ()#line:1051
        if OOO0OOOOO0OO0O0O0 >=0 and OOO0OOOOO0OO0O0O0 <len (OO0OOO0OO0OO0000O ):#line:1052
            return OO0OOO0OO0OO0000O [OOO0OOOOO0OO0O0O0 ]#line:1053
        else :#line:1054
            print (f"ERROR: dataset has only {len(OO0OOO0OO0OO0000O)} variables, required index is {OOO0OOOOO0OO0O0O0}, but available values are 0-{len(OO0OOO0OO0OO0000O)-1}.")#line:1055
            exit (1 )#line:1056
    def get_dataset_variable_index (O0OOO00OOOOOOO00O ,OO000000OOO00O0O0 ):#line:1058
        ""#line:1064
        if not (O0OOO00OOOOOOO00O ._is_calculated ()):#line:1065
            print ("ERROR: Task has not been calculated.")#line:1066
            return #line:1067
        OOOOOOO000OO0O0OO =O0OOO00OOOOOOO00O .get_dataset_variable_list ()#line:1068
        if OO000000OOO00O0O0 in OOOOOOO000OO0O0OO :#line:1069
            return OOOOOOO000OO0O0OO .index (OO000000OOO00O0O0 )#line:1070
        else :#line:1071
            print (f"ERROR: attribute {OO000000OOO00O0O0} is not in dataset. The list of attribute names is  {OOOOOOO000OO0O0OO}.")#line:1072
            exit (1 )#line:1073
    def get_dataset_category_list (O0O00O000OO00O0O0 ,O0O0OOO00000OO00O ):#line:1076
        ""#line:1082
        if not (O0O00O000OO00O0O0 ._is_calculated ()):#line:1083
            print ("ERROR: Task has not been calculated.")#line:1084
            return #line:1085
        OOO0OO0O00O000O00 =O0O00O000OO00O0O0 .result ["datalabels"]['catnames']#line:1086
        O000OOOOO00OOOOO0 =None #line:1087
        if isinstance (O0O0OOO00000OO00O ,int ):#line:1088
            O000OOOOO00OOOOO0 =O0O0OOO00000OO00O #line:1089
        else :#line:1090
            O000OOOOO00OOOOO0 =O0O00O000OO00O0O0 .get_dataset_variable_index (O0O0OOO00000OO00O )#line:1091
        if O000OOOOO00OOOOO0 >=0 and O000OOOOO00OOOOO0 <len (OOO0OO0O00O000O00 ):#line:1093
            return OOO0OO0O00O000O00 [O000OOOOO00OOOOO0 ]#line:1094
        else :#line:1095
            print (f"ERROR: dataset has only {len(OOO0OO0O00O000O00)} variables, required index is {O000OOOOO00OOOOO0}, but available values are 0-{len(OOO0OO0O00O000O00)-1}.")#line:1096
            exit (1 )#line:1097
    def get_dataset_category_count (O0OO000O0OOOOOO00 ,OOOOO0000O0O0OO0O ):#line:1099
        ""#line:1105
        if not (O0OO000O0OOOOOO00 ._is_calculated ()):#line:1106
            print ("ERROR: Task has not been calculated.")#line:1107
            return #line:1108
        OOOOOOOOO00OO0O0O =None #line:1109
        if isinstance (OOOOO0000O0O0OO0O ,int ):#line:1110
            OOOOOOOOO00OO0O0O =OOOOO0000O0O0OO0O #line:1111
        else :#line:1112
            OOOOOOOOO00OO0O0O =O0OO000O0OOOOOO00 .get_dataset_variable_index (OOOOO0000O0O0OO0O )#line:1113
        O0OO0OOOOO0OOO00O =O0OO000O0OOOOOO00 .get_dataset_category_list (OOOOOOOOO00OO0O0O )#line:1114
        return len (O0OO0OOOOO0OOO00O )#line:1115
    def get_dataset_category_name (OO0O0O00O00O0O0OO ,OOO00O0OO0OO00OO0 ,OOOO0O0OOO00OO0OO ):#line:1118
        ""#line:1125
        if not (OO0O0O00O00O0O0OO ._is_calculated ()):#line:1126
            print ("ERROR: Task has not been calculated.")#line:1127
            return #line:1128
        O0OO0O00OO0O0O00O =None #line:1129
        if isinstance (OOO00O0OO0OO00OO0 ,int ):#line:1130
            O0OO0O00OO0O0O00O =OOO00O0OO0OO00OO0 #line:1131
        else :#line:1132
            O0OO0O00OO0O0O00O =OO0O0O00O00O0O0OO .get_dataset_variable_index (OOO00O0OO0OO00OO0 )#line:1133
        OOO000OOO0OO0O0OO =OO0O0O00O00O0O0OO .get_dataset_category_list (O0OO0O00OO0O0O00O )#line:1135
        if OOOO0O0OOO00OO0OO >=0 and OOOO0O0OOO00OO0OO <len (OOO000OOO0OO0O0OO ):#line:1136
            return OOO000OOO0OO0O0OO [OOOO0O0OOO00OO0OO ]#line:1137
        else :#line:1138
            print (f"ERROR: variable has only {len(OOO000OOO0OO0O0OO)} categories, required index is {OOOO0O0OOO00OO0OO}, but available values are 0-{len(OOO000OOO0OO0O0OO)-1}.")#line:1139
            exit (1 )#line:1140
    def get_dataset_category_index (O0O00OOO0OO0OO00O ,OOO00OO0O0O000OOO ,O00OOO000O0OO000O ):#line:1143
        ""#line:1150
        if not (O0O00OOO0OO0OO00O ._is_calculated ()):#line:1151
            print ("ERROR: Task has not been calculated.")#line:1152
            return #line:1153
        OO0OO00OOOOO000O0 =None #line:1154
        if isinstance (OOO00OO0O0O000OOO ,int ):#line:1155
            OO0OO00OOOOO000O0 =OOO00OO0O0O000OOO #line:1156
        else :#line:1157
            OO0OO00OOOOO000O0 =O0O00OOO0OO0OO00O .get_dataset_variable_index (OOO00OO0O0O000OOO )#line:1158
        O000OO0O0O000OO00 =O0O00OOO0OO0OO00O .get_dataset_category_list (OO0OO00OOOOO000O0 )#line:1159
        if O00OOO000O0OO000O in O000OO0O0O000OO00 :#line:1160
            return O000OO0O0O000OO00 .index (O00OOO000O0OO000O )#line:1161
        else :#line:1162
            print (f"ERROR: value {O00OOO000O0OO000O} is invalid for the variable {O0O00OOO0OO0OO00O.get_dataset_variable_name(OO0OO00OOOOO000O0)}. Available category names are {O000OO0O0O000OO00}.")#line:1163
            exit (1 )#line:1164
def clm_vars (OO000OOOOOO00OOO0 ,minlen =1 ,maxlen =3 ,type ='con'):#line:1166
    ""#line:1174
    OO0O0O00O00000O0O =[]#line:1175
    for O000O0OO0OO00OOOO in OO000OOOOOO00OOO0 :#line:1176
        if isinstance (O000O0OO0OO00OOOO ,dict ):#line:1177
            O0O00000OOOO00OO0 =O000O0OO0OO00OOOO #line:1178
        else :#line:1179
            O0O00000OOOO00OO0 ={}#line:1180
            O0O00000OOOO00OO0 ['name']=O000O0OO0OO00OOOO #line:1181
            O0O00000OOOO00OO0 ['type']='subset'#line:1182
            O0O00000OOOO00OO0 ['minlen']=1 #line:1183
            O0O00000OOOO00OO0 ['maxlen']=1 #line:1184
        OO0O0O00O00000O0O .append (O0O00000OOOO00OO0 )#line:1185
    OOOOOOOO0O0O0000O ={}#line:1186
    OOOOOOOO0O0O0000O ['attributes']=OO0O0O00O00000O0O #line:1187
    OOOOOOOO0O0O0000O ['minlen']=minlen #line:1188
    OOOOOOOO0O0O0000O ['maxlen']=maxlen #line:1189
    OOOOOOOO0O0O0000O ['type']=type #line:1190
    return OOOOOOOO0O0O0000O #line:1191
def clm_subset (O00OO000OOOOO00OO ,minlen =1 ,maxlen =1 ):#line:1193
    ""#line:1201
    O0OOOO0000O0O00OO ={}#line:1202
    O0OOOO0000O0O00OO ['name']=O00OO000OOOOO00OO #line:1203
    O0OOOO0000O0O00OO ['type']='subset'#line:1204
    O0OOOO0000O0O00OO ['minlen']=minlen #line:1205
    O0OOOO0000O0O00OO ['maxlen']=maxlen #line:1206
    return O0OOOO0000O0O00OO #line:1207
def clm_seq (O000OOOOOOO0O00OO ,minlen =1 ,maxlen =2 ):#line:1209
    ""#line:1217
    O0OO00OOOO0OO000O ={}#line:1218
    O0OO00OOOO0OO000O ['name']=O000OOOOOOO0O00OO #line:1219
    O0OO00OOOO0OO000O ['type']='seq'#line:1220
    O0OO00OOOO0OO000O ['minlen']=minlen #line:1221
    O0OO00OOOO0OO000O ['maxlen']=maxlen #line:1222
    return O0OO00OOOO0OO000O #line:1223
def clm_lcut (OOO00OO0OO0O0OO0O ,minlen =1 ,maxlen =2 ):#line:1225
    ""#line:1233
    O00O00OOO0OOO0000 ={}#line:1234
    O00O00OOO0OOO0000 ['name']=OOO00OO0OO0O0OO0O #line:1235
    O00O00OOO0OOO0000 ['type']='lcut'#line:1236
    O00O00OOO0OOO0000 ['minlen']=minlen #line:1237
    O00O00OOO0OOO0000 ['maxlen']=maxlen #line:1238
    return O00O00OOO0OOO0000 #line:1239
def clm_rcut (O00OO0OOO0O0O00OO ,minlen =1 ,maxlen =2 ):#line:1241
    ""#line:1249
    O000O00OO00000O00 ={}#line:1250
    O000O00OO00000O00 ['name']=O00OO0OOO0O0O00OO #line:1251
    O000O00OO00000O00 ['type']='rcut'#line:1252
    O000O00OO00000O00 ['minlen']=minlen #line:1253
    O000O00OO00000O00 ['maxlen']=maxlen #line:1254
    return O000O00OO00000O00 #line:1255

