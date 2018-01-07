import numpy as np
import fortranformat as ff
import pytz, datetime
import os

inpath  = "data/201601/"
outpath = "new/"
#===============================================================================

def write_in(a,f_out,k,xlat,xlon,ID,ter,kx,bogus,date,slp,p,z,t,td,spd,direc):
    out_form1 = ff.FortranRecordWriter('2f20.5,a5')
    out_form2 = ff.FortranRecordWriter('f20.5,5i10,3l10,2i10,a20,13(f13.5,i7)')
    out_form3 = ff.FortranRecordWriter('10(f13.5,i7)')
    out_form4 = ff.FortranRecordWriter('3i7')

    for l in range(a[4]):
        aa = [xlat[l],xlon[l],ID[l]]
        f_out.write(out_form1.write(aa))

        if k == 'surface':
            f_out.write('                                   SURFACE DATA FROM ??????????? SOURCE    FM-12 SYNOP                                                                     ')
        elif k == 'high':
            f_out.write('                                   SOUNDINGS FROM ????????? SOURCE         FM-35 TEMP                                                                      ')

        iseq_num = l+1
        aa = [ter[l],kx*6,0,0,iseq_num,0,True,bogus,False,-888888, -888888,\
        date,slp[l],0,-888888.,0, -888888.,0, -888888.,0, -888888.,0, \
              -888888.,0, \
              -888888.,0, -888888.,0, -888888.,0, -888888.,0, \
              -888888.,0, \
              -888888.,0, -888888.,0]
        f_out.write(out_form2.write(aa))
        f_out.write("\n")

        for m in range(kx):
            aa = [p[a[4]*m+l] ,0 , z[a[4]*m+l] , 0 , t[a[4]*m+l] ,0, td[a[4]*m+l] ,0 , \
            spd[a[4]*m+l] ,0, direc[a[4]*m+l],0, -888888.,0, -888888.,0,-888888.,0, -888888.,0]
            f_out.write(out_form3.write(aa))
            f_out.write("\n")

        aa = [ -777777.,0, -777777.,0,float(kx),0,\
         -888888.,0, -888888.,0, -888888.,0, \
         -888888.,0, -888888.,0, -888888.,0, \
         -888888.,0]
        f_out.write(out_form3.write(aa))
        f_out.write("\n")

        aa = [kx,0,0]
        f_out.write(out_form4.write(aa))
        f_out.write("\n")
#===============================================================================

def read_in_ground(data,date,a,f_in):
    ID    = []
    xlon  = []
    xlat  = []
    ter   = []
    direc = []
    spd   = []
    slp   = []
    td    = []
    t     = []

    form_ID    = ff.FortranRecordReader('i5')
    form_xlon  = ff.FortranRecordReader('f7.2')
    form_xlat  = ff.FortranRecordReader('f6.2')
    form_ter   = ff.FortranRecordReader('f4.0')
    form_direc = ff.FortranRecordReader('f4.0')
    form_spd   = ff.FortranRecordReader('f4.0')
    form_slp   = ff.FortranRecordReader('f4.0')
    form_td    = ff.FortranRecordReader('f5.1')
    form_t     = ff.FortranRecordReader('f5.1')

    for i in range(a[4]):
        ID.append(form_ID.read(data[18+i*148:23+i*148])[0])

    for i in range(a[4]):
        xlon.append(form_xlon.read(data[24+i*148:31+i*148])[0])

    for i in range(a[4]):
        xlat.append(form_xlat.read(data[33+i*148:39+i*148])[0])

    for i in range(a[4]):
        ter.append(form_ter.read(data[40+i*148:44+i*148])[0])
    for j in range(a[4]):
        if ter[j] == 9999.:
            ter[j] = -888888.

    for i in range(a[4]):
        direc.append(form_direc.read(data[55+i*148:59+i*148])[0])
    for j in range(a[4]):
        if direc[j] == 9999.:
            direc[j] = -888888.

    for i in range(a[4]):
        spd.append(form_spd.read(data[60+i*148:64+i*148])[0])
    for j in range(a[4]):
        if spd[j] == 9999.:
            spd[j] = -888888.

    for i in range(a[4]):
        slp.append(form_slp.read(data[65+i*148:69+i*148])[0])
    for j in range(a[4]):
        if slp[j] == 9999.:
            slp[j] = -888888.

    for i in range(a[4]):
        td.append(form_td.read(data[110+i*148:115+i*148])[0])
    for j in range(a[4]):
        if td[j] == 999.9:
            td[j] = -888888.

    for i in range(a[4]):
        t.append(form_t.read(data[129+i*148:134+i*148])[0])
    for j in range(a[4]):
        if t[j] == 999.9:
            t[j] = -888888.

    bogus = False
    p     = slp
    for pl in range(a[4]):
        if p[pl] >= 500 and p[pl] != -888888.:
            p[pl] = (p[pl]/10.)+900.
            p[pl] =  p[pl]*100.
        elif p[pl] < 500 and p[pl] != -888888.:
            p[pl] = (p[pl]/10.)+1000.
            p[pl] =  p[pl]*100.
    z     = ter
    kx    = 1
    for it in range(a[4]):
        if t[it] != -888888.:
            t[it]     = t[it] + 273.15
        if td[it] != -888888.:
            td[it]     = td[it] + 273.15

    f_in.close()

    return ID,xlon,xlat,ter,direc,spd,slp,td,t,kx,bogus,p,z
#===============================================================================

def read_in_high(data,date,a,f_in,level,inpath):
    a[4],a[5] = a[5],a[4]

    ID    = []
    xlon  = []
    xlat  = []
    ter   = []
    z     = []
    t     = []
    t_td  = []
    direc = []
    spd   = []
    p     = []
    slp   = []
    td    = []

    form_ID    = ff.FortranRecordReader('i5')
    form_xlon  = ff.FortranRecordReader('f7.2')
    form_xlat  = ff.FortranRecordReader('f6.2')
    form_ter   = ff.FortranRecordReader('f4.0')
    form_z     = ff.FortranRecordReader('f4.0')
    form_t     = ff.FortranRecordReader('f4.0')
    form_direc = ff.FortranRecordReader('f4.0')
    form_spd   = ff.FortranRecordReader('f4.0')
    for i in range(a[4]):
        if data[67+i*59] == ".":
            form_t_td = ff.FortranRecordReader('f4.1')
        else:
            form_t_td = ff.FortranRecordReader('f4.0')

    for i in range(a[4]):
        ID.append(form_ID.read(data[23+i*59:28+i*59])[0])

    for i in range(a[4]):
        xlon.append(form_xlon.read(data[29+i*59:36+i*59])[0])

    for i in range(a[4]):
        xlat.append(form_xlat.read(data[38+i*59:44+i*59])[0])

    for i in range(a[4]):
        ter.append(form_ter.read(data[45+i*59:49+i*59])[0])
        slp.append(-888888.)
    for j in range(a[4]):
        if ter[j] == 9999.:
            ter[j] = -888888.

    f_in.close()

    for lev in level:
        inname  = inpath+"high/plot/"+str(lev)+"/"+tl
        f_in    = open(inname, 'r')
        f_in.readline()
        loc = f_in.tell()
        f_in.seek(loc) #loc=44(1000) loc=43(else)
        data = f_in.read(-1)
        form_date = ff.FortranRecordReader('4i3,2i4')
        a         = form_date.read(data)
        a[4],a[5] = a[5],a[4]

        for i in range(a[4]):
            p.append(a[5])

        for i in range(a[4]):
            z.append(form_z.read(data[55+i*59:59+i*59])[0])
        for j in range(a[4]):
            if z[j] == 9999.:
                z[j] = -888888.

        for i in range(a[4]):
            t.append(form_t.read(data[60+i*59:64+i*59])[0])
        for j in range(a[4]):
            if t[j] == 9999.:
                t[j] = -888888.

        for i in range(a[4]):
            t_td.append(form_t_td.read(data[65+i*59:69+i*59])[0])

        for i in range(a[4]):
            direc.append(form_direc.read(data[70+i*59:74+i*59])[0])
        for j in range(a[4]):
            if direc[j] == 9999.:
                direc[j] = -888888.

        for i in range(a[4]):
            spd.append(form_spd.read(data[75+i*59:79+i*59])[0])
        for j in range(a[4]):
            if spd[j] == 9999.:
                spd[j] = -888888.

    bogus = False
    kx    = 8

    for i in range(a[4]*kx):
        td.append(t[i]-t_td[i])
    for j in range(a[4]*kx):
        if t[j] == -888888. or t_td[j] == 9999.:
            td[j] = -888888.

    for it in range(a[4]*kx):
        if t[it] != -888888.:
            t[it]     = t[it] + 273.15
        if td[it] != -888888.:
            td[it]     = td[it] + 273.15

    f_in.close()
    return ID,xlon,xlat,ter,direc,spd,slp,td,t,kx,bogus,p,z
#===============================================================================

common          = []
pathDir_high    =  os.listdir(inpath+"high/plot/1000/")
pathDir_surface =  os.listdir(inpath+"surface/plot/")
only_high       = os.listdir(inpath+"high/plot/1000/")
only_surface    = os.listdir(inpath+"surface/plot/")
for i in pathDir_surface:
    for j in pathDir_high:
        if i == j:
            common.append(i)
for i in pathDir_surface:
    for j in common:
        if i == j:
            only_surface.remove(i)
for i in pathDir_high:
    for j in common:
        if i == j:
            only_high.remove(i)

for tl in common:
    print tl
    for k in ['surface','high']:
        if k == 'surface':
            inname  = inpath+"surface/plot/"+tl
            form_date = ff.FortranRecordReader('4i3,i4')
        elif k =='high':
            inname  = inpath+"high/plot/1000/"+tl
            form_date = ff.FortranRecordReader('4i3,2i4')

        f_in    = open(inname, 'r')
        f_in.readline()
        loc = f_in.tell()
        f_in.seek(loc)  #loc=36
        data      = f_in.read(-1)
        a         = form_date.read(data)
        date_char = (2000+a[0])*10000000000+a[1]*100000000+a[2]*1000000+a[3]*10000
        local     = pytz.timezone ("Asia/Shanghai")
        naive     = datetime.datetime.strptime (str(date_char), "%Y%m%d%H%M%S")
        local_dt  = local.localize(naive, is_dst=None)
        utc_dt    = local_dt.astimezone (pytz.utc)
        date      = utc_dt.strftime("%Y%m%d%H%M%S")

        if k == 'surface':
            f_out     = open(outpath+str(date), 'w')
            if a[4] ==0:
                print "surface empty"
            ID,xlon,xlat,ter,direc,spd,slp,td,t,kx,bogus,p,z = read_in_ground(data,date,a,f_in)
        elif k =='high':
            level = [1000,925,850,700,500,300,200,100]
            if a[5] ==0:
                print "high empty"
            ID,xlon,xlat,ter,direc,spd,slp,td,t,kx,bogus,p,z = read_in_high(data,date,a,f_in,level,inpath)

        write_in(a,f_out,k,xlat,xlon,ID,ter,kx,bogus,date,slp,p,z,t,td,spd,direc)
    f_out.close()



for tl in only_surface:
    print tl
    k = 'surface'
    inname  = inpath+"surface/plot/"+tl
    form_date = ff.FortranRecordReader('4i3,i4')

    f_in    = open(inname, 'r')
    f_in.readline()
    loc = f_in.tell()
    f_in.seek(loc)  #loc=36
    data      = f_in.read(-1)
    a         = form_date.read(data)
    if a[4]==0:
        print "surface empty"
        continue
    date_char = (2000+a[0])*10000000000+a[1]*100000000+a[2]*1000000+a[3]*10000
    local     = pytz.timezone ("Asia/Shanghai")
    naive     = datetime.datetime.strptime (str(date_char), "%Y%m%d%H%M%S")
    local_dt  = local.localize(naive, is_dst=None)
    utc_dt    = local_dt.astimezone (pytz.utc)
    date      = utc_dt.strftime("%Y%m%d%H%M%S")
    f_out     = open(outpath+str(date), 'w')
    ID,xlon,xlat,ter,direc,spd,slp,td,t,kx,bogus,p,z = read_in_ground(data,date,a,f_in)

    write_in(a,f_out,k,xlat,xlon,ID,ter,kx,bogus,date,slp,p,z,t,td,spd,direc)
f_out.close()



for tl in only_high:
    print tl
    k = 'high'
    inname  = inpath+"high/plot/1000/"+tl
    form_date = ff.FortranRecordReader('4i3,2i4')

    f_in    = open(inname, 'r')
    f_in.readline()
    loc = f_in.tell()
    f_in.seek(loc)  #loc=36
    data      = f_in.read(-1)

    a         = form_date.read(data)
    if a[5]==0:
        print "high empty"
        continue
    date_char = (2000+a[0])*10000000000+a[1]*100000000+a[2]*1000000+a[3]*10000
    local     = pytz.timezone ("Asia/Shanghai")
    naive     = datetime.datetime.strptime (str(date_char), "%Y%m%d%H%M%S")
    local_dt  = local.localize(naive, is_dst=None)
    utc_dt    = local_dt.astimezone (pytz.utc)
    date      = utc_dt.strftime("%Y%m%d%H%M%S")
    f_out     = open(outpath+str(date), 'w')
    level     = [1000,925,850,700,500,300,200,100]
    ID,xlon,xlat,ter,direc,spd,slp,td,t,kx,bogus,p,z = read_in_high(data,date,a,f_in,level,inpath)

    write_in(a,f_out,k,xlat,xlon,ID,ter,kx,bogus,date,slp,p,z,t,td,spd,direc)
f_out.close()
