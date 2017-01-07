# Cheerypy interface for handling a data warehouse representing Gene Data
# Done as part for CSE601 - Data Mining and BioInformatics at University at Buffalo

#The code implements a working HTML interface that allows the administerator to query the warehouse
#and do changes in an interactive manner. 

#For representation; the code implements certain standard queries. 

#The project scored a maximum possible 100 points 

import cherrypy
import mysql.connector
import pandas
import numpy as np
import scipy.stats as stats
import sys
import pandasql

#"SELECT maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id = \"0012502\" and ds.`name` =\"ALL\";"
#Each Problem as a separate result... 
#Globals.. 
global query
query = {'1a': "SELECT COUNT(DISTINCT p_id) from Diagnosis d INNER JOIN disease ds ON d.`ds_id`=ds.`ds_id` WHERE ds.`description`=\"tumor\";",
	'1b': "SELECT COUNT(DISTINCT p_id) as \"Num Patients\" from Diagnosis d INNER JOIN disease ds ON d.`ds_id`=ds.`ds_id` WHERE ds.`type`=\"leukemia\";",
	'1c': "SELECT COUNT(DISTINCT p_id) as \"Num Patients\" from Diagnosis d INNER JOIN disease ds ON d.`ds_id`=ds.`ds_id` WHERE ds.`name`=\"ALL\";",
	'2': "SELECT distinct dr.`type` as \"Drug_Type\" from drug dr inner join (DrugUse du,Diagnosis d,disease ds) on (d.`ds_id`=ds.`ds_id` and d.`p_id`=du.`p_id` and du.`dr_id`=dr.`dr_id`) where ds.`description`=\"tumor\";",
	'3': "SELECT  mic.s_id as \"Sample Id\",mic.pb_id as \"Probe Id\" ,mic.exp \"Expression Val.\" from microarray_fact mic INNER JOIN (probe pb, GeneCluster gc, disease ds, Diagnosis d, sample s) ON (mic.pb_id=pb.pb_id and pb.UID=gc.UID and d.`ds_id`=ds.`ds_id` and d.p_id=s.p_id and mic.s_id=s.s_id) WHERE ds.`name`=\"ALL\" and gc.cl_id=\"00002\" and mic.`mu_id`=\"001\";",
	'4a': "SELECT s.p_id,maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id = \"0012502\" and ds.`name` =\"ALL\";",
	'4b': "SELECT s.p_id,maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id = \"0012502\" and ds.`name` !='ALL';",
	'5a': "SELECT s.p_id,maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id = \"0007154\" and ds.`name` =\"ALL\";",
	'5b': "SELECT s.p_id,maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id = \"0007154\" and ds.`name` =\"AML\";",
	'5c': "SELECT s.p_id,maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id = \"0007154\" and ds.`name` =\"colon tumor\";",
	'5d': "SELECT s.p_id,maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id = \"0007154\" and ds.`name` =\"breast tumor\";",
	'6a': "SELECT s.p_id,maf.pb_id,maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id = \"0007154\" and ds.`name` =\"ALL\" ORDER BY s.p_id,maf.pb_id;",
	'6b': "SELECT s.p_id,maf.pb_id,maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id = \"0007154\" and ds.`name` =\"AML\" ORDER BY s.p_id,maf.pb_id;",
	}
global cnx
cnx = mysql.connector.connect(user='root',password='suramrit',host='127.0.0.1',database='BioStar')
#global data4
#data4=pandas.read_sql_query(query['2'], cnx)
class HelloWorld(object):
	@cherrypy.expose
	def index(self):
		 return """<html>
          <head></head>
          <body>
          	<h1>See Result of Defined Queries</h1>
            <form method="get" action="query1">
              <button type="submit">Query1!</button>
            </form>
            <form method="get" action="query2">
              <button type="submit">Query2!</button>
            </form>
            <form method="get" action="query3">
              <button type="submit">Query3!</button>
            </form>
            <form method="get" action="query4">
              <button type="submit">Query4!</button>
            </form>
            <form method="get" action="query5">
              <button type="submit">Query5!</button>
            </form>
            <form method="get" action="query6">
              <button type="submit">Query6!</button>
            </form>
            <form method="get" action="query7_Disease">
              <button type="submit">Query7!</button>
            </form>
            <form method="get" action="custom_Query">
            <button type="submit">Create a Custom Query</button>
            </form>
            <form method="get" action="customTstat">
            <button type="submit">Compute Custom T Statistics</button>
            </form>
            <form method="get" action="customFstat">
            <button type="submit">Compute Custom F Statistics</button>
            </form>
          </body>
        </html>"""
	@cherrypy.expose
	def query1(self, length=8):
		res1 = pandas.read_sql_query("SELECT COUNT(DISTINCT p_id) as \"Num Patients\" from Diagnosis d INNER JOIN disease ds ON d.`ds_id`=ds.`ds_id` WHERE ds.`description`=\"tumor\";", cnx)
		res2 = pandas.read_sql_query(query['1b'], cnx)
		res3 = pandas.read_sql_query(query['1c'], cnx)
		print(res1.to_html(max_rows=25))
		return """<html>
					<form method="get" action="index">
              		<button type="submit">Return</button>
           			</form>
           			<h1>Patients with Tumor</h1>"""+res1.to_html(index=False)+"""
					<h1>Patients with Leukemia</h1>"""+res2.to_html(index=False)+"""
					<h1>Patients with ALL</h1>"""+res3.to_html(index=False)+"""
				</html>"""
	@cherrypy.expose
	def query2(self, length=8):
		global data
		data=pandas.read_sql_query(query['2'], cnx)
		print(data.head())
		pysql = lambda q: pandasql.sqldf(q, globals())
		que = "select count(*) from data;" #user input on results.. 
		data2 = pysql(que)
		print(data2)
		return """<html>
					<form method="get" action="index">
              		<button type="submit">Return</button>
           			</form>
           			 <form method="post" action="processQuery2"> 
            			Custom Query on Result: 
            			<input type="text" name="qu"><br> 
    					<input type="submit">
    				</form>
					<h1>Drug type used for patients with Tumor <h3>(Rows-"""+str(len(data.index))+""")</h3></h1> """+data.to_html(index=False)+"""
					</html>"""
	@cherrypy.expose
	def processQuery2(self,qu,length=8):
		#global data
		#data=pandas.read_sql_query(query['2'], cnx)
		#print(data.head())
		pysql = lambda q: pandasql.sqldf(q, globals())
		data2 = pysql(qu)
		return data2.to_html(index=False)

	@cherrypy.expose
	def query3(self, length=8):	
		global data
		data=pandas.read_sql_query(query['3'], cnx)		
		print(data.head())	
		return """<html>
					<form method="get" action="index">
              		<button type="submit">Return</button>
           			</form>
           			</form>
           			 <form method="post" action="processQuery3"> 
            			Custom Query on Result: 
            			<input type="text" name="qu"><br> 
    					<input type="submit">
    				</form>
					<h1>mRNA probe values for patients with ALL <h3>(Rows-"""+str(len(data.index))+""")</h3></h1> """+data.to_html(index=False)+"""
					</html>"""
	@cherrypy.expose
	def processQuery3(self,qu,length=8):
		#global data
		#data=pandas.read_sql_query(query['3'], cnx)
		#print(data.head())
		pysql = lambda q: pandasql.sqldf(q, globals())
		data2 = pysql(qu)
		return data2.to_html(index=False)		

	@cherrypy.expose
	def query4(self, length=8):	
		global data1
		data1=pandas.read_sql_query(query['4a'], cnx)
		pysql = lambda q: pandasql.sqldf(q, globals())
		data1_rep = pysql("select p_id as \"Patient ID\",exp as \"Expression Val\" from data1 ")
		global data2
		data2=pandas.read_sql_query(query['4b'], cnx)
		data2_rep = pysql("select p_id as \"Patient ID\",exp as \"Expression Val\" from data2 ")			
		a=data1['exp'].values
		b=data2['exp'].values
		print(stats.tmean(a))
		print(stats.tmean(b))
		print(stats.tvar(a))
		print(stats.tvar(b))
		return """<html>
					<form method="get" action="index">
              		<button type="submit">Return</button>
           			</form>
           			</form>
           			 <form method="post" action="processQuery4"> 
            			Custom Query on Result: 
            			<input type="text" name="qu"><br> 
    					<input type="submit">
    				</form>
    				<h2>T-statistics for Exp Values::</h2>"""+(str)(stats.ttest_ind(a,b,equal_var=True)[0])+"""
					<h1>Exp values for patients with ALL<h3>(Rows-"""+str(len(data1.index))+""")</h3></h1>"""+data1_rep.to_html(index=False)+"""
					<h1>Exp values for patients without ALL<h3>(Rows-"""+str(len(data2.index))+""")</h3></h1>"""+data2_rep.to_html(index=False)+"""
					
					</html>"""
	@cherrypy.expose
	def processQuery4(self,qu,length=8):
		#global data1
		#data1=pandas.read_sql_query(query['4a'], cnx)
		#global data2
		#data2=pandas.read_sql_query(query['4b'], cnx)
		pysql = lambda q: pandasql.sqldf(q, globals())
		data3 = pysql(qu)
		return data3.to_html(index=False)
	@cherrypy.expose
	def query5(self, length=8):	
		global data1
		data1=pandas.read_sql_query(query['5a'], cnx)
		global data2
		data2=pandas.read_sql_query(query['5b'], cnx)
		global data3
		data3=pandas.read_sql_query(query['5c'], cnx)
		global data4
		data4=pandas.read_sql_query(query['5d'], cnx)
		pysql = lambda q: pandasql.sqldf(q, globals())
		data1_rep = pysql("select p_id as \"Patient ID\",exp as \"Expression Val\" from data1 ")
		data2_rep = pysql("select p_id as \"Patient ID\",exp as \"Expression Val\" from data2 ")
		data3_rep = pysql("select p_id as \"Patient ID\",exp as \"Expression Val\" from data3 ")
		data4_rep = pysql("select p_id as \"Patient ID\",exp as \"Expression Val\" from data4 ")
		return """<html>
					<form method="get" action="index">
              		<button type="submit">Return</button>
           			</form>
           			</form>
           			 <form method="post" action="processQuery5"> 
            			Custom Query on Result: 
            			<input type="text" name="qu"><br> 
    					<input type="submit">
    				</form>
    				<h2>F-statistics for Exp Values::</h2>"""+(str)(stats.f_oneway(data1['exp'].values,data2['exp'].values,data3['exp'].values,data4['exp'].values)[0])+"""
    				<h1>Exp values for patients with ALL<h3>(Rows-"""+str(len(data1.index))+""")</h3></h1>"""+data1_rep.to_html(index=False)+"""
    				<h1>Exp values for patients with AML<h3>(Rows-"""+str(len(data2.index))+""")</h3></h1>"""+data2_rep.to_html(index=False)+"""
    				<h1>Exp values for patients with colon tumor<h3>(Rows-"""+str(len(data3.index))+""")</h3></h1>"""+data3_rep.to_html(index=False)+"""
    				<h1>Exp values for patients with breast tumor<h3>(Rows-"""+str(len(data4.index))+""")</h3></h1>"""+data4_rep.to_html(index=False)+"""
    				
    				</html>"""
	@cherrypy.expose
	def processQuery5(self,qu,length=8):
		#global data1
		#data1=pandas.read_sql_query(query['5a'], cnx)
		#global data2
		#data2=pandas.read_sql_query(query['5b'], cnx)
		#global data3
		#data3=pandas.read_sql_query(query['5c'], cnx)
		#global data4
		#data4=pandas.read_sql_query(query['5d'], cnx)
		pysql = lambda q: pandasql.sqldf(q, globals())
		data5 = pysql(qu)
		return data5.to_html(index=False)

	@cherrypy.expose
	def query6(self, length=8):
		global data1
		data1=pandas.read_sql_query(query['6a'], cnx)
		global data2
		data2=pandas.read_sql_query(query['6b'], cnx)
		pysql = lambda q: pandasql.sqldf(q, globals())
		data1_rep = pysql("select p_id as \"Patient ID\", pb_id as  \"Probe Id\" ,exp as \"Expression Val\" from data1  ")
		data2_rep = pysql("select p_id as \"Patient ID\", pb_id as  \"Probe Id\" ,exp as \"Expression Val\" from data2 ")
		ALL_patientVecs={}
		AML_patientVecs={}
		grpdRows=data1.groupby(['p_id'])['exp'];
		for r in grpdRows:
			ALL_patientVecs[r[0]]=r[1].values
		grpdRows=data2.groupby(['p_id'])['exp'];
		for r in grpdRows:
			AML_patientVecs[r[0]]=r[1].values
		
		AML_pids=list(AML_patientVecs.keys())
		ALL_pids=list(ALL_patientVecs.keys())
		pccALLonly=[]
		
		for i in range(len(ALL_pids)):
			p=ALL_pids[i]
			for j in range(i+1,len(ALL_pids)):
				q=ALL_pids[j]
				#print(i+1,",",j+1,": " ,stats.pearsonr(ALL_patientVecs[p],ALL_patientVecs[q])[0])
				pccALLonly.append(stats.pearsonr(ALL_patientVecs[p],ALL_patientVecs[q])[0])
		print(float(len(pccALLonly)))
		pcc_ALL = sum(pccALLonly) / float(len(pccALLonly))
		pccML=[]
		for i in range(len(ALL_pids)):
			p=ALL_pids[i]
			for j in range(len(AML_pids)):
				q=AML_pids[j]
				pccML.append(stats.pearsonr(ALL_patientVecs[p],AML_patientVecs[q])[0])
		pcc_AM_AL = sum(pccML) / float(len(pccML))

		return """<html>
					<form method="get" action="index">
              		<button type="submit">Return</button>
           			</form>
           			<form method="post" action="processQuery6"> 
            			Custom Query on Result: 
            			<input type="text" name="qu"><br> 
    					<input type="submit">
    				</form>
           			<h2>Pearson Correlation Coeff for Exp Values for 2 patients in ALL::</h2>"""+str(pcc_ALL)+"""
           			<h2>Pearson Correlation Coeff for Exp Values for one patient in ALL and one in AML::</h2>"""+str(pcc_AM_AL)+"""
           			<h1>Exp values for patients with ALL<h3>(Rows-"""+str(len(data1.index))+""")</h3></h1>"""+data1_rep.to_html(index=False)+"""
    				<h1>Exp values for patients with AML<h3>(Rows-"""+str(len(data2.index))+""")</h3></h1>"""+data2_rep.to_html(index=False)+"""
    				"""
	@cherrypy.expose
	def processQuery6(self,qu):
		#global data1
		#data1=pandas.read_sql_query(query['6a'], cnx)
		#global data2
		#data2=pandas.read_sql_query(query['6b'], cnx)
		pysql = lambda q: pandasql.sqldf(q, globals())
		data3 = pysql(qu)
		return data3.to_html(index=False)
	@cherrypy.expose
	def query7_Disease(self):
		return """<form method="get" action="index">
        		<button type="submit">Return</button>
        		</form>
        		<form method="post" action="query7"> 
        		Select Disease for Classification:<br>
            			<input type="radio" name="disease" value="ALL">ALL<br>
  						<input type="radio" name="disease" value="AML"> AML<br>
  						<input type="radio" name="disease" value="Giloblastome"> Giloblastome<br>
  						<input type="radio" name="disease" value="Colon tumor"> Colon tumor<br>
  						<input type="radio" name="disease" value="Breast tumor"> Breast Tumor<br>
  						<input type="radio" name="disease" value="Flu"> Flu<br>
    			Select Test Patient to classify:<br>
    					 <input type="checkbox" name="patient" value="test1"> Patient 1<br>
    					 <input type="checkbox" name="patient" value="test2"> Patient 2<br>
    					 <input type="checkbox" name="patient" value="test3"> Patient 3<br>		
    					 <input type="checkbox" name="patient" value="test4"> Patient 4<br>
    					 <input type="checkbox" name="patient" value="test5"> Patient 5<br>
    					<input type="submit">
    				</form>"""

	@cherrypy.expose
	def query7(self,disease,patient):
		print('checking::')
		print(isinstance(patient,list))
		q="SELECT g.UID,d.p_id,mic.exp from microarray_fact mic INNER JOIN (probe pb, gene g, disease ds, Diagnosis d, sample s) on (mic.pb_id=pb.pb_id and pb.UID=g.UID and d.`ds_id`=ds.`ds_id` and d.p_id=s.p_id and mic.s_id=s.s_id) where ";
		criterion="ds.`name` =\""+disease+"\" ORDER BY d.p_id,g.UID;"
		query=q+criterion
		#print(query)
		global data1
		data1 = pandas.read_sql_query(query, cnx)
		criterion="ds.`name` !=\""+disease+"\" ORDER BY d.p_id,g.UID;"
		query = q+criterion
		global data2
		data2 = pandas.read_sql_query(query, cnx)
		#print(data1.head())
		#print(data2.head())
		#Part 1 --- Find Informative genes for the disease
		UID_CritVecs={}
		UID_NoCritVecs={}
		grpdRows=data1.groupby(['UID'])['exp'];
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
		if not InformativeUIDs:
			return """<html><form method="get" action="query7_Disease">
              		<button type="submit">Return</button>
           			</form> <h3>No Informative Genes Found</h3><br>
					   <h3>Classification not possible</h3><html>"""
		
		#Part 2-- Classify Test Patient For the Disease
		
		Crit_PidVecs={}
		NoCrit_PidVecs={}
		PnewVecs={}
		data1=data1[data1['UID'].isin(InformativeUIDs)]
		grpdRows=data1.groupby(['p_id'])['exp']
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
		for i in range (1,len(data3.columns)):
			PnewVecs[data3.columns[i]]=data3[data3.columns[i]].values
			print(PnewVecs[data3.columns[i]].shape)
		ew_pids=list(PnewVecs.keys())
		Crit_pids=list(Crit_PidVecs.keys())
		NoCrit_pids=list(NoCrit_PidVecs.keys())
		class_df = pandas.DataFrame(data ={'Test Patient':[],'Classified as':[]})

		if isinstance(patient,list):
			for pidnew in patient: #if single loop runs over each char!! 
				pnvec=PnewVecs[pidnew]
				pccCrit=[] #groupA RAs
				for i in range(len(Crit_pids)):
					p=Crit_pids[i]
					pccCrit.append(stats.pearsonr(pnvec,Crit_PidVecs[p])[0])

				pccNoCrit=[] #groupB RAs
				for i in range(len(NoCrit_pids)):
					p=NoCrit_pids[i]
					pccNoCrit.append(stats.pearsonr(pnvec,NoCrit_PidVecs[p])[0])
			#print(len(pccCrit))
			#print(len(pccNoCrit))
			#print(stats.ttest_ind(pccCrit,pccNoCrit,equal_var=True))
		
				if((stats.ttest_ind(pccCrit,pccNoCrit,equal_var=True)[1])<0.01):
					class_df=class_df.append({'Test Patient':pidnew, 'Classified as':'Having'},ignore_index=True)
				else:
					class_df=class_df.append({'Test Patient':pidnew, 'Classified as':'Not Having'},ignore_index=True)
		else:
			print('in else')
			pnvec=PnewVecs[patient]
			pccCrit=[] #groupA RAs
			for i in range(len(Crit_pids)):
				p=Crit_pids[i]
				pccCrit.append(stats.pearsonr(pnvec,Crit_PidVecs[p])[0])

			pccNoCrit=[] #groupB RAs
			for i in range(len(NoCrit_pids)):
				p=NoCrit_pids[i]
				pccNoCrit.append(stats.pearsonr(pnvec,NoCrit_PidVecs[p])[0])
			#print(len(pccCrit))
			#print(len(pccNoCrit))
			#print(stats.ttest_ind(pccCrit,pccNoCrit,equal_var=True))
		
			if((stats.ttest_ind(pccCrit,pccNoCrit,equal_var=True)[1])<0.01):
				class_df=class_df.append({'Test Patient':patient, 'Classified as':'Having'},ignore_index=True)
			else:
				class_df=class_df.append({'Test Patient':patient, 'Classified as':'Not Having'},ignore_index=True)

		print(class_df.head())
		return"""<html>
					<form method="get" action="query7_Disease">
              		<button type="submit">Return</button>
           			</form>
           			<h2>Informative Genes UIDs::</h2><br>"""+str(InformativeUIDs)+"""
           			<h2> Classification Results:<h2>"""+class_df.to_html(index=False)+"""
           			</html>"""

	@cherrypy.expose
	def custom_Query(self):
		return """<html>
					<form method="get" action="index">
              		<button type="submit">Return</button>
           			</form>
           			</form>
           			 <form method="post" action="processCustom"> 
            			Custom Query on DataBase: 
            			<textarea name="qu" style="width:768; height:350"></textarea><br> 
    					<input type="submit">
    				</form>"""

	@cherrypy.expose
	def processCustom(self,qu):
		data1 = pandas.read_sql_query(qu, cnx)
		return """<html>
				<h2> Classification Results:<h2>"""+data1.to_html(index=False)

	@cherrypy.expose
	def customTstat(self):			
		return """<form method="get" action="index">
        		<button type="submit">Return</button>
        		</form>
        		<form method="post" action="process_CustomTstat"> 
        		Select First Disease:<br>
            			<input type="radio" name="disease1" value="ALL">ALL<br>
  						<input type="radio" name="disease1" value="AML"> AML<br>
  						<input type="radio" name="disease1" value="Giloblastome"> Giloblastome<br>
  						<input type="radio" name="disease1" value="Colon tumor"> Colon tumor<br>
  						<input type="radio" name="disease1" value="Breast tumor"> Breast Tumor<br>
  						<input type="radio" name="disease1" value="Flu"> Flu<br>
  				Select Second Disease:<br>
            			<input type="radio" name="disease2" value="ALL">ALL<br>
  						<input type="radio" name="disease2" value="AML"> AML<br>
  						<input type="radio" name="disease2" value="Giloblastome"> Giloblastome<br>
  						<input type="radio" name="disease2" value="Colon tumor"> Colon tumor<br>
  						<input type="radio" name="disease2" value="Breast tumor"> Breast Tumor<br>
  						<input type="radio" name="disease2" value="Flu"> Flu<br>
  						Go Id Value: 
            			<input type="text" name="go"><br> 
    			<input type="submit">
    				</form>"""


	@cherrypy.expose
	def process_CustomTstat(self,disease1,disease2,go):
		print(disease2)
		q1 = "SELECT s.p_id,maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id =\""+go+"\"and ds.`name` =\""+disease1+"\"";
		q1_not = "SELECT s.p_id,maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id =\""+go+"\"and ds.`name` !=\""+disease1+"\"";
		global data1
		data1 = pandas.read_sql_query(q1, cnx)
		global data1_not
		data1_not = pandas.read_sql_query(q1_not, cnx)
		a=data1['exp'].values
		b=data1_not['exp'].values
		print(stats.tmean(a))
		print(stats.tmean(b))
		print(stats.tvar(a))
		print(stats.tvar(b))
		if disease1 == disease2:
			return """<html>
					<form method="get" action="index">
              		<button type="submit">Return</button>
           			</form>
           			</form>
    				<h2>T-statistics for Exp Values::</h2>"""+(str)(stats.ttest_ind(a,b,equal_var=True)[0])+"""
					<h1>Exp values for patients with """+disease1+"""<h3>(Rows-"""+str(len(data1.index))+""")</h3></h1>"""+data1.to_html(index=False)+"""
					<h1>Exp values for patients without """+disease1+"""<h3>(Rows-"""+str(len(data1_not.index))+""")</h3></h1>"""+data1_not.to_html(index=False)+"""
					</html>"""
		else:
			q2 = "SELECT s.p_id,maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id =\""+go+"\"and ds.`name` =\""+disease2+"\"";
			data2 = pandas.read_sql_query(q2, cnx)	
			b=data2['exp'].values
			print(stats.tmean(a))
			print(stats.tmean(b))
			print(stats.tvar(a))
			print(stats.tvar(b))
			return """<html>
				<form method="get" action="index">
            	<button type="submit">Return</button>
           		</form>
           		</form>
           		 
    			<h2>T-statistics for Exp Values::</h2>"""+(str)(stats.ttest_ind(a,b,equal_var=True)[0])+"""
				<h1>Exp values for patients with """+disease1+"""<h3>(Rows-"""+str(len(data1.index))+""")</h3></h1>"""+data1.to_html(index=False)+"""
				<h1>Exp values for patients with """+disease2+"""<h3>(Rows-"""+str(len(data2.index))+""")</h3></h1>"""+data2.to_html(index=False)+"""
				</html>"""				

	@cherrypy.expose
	def customFstat(self):
		return """<form method="get" action="index">
        		<button type="submit">Return</button>
        		</form>
        		<form method="post" action="process_CustomFstat"> 
        		Select Diseases:(At least 3)<br>
            			<input type="checkbox" name="disease" value="ALL">ALL<br>
  						<input type="checkbox" name="disease" value="AML"> AML<br>
  						<input type="checkbox" name="disease" value="Giloblastome"> Giloblastome<br>
  						<input type="checkbox" name="disease" value="Colon tumor"> Colon tumor<br>
  						<input type="checkbox" name="disease" value="Breast tumor"> Breast Tumor<br>
  						<input type="checkbox" name="disease" value="Flu"> Flu<br>
    				Go Id Value: 
            			<input type="text" name="go"><br>
            			<input type="submit">
    				</form>"""

	@cherrypy.expose
	def process_CustomFstat(self,disease,go):
		data=[]
		print(disease)
		exp=[]
		i=0
		for dis in disease:
			print(i)
			q = "SELECT s.p_id,maf.exp from GOAnnotation ga inner join (probe pb,Diagnosis dg,disease ds, microarray_fact maf, sample s) on (ga.UID = pb.UID and pb.pb_id=maf.pb_id and dg.ds_id= ds.ds_id and dg.p_id=s.p_id and maf.s_id= s.s_id) where ga.go_id =\""+go+"\"and ds.`name` =\""+dis+"\""
			data.insert(i,pandas.read_sql_query(q, cnx))
			print(data[i].head())
			i=i+1
		i=0
		for frame in data:
			exp.insert(i,data[i]['exp'].values)
			i=i+1
		print(exp) 
		print((str)(stats.f_oneway(*exp)[0]))
		return """<html>
		<form method="get" action="customFstat">
        		<button type="submit">Return</button>
        		</form>
		<h3>FStatistics::"""+(str)(stats.f_oneway(*exp)[0])+"""

				 	</html>"""

if __name__ == '__main__':
	cherrypy.quickstart(HelloWorld())
