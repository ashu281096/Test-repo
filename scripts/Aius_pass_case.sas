Convert the following SAS code to Python:
**signoff;


	/*%let app130=172.22.248.100; */
%let app130=172.22.243.150;
	/*%let app130=172.22.37.69;*/

options comamid=tcp remote=APP130; 
filename rlink '!sasroot\connect\saslink\tcpwin.scr';
*signon username = 1168059 password = "Nbsm0723" ;  * mustchg;
signon app130; 
libname rwork slibref=work server=app130;


/*
	LIBNAME AIUS  			"\\192.168.0.45\users\DataMart\Basel_ii\aius";    * 124 server;

LIBNAME AIUS slibref=AIUS server=APP130;
*/

LIBNAME AIUS  "\\twwpapsas01\DATA\DataMart\basel_ii\aius";

	proc sql;
	create table a000 as
	select a.app_no,a.add_date,a.cus_id,a.flow_type,a.case_type,a.app_type,a.bus_group,a.reject_code,a.Ao_Mt_User,b.product_code,b.Product_Unity,b.loan_code,b.apply_amt
	from AIUS.aius003t (read=sba) a left join AIUS.aius005t (read=sba) b on a.app_no=b.app_no
    where substr(a.app_no,1,2) in ('11' '12');
	create table a001 as
	select a.*,b.card_limit
	from a000 a left join AIUS.aius029t (read=sba) b on a.app_no=b.app_no;
	create table a002 as
	select a.*,b.limit_appr,b.order_code
	from a001 a left join AIUS.aius031t (read=sba) b on a.app_no=b.app_no;
   	create table a003 as
	select a.*,b.notify_no,b.isfake,b.add_date as notify_date,b.Fake_Code
	from a002 a left join AIUS.aius032t (read=sba) b on a.app_no=b.app_no;
	create table a004 as
	select a.*,b.ApplyChannel
	from a003 a left join AIUS.aius010t (read=sba) b on a.app_no=b.app_no;
quit;

data a003a;
	set a004;
	length pd_seg $15.;
	month=substr(add_date,2,4);
	month2=substr(notify_date,2,4);
	if flow_type in ('Z0' 'R0') and reject_code='  ' then appr_flag='Y';
	else appr_flag='N';
	if order_code='N' then limit_appr2=0;
	else if order_code='Y' then limit_appr2=limit_appr;
	else limit_appr2=0;
	select;
	when (case_type='1')  pd_seg='P01-M&A';
	when (case_type='6' and bus_group in ('CPL' 'MGE')) pd_seg='P02-P LOAN';
	when (case_type='6' and bus_group eq 'BIL') pd_seg='P03-BIL';
	when (case_type='6' and bus_group eq 'MME') pd_seg='P01-M&A';
	when (case_type='5') pd_seg='P04-Card';
	otherwise pd_seg='P99-missing';
	end;
	if case_type='3' then delete;
run;

%let yymm=11212;
data b000;
	set a003a;
	if notify_no ^=' ';
	if isfake='Y' then fraud_flag='Y';
	else fraud_flag='N';
	format d1 mmddyy8.;
	format d2 mmddyy8.;
	 d1 = mdy(substr(add_date,4,2),substr(add_date,6,2),1911+substr(add_date,1,3)*1);
	 d2 = mdy(substr(notify_date,4,2),substr(notify_date,6,2),1911+substr(notify_date,1,3)*1);
	 if substr(notify_date,1,5) ne "&yymm" then delete;
run;



/****data output****/

PROC EXPORT DATA=B000
   		OUTFILE="M:\Seven\每月看件報表\每月E-LOAN案件資料\Raw data\Pass_case11212.xlsx"
	 	DBMS=XLSX
	 	REPLACE;
	RUN;


/*** AFD mapping ****/
	data aius34t;
		set aius.aius034t (read=sba);
		if substr(Notify_No,1,3) in ('111');
	run; 

PROC SQL;
	CREATE TABLE B000A AS
	SELECT a.app_no,a.cus_id,b.IsFake,b.Fake_Code,b.Content
	FROM B000 a LEFT JOIN aius34t b on a.Notify_No=b.Notify_No;
QUIT;


PROC EXPORT DATA=B000A
		DBMS=XLSX
   		OUTFILE="M:\AFD\REPORT\\ELOAN_MAPPING_2203.xlsx"
		REPLACE;
		SHEET="aius34t";
RUN;	
