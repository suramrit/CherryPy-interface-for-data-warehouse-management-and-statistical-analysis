
#import datetime
import mysql.connector
import pandas
import numpy as np
import scipy.stats as stats
import sys

def Quest1():
	global query
	global cnx
	data=pandas.read_sql_query(query['1a'], cnx)
	print(data.to_string(index=False))
	print()
	data=pandas.read_sql_query(query['1b'], cnx)
	print(data.to_string(index=False))
	print()
	data=pandas.read_sql_query(query['1c'], cnx)
	print(data.to_string(index=False))
	return

def Quest2():
	global query
	global cnx
	data=pandas.read_sql_query(query['2'], cnx)
	print(data.to_string(index=False))
	return

def Quest3():
	global query
	global cnx
	data=pandas.read_sql_query(query['3'], cnx)
	print(data.to_string(index=False))
	return

def Quest4():
	global query
	global cnx
	data=pandas.read_sql_query(query['4a'], cnx)
	data2=pandas.read_sql_query(query['4b'], cnx)
	a=data['exp'].values
	b=data2['exp'].values
	
	print(stats.tmean(a))
	print(stats.tmean(b))
	print(stats.tvar(a))
	print(stats.tvar(b))

	print(stats.ttest_ind(a,b,equal_var=True))
	return


def Quest5():
	global query
	global cnx
	data=pandas.read_sql_query(query['5a'], cnx)
	data2=pandas.read_sql_query(query['5b'], cnx)
	data3=pandas.read_sql_query(query['5c'], cnx)
	data4=pandas.read_sql_query(query['5d'], cnx)

	print(data.shape)
	print(data2.shape)
	print(data3.shape)
	print(data4.shape)
	
	print(stats.f_oneway(data['exp'].values,data2['exp'].values,data3['exp'].values,data4['exp'].values))
	return

def Quest6():
	global query
	global cnx
	data=pandas.read_sql_query(query['6a'], cnx)
	data2=pandas.read_sql_query(query['6b'], cnx)
	'''
	print(data.shape)
	print(data2.shape)
	'''
	ALL_patientVecs={}
	AML_patientVecs={}
	grpdRows=data.groupby(['p_id'])['exp'];
	for r in grpdRows:
		ALL_patientVecs[r[0]]=r[1].values
	grpdRows=data2.groupby(['p_id'])['exp'];
	for r in grpdRows:
		AML_patientVecs[r[0]]=r[1].values

	#for k in ALL_patientVecs:
	#	print(ALL_patientVecs[k].shape)

	ALL_pids=list(ALL_patientVecs.keys())
	AML_pids=list(AML_patientVecs.keys())

	##For 'within ALL' pearson correlation Coefficients
	pccALLonly=[]
	for i in range(len(ALL_pids)):
		p=ALL_pids[i]
		for j in range(i+1,len(ALL_pids)):
			q=ALL_pids[j]
			#print(i+1,",",j+1,": " ,stats.pearsonr(ALL_patientVecs[p],ALL_patientVecs[q])[0])
			pccALLonly.append(stats.pearsonr(ALL_patientVecs[p],ALL_patientVecs[q])[0])
	print(len(pccALLonly))
	#print(sum(pccALLonly))
	print(sum(pccALLonly) / float(len(pccALLonly)))

	##For 'AML vs ALL' pearson correlation Coefficients
	pccML=[]
	for i in range(len(ALL_pids)):
		p=ALL_pids[i]
		for j in range(len(AML_pids)):
			q=AML_pids[j]
			pccML.append(stats.pearsonr(ALL_patientVecs[p],AML_patientVecs[q])[0])
	
	print(len(pccML))
	print(sum(pccML) / float(len(pccML)))
	return

def Quest7():
	#global query
	global cnx
	dis = input("Enter disease: ")
	dis="\""+dis+"\""
	q="SELECT g.UID,d.p_id,mic.exp from microarray_fact mic INNER JOIN (probe pb, gene g, disease ds, Diagnosis d, sample s) on (mic.pb_id=pb.pb_id and pb.UID=g.UID and d.`ds_id`=ds.`ds_id` and d.p_id=s.p_id and mic.s_id=s.s_id) where ";
	
	criterion="ds.`name` ="+dis+" ORDER BY d.p_id,g.UID;"
	query=q+criterion
	data=pandas.read_sql_query(query, cnx)
	print(data.shape)
	criterion="ds.`name` !="+dis+" ORDER BY d.p_id,g.UID;"
	query=q+criterion
	data2=pandas.read_sql_query(query, cnx)
	print(data2.shape)


	UID_CritVecs={}
	UID_NoCritVecs={}
	grpdRows=data.groupby(['UID'])['exp'];
	for r in grpdRows:
		UID_CritVecs[r[0]]=r[1].values
	
	grpdRows=data2.groupby(['UID'])['exp'];
	for r in grpdRows:
		UID_NoCritVecs[r[0]]=r[1].values
	
	Crit_UIDs=list(UID_CritVecs.keys())
	NoCrit_UIDs=list(UID_NoCritVecs.keys())
	
	InformativeUIDs=[]
	for i in range(len(Crit_UIDs)):
		p=Crit_UIDs[i]
		if(p in UID_NoCritVecs):
			if((stats.ttest_ind(UID_CritVecs[p],UID_NoCritVecs[p],equal_var=True)[1])<0.01):
				InformativeUIDs.append(p)
	InformativeUIDs.sort()
	print(InformativeUIDs)
	
	#Part2: Classify New Patient
	Crit_PidVecs={}
	NoCrit_PidVecs={}
	PnewVecs={}

	data=data[data['UID'].isin(InformativeUIDs)]
	print(data.shape)
	grpdRows=data.groupby(['p_id'])['exp'];
	for r in grpdRows:
		Crit_PidVecs[r[0]]=r[1].values
		print(Crit_PidVecs[r[0]].shape)
	data2=data2[data2['UID'].isin(InformativeUIDs)]
	print(data2.shape)
	grpdRows=data2.groupby(['p_id'])['exp'];
	for r in grpdRows:
		NoCrit_PidVecs[r[0]]=r[1].values
		print(NoCrit_PidVecs[r[0]].shape)

	in_uid=', '.join(list(map(lambda x: '%s', InformativeUIDs)))
	q="SELECT * from test_samples t WHERE t.`UID` IN ("+in_uid+") ORDER BY t.UID;"
	data3=pandas.read_sql_query(q, cnx,params=InformativeUIDs)
	#print(data3)
	#data3=data3[data3['UID'].isin(InformativeUIDs)]
	print(data3.shape)
	print(data3)

	for i in range (1,len(data3.columns)):
		PnewVecs[data3.columns[i]]=data3[data3.columns[i]].values
		print(PnewVecs[data3.columns[i]].shape)
	
	New_pids=list(PnewVecs.keys())
	Crit_pids=list(Crit_PidVecs.keys())
	NoCrit_pids=list(NoCrit_PidVecs.keys())
	
	##For 'P_new vs P_criterion' pearson correlation Coefficients
	pidnew = input("Enter name of test patient to classify : ")
	if(pidnew in New_pids):
		pnvec=PnewVecs[pidnew]
		
		pccCrit=[] #groupA RAs
		for i in range(len(Crit_pids)):
			p=Crit_pids[i]
			pccCrit.append(stats.pearsonr(pnvec,Crit_PidVecs[p])[0])

		pccNoCrit=[] #groupB RAs
		for i in range(len(NoCrit_pids)):
			p=NoCrit_pids[i]
			pccNoCrit.append(stats.pearsonr(pnvec,NoCrit_PidVecs[p])[0])
		
		print(len(pccCrit))
		print(len(pccNoCrit))
		print(stats.ttest_ind(pccCrit,pccNoCrit,equal_var=True))
		if((stats.ttest_ind(pccCrit,pccNoCrit,equal_var=True)[1])<0.01):
			print("Patient ",pidnew, " has been classified as having "+dis)
		else:
			print("Patient ",pidnew, " has been classified as NOT having "+dis)
		
	else:
		print("No such patient!")

	return

#print(sys.argv)
global query
query = {'1a': "SELECT COUNT(DISTINCT p_id) from Diagnosis d INNER JOIN disease ds ON d.`ds_id`=ds.`ds_id` WHERE ds.`description`=\"tumor\";",
	'1b': "SELECT COUNT(DISTINCT p_id) from Diagnosis d INNER JOIN disease ds ON d.`ds_id`=ds.`ds_id` WHERE ds.`type`=\"leukemia\";",
	'1c': "SELECT COUNT(DISTINCT p_id) from Diagnosis d INNER JOIN disease ds ON d.`ds_id`=ds.`ds_id` WHERE ds.`name`=\"ALL\";",
	'2': "SELECT distinct dr.`type` from drug dr inner join (DrugUse du,Diagnosis d,disease ds) on (d.`ds_id`=ds.`ds_id` and d.`p_id`=du.`p_id` and du.`dr_id`=dr.`dr_id`) where ds.`description`=\"tumor\";",
	'3': "SELECT  mic.s_id,mic.pb_id,mic.exp from microarray_fact mic INNER JOIN (probe pb, GeneCluster gc, disease ds, Diagnosis d, sample s) ON (mic.pb_id=pb.pb_id and pb.UID=gc.UID and d.`ds_id`=ds.`ds_id` and d.p_id=s.p_id and mic.s_id=s.s_id) WHERE ds.`name`=\"ALL\" and gc.cl_id=\"00002\" and mic.`mu_id`=\"001\";",
	'4a': "SELECT maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id = \"0012502\" and ds.`name` =\"ALL\";",
	'4b': "SELECT maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id = \"0012502\" and ds.`name` !='ALL';",
	'5a': "SELECT maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id = \"0007154\" and ds.`name` =\"ALL\";",
	'5b': "SELECT maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id = \"0007154\" and ds.`name` =\"AML\";",
	'5c': "SELECT maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id = \"0007154\" and ds.`name` =\"colon tumor\";",
	'5d': "SELECT maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id = \"0007154\" and ds.`name` =\"breast tumor\";",
	'6a': "SELECT s.p_id,maf.pb_id,maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id = \"0007154\" and ds.`name` =\"ALL\" ORDER BY s.p_id,maf.pb_id;",
	'6b': "SELECT s.p_id,maf.pb_id,maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id = \"0007154\" and ds.`name` =\"AML\" ORDER BY s.p_id,maf.pb_id;",
	
	}
global cnx
cnx = mysql.connector.connect(user='root', password='cse601', host='127.0.0.1',database='Biostar_proj1')

qnum=sys.argv[1]
options = {'1' : Quest1,
           '2' : Quest2,
           '3' : Quest3,
           '4' : Quest4,
           '5' : Quest5,
           '6' : Quest6,
           '7' : Quest7
}
options[qnum]()
cnx.close()
