import os,sys
import time
from datetime import date, timedelta, datetime

leapMonthDays = [0,31,29,31,30,31,30,31,31,30,31,30,31]
unleapMonthDays = [0,31,28,31,30,31,30,31,31,30,31,30,31]

def days_between(date_str1, date_str2):
	# Convert the strings to datetime objects
	date1 = datetime.strptime(date_str1, '%Y-%m-%d')
	date2 = datetime.strptime(date_str2, '%Y-%m-%d')

	# Calculate the difference between the two dates
	delta = date2 - date1

	# Get the number of days
	days = abs(delta.days)
	return days

def monthfirstday():
	d = datetime.now()
	return '%4d-%02d-01' % (d.year, d.month)

def curDatetime():
	return datetime.now()

def curDateString():
	d = curDatetime()
	return '%04d-%02d-%02d' %(d.year,d.month,d.day)
	
def curTimeString():
	d = curDatetime()
	return '%02d:%02d:%02d' %(d.hour,d.minute,d.second)
	
def timestampstr():
	d = curDatetime()
	return '%04d-%02d-%02d %02d:%02d:%02d.%03d' % (d.year,
			d.month,
			d.day,
			d.hour,
			d.minute,
			d.second,
			d.microsecond/1000)
	
def isMonthLastDay(d):
	dd = timedelta(1)
	d1 = d + dd
	if d1.month != d.month:
		return True
	return False

def isLeapYear(year):
	if year % 4 == 0 and year % 100 == 0 and not (year % 400 == 0):
		return True
	return False
		
def timestamp(dt):
	return int(time.mktime((dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second,dt.microsecond,0,0)))

def timeStampSecond(dt):
	return int(time.mktime((dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second,0,0,0)))

def addSeconds(dt,s):
	ndt = dt + timedelta(0,s)
	return ndt
	
def monthMaxDay(y,m):
	if isLeapYear(y):
		return leapMonthDays[m]
	return unleapMonthDays[m]

def date2str(dt=None):
	if dt is None:
		dt = curDatetime()
	return '%04d-%02d-%02d' % (dt.year,dt.month,dt.day)

def time2str(dt):
	return '%02d:%02d:%02d' % (dt.hour,dt,minute,dt.second)
	
def str2Date(dstr):
	try:
		haha = dstr.split(' ')
		y,m,d = haha[0].split('-')
		H = M = S = 0
		if len(haha) > 1:
			H,M,S = haha[1].split(':')
		return ymdDate(int(y),int(m),int(d),int(H),int(M),int(S))
	except Exception as e:
		print(e)
		return None
		
def ymdDate(y,m,d,H=0,M=0,S=0):
	return datetime(y,m,d,H,M,S)
	
def str2Datetime(dstr):
	x = dstr.split(' ')
	d = x[0]
	t = '00:00:00'
	if len(x) > 1:
		t = x[1]
	y,m,d = d.split('-')
	H,M,S = t.split(':')
	return datetime(int(y),int(m),int(d),int(H),int(M),int(S))
	
def strdate_add(date_str, days=0, months=0, years=0):
	dt = str2Datetime(date_str)
	dt = dateAdd(dt, days=days, months=months, years=years)
	ds = date2str(dt)
	return ds

def addMonths(dt,months):
	y = dt.year
	m = dt.month + months
	d = dt.day
	mm = (m - 1) % 12 + 1
	md = int((m - 1) / 12)
	y += md
	m = mm
	maxd = monthMaxDay(y,m)
	if d > maxd:
		d = maxd
	return ymdDate(y,m,d)

def addYears(dt,years):
	y = dt.year + years
	m = dt.month
	d = dt.day
	maxd = monthMaxDay(y,m)
	if d > maxd:
		d = maxd
	return ymdDate(y,m,d)

def dateAdd(dt,days=0,months=0,years=0):
	if days != 0:
		dd = timedelta(days)
		dt = dt + dd	
	if months != 0:
		dt = addMonths(dt,months)
	if years != 0:
		dt = addYears(dt,years)
	return dt

def firstSunday(dt):
	f = dt.weekday()
	if f<6:
		return dt + timedelta(7 - f)
	return dt

DTFORMAT = '%Y%m%d %H%M%S'
def getCurrentTimeStamp() :
	t = time.localtime()
	return TimeStamp(t)
	
def TimeStamp(t) :
	return time.strftime(DTFORMAT,t)

def StepedTimestamp(baseTs,ts,step) :
	if step<2 :
		return ts
	offs = int(timestampSub(ts,baseTs))
	step = int(step)
	r,m = divmod(offs,step)
	if m < step/2 :
		return timestampAdd(baseTs,step * r)
	else :
		return timestampAdd(baseTs,step * (r+1))
		
def timestampAdd(ts1,ts2) :
	t1 = time.strptime(ts1,DTFORMAT)
	tf = time.mktime(t1)
	if type(ts2)=='' :
		t2 = time.strptime(ts2,DTFORMAT)
		ts2 = time.mktime(t2)
	tf += ts2
	t = time.localtime(tf)
	return TimeStamp(t)

def timestampSub(ts1,ts2) :
	t1 = time.strptime(ts1,DTFORMAT)
	t2 = time.strptime(ts2,DTFORMAT)
	ret = time.mktime(t1) - time.mktime(t2)
	return int(ret)

def timestamp2dt(t):
	return datetime.fromtimestamp(t)

def date_weekinyear(date_str):
	w = datetime.strptime(date_str, '%Y-%m-%d').strftime('%W')
	return date_str[:5] + w

def date_season(date_str):
	m = date_str[5:7]
	sl = {
		'01':'1',
		'02':'1',
		'03':'1',
		'04':'2',
		'05':'2',
		'06':'2',
		'07':'3',
		'08':'3',
		'09':'3',
		'10':'4',
		'11':'4',
		'12':'4',
	}
	s = sl.get(m)
	return date_str[:5] + s

"""
Patterns =
	'D'
	'W[0-6]'
	'M[00-31]'
	'S[0-2]-[00-31]'
	'Y[01-12]-[00-31]'
}
"""

def str2date(sd):
	a = [ int(i) for i in sd.split('-') ]
	return date(*a)

def is_monthend(dt):
	if isinstance(dt, str):
		dt = str2date(dt)
	nxt_day = dt + timedelta(days=1)
	if dt.month != nxt_day.month:
		return True
	return False

def is_match_pattern(pattern, strdate):
	"""
R:代表实时
D：代表日
W[0-6]：代表周日到周六
M[00-31]:代表月末月到某一天
S[1-3]-[00-31]:代表季度第几个月的第几天
Y[1-12]-[00-31]:代表一年中的某个月的某一天
	"""
	if pattern == 'D':
		return True
	dt = str2date(strdate)
	if pattern.startswith('W'):
		w = (int(pattern[1]) + 6) % 7
		if dt.weekday() == w:
			return True
		return False
	if pattern.startswith('M'):
		day = int(pattern[1:])
		if day == 0 and is_monthend(dt):
			return True
		if day == dt.day:
			return True
		return False
	if pattern.startswith('S'):
		m,d = [ int(i) for i in pattern[1:].split('-') ]
		print(f'{m=}-{d=}, {dt.month=} {dt.day}')
		m %= 4
		if m == dt.month % 4 and d == dt.day:
			return True
		return False
	if pattern.startswith('Y'):
		m,d = [ int(i) for i in pattern[1:].split('-') ]
		print(f'{m=}-{d=}, {dt.month=} {dt.day}')
		if m == dt.month and d == dt.day:
			return True
		return False

