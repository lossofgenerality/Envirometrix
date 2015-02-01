from datetime import *
import re

class Tag():
    """
    This class represents a format tag indicating a single datum which can be parsed from the name of a data file
    """    
    
    """
    Methods
    """
    def __init__(self, tag, name, regex, **kwargs):

        self.tag = tag
        self.name = name.replace(' ', '_')
        self.regex = regex

        self.description = 'N/A'
        self.default = ''


        '''
        The relations property is a callable which takes a dictionary
        of data parsed from a filename and return a dictionary of additional
        data which are to be applied to update the dictionary.
        '''
        self.relations = lambda vars: vars
        
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
        
    @property
    def re(self):
        """
        Returns regex group for this tag.
        """
        return '(?P<{}>{})'.format(self.name, self.regex)
        

### Starting Date and Time Data ###

# Tags #    

startYear = Tag(
    tag='%sY',
    name='startYear',
    regex=r'\d\d\d\d',
    description="""
        Starting year with century as a decimal number.
    """,
    default=datetime.now().strftime('%Y')
)

startMonth = Tag(
    tag='%sm',
    name='startMonth',
    regex=r'1[0-2]|0[1-9]|[1-9]',
    description="""
        Starting month as a zero-padded decimal number.
    """,
    default='01'
)

startDay = Tag(
    tag='%sD',
    name='startDay',
    regex=r'3[0-1]|[1-2]\d|0[1-9]|[1-9]| [1-9]',
    description="""
        Starting day as a zero-padded decimal number.
    """,
    default='01'
)

startHour = Tag(
    tag='%sH',
    name='startHour',
    regex=r'2[0-3]|[0-1]\d|\d',
    description="""
        Starting hour on a 24 hour clock as a zero-padded decimal number.
    """,
    default='00'
)

startMinute = Tag(
    tag='%sM',
    name='startMinute',
    regex=r'[0-5]\d|\d',
    description="""
        Starting minute as a zero-padded decimal number.
    """,
    default='00'
)

startSecond = Tag(
    tag='%sS',
    name='startSecond',
    regex=r'6[0-1]|[0-5]\d|\d',
    description="""
        Starting second as a zero-padded decimal number.
    """,
    default='00'
)

# General Relations #

def __get_starttime(vars):
    """
    Use existing start time and date info, and default values, to fill in all start time info.
    """
    if not 'startSecond' in vars:
        vars['startSecond'] = startSecond.default
    if not 'startMinute' in vars:
        vars['startMinute'] = startMinute.default
        
    starttime = time(int(vars['startHour']), int(vars['startMinute']), int(vars['startSecond']))
    vars['startTime'] = starttime
    if 'startDate' in vars:
        vars['startDatetime'] = datetime.combine(vars['startDate'], starttime)
    
    return vars


def __get_startdate(vars):
    """
    Use existing start time and date info, and default values, to fill in all start date and time info.
    """
    if not 'startDay' in vars:
        vars['startDay'] = startDay.default
    if not 'startMonth' in vars:
        vars['startMonth'] = startMonth.default
    
    startdate = date(int(vars['startYear']), int(vars['startMonth']), int(vars['startDay']))
    vars['startDate'] = startdate
    # if not 'startTime' in vars:
        # vars['startHour'] = startHour.default
        # vars['startMinute'] = startMinute.default
        # vars['startSecond'] = startSecond.default

    return __get_starttime(vars)

# Specific Relations #

def __startYear_relations(vars):
    vars = __get_startdate(vars)
    return vars
startYear.relations = __startYear_relations
        
def __startMonth_relations(vars):
    vars = __get_startdate(vars)
    return vars
startMonth.relations = __startMonth_relations
    
def __startDay_relations(vars):
    vars = __get_startdate(vars)
    return vars
startDay.relations = __startDay_relations

def __startHour_relations(vars):
    vars = __get_starttime(vars)
    return vars
startHour.relations = __startHour_relations

def __startMinute_relations(vars):
    vars = __get_starttime(vars)
    return vars
startMinute.relations = __startMinute_relations
    
def __startSecond_relations(vars):
    vars = __get_starttime(vars)
    return vars
startSecond.relations = __startSecond_relations



### Ending Date and Time Data ###

# Tags #    

endYear = Tag(
    tag='%eY',
    name='endYear',
    regex=r'\d\d\d\d',
    description="""
        Ending year with century as a decimal number.
    """,
    default=datetime.now().strftime('%Y')
)

endMonth = Tag(
    tag='%em',
    name='endMonth',
    regex=r'1[0-2]|0[1-9]|[1-9]',
    description="""
        Ending month as a zero-padded decimal number.
    """,
    default='01'
)

endDay = Tag(
    tag='%eD',
    name='endDay',
    regex=r'3[0-1]|[1-2]\d|0[1-9]|[1-9]| [1-9]',
    description="""
        Ending day as a zero-padded decimal number.
    """,
    default='01'
)

endHour = Tag(
    tag='%eH',
    name='endHour',
    regex=r'2[0-3]|[0-1]\d|\d',
    description="""
        Ending hour on a 24 hour clock as a zero-padded decimal number.
    """,
    default='00'
)

endMinute = Tag(
    tag='%eM',
    name='endMinute',
    regex=r'[0-5]\d|\d',
    description="""
        Ending minute as a zero-padded decimal number.
    """,
    default='00'
)

endSecond = Tag(
    tag='%eS',
    name='endSecond',
    regex=r'6[0-1]|[0-5]\d|\d',
    description="""
        Ending second as a zero-padded decimal number.
    """,
    default='00'
)

# General Relations #

def __get_endtime(vars):
    """
    Use existing end time and date info, and default values, to fill in all end time info.
    """
    # if not 'endSecond' in vars:
        # vars['endSecond'] = endSecond.default
    # if not 'endMinute' in vars:
        # vars['endMinute'] = endMinute.default
    
    endtime = time(int(vars['endHour']), int(vars['endMinute']), int(vars['endSecond']))
    vars['endTime'] = endtime
    if 'endDate' in vars:
        vars['endDatetime'] = datetime.combine(vars['endDate'], endtime)
    
    return vars

def __get_enddate(vars):
    """
    Use existing start time and date info, and default values, to fill in all start date and time info.
    """
    if not 'endDay' in vars:
        vars['endDay'] = endDay.default
    if not 'endMonth' in vars:
        vars['endMonth'] = endMonth.default
    
    enddate = date(int(vars['endYear']), int(vars['endMonth']), int(vars['endDay']))
    vars['endDate'] = enddate
    # if not 'endTime' in vars:
        # vars['endHour'] = endHour.default
        # vars['endMinute'] = endMinute.default
        # vars['endSecond'] = endSecond.default

    return __get_endtime(vars)

# Specific Relations #

def __endYear_relations(vars):
    vars = __get_enddate(vars)
    return vars
endYear.relations = __endYear_relations
        
def __endMonth_relations(vars):
    vars = __get_enddate(vars)
    return vars
endMonth.relations = __endMonth_relations
    
def __endDay_relations(vars):
    vars= __get_enddate(vars)
    return vars
endDay.relations = __endDay_relations

def __endHour_relations(vars):
    vars = __get_endtime(vars)
    return vars
endHour.relations = __endHour_relations

def __endMinute_relations(vars):
    vars = __get_endtime(vars)
    return vars
endMinute.relations = __endMinute_relations
    
def __endSecond_relations(vars):
    vars = __get_endtime(vars)
    return vars
endSecond.relations = __endSecond_relations



### Geographical Data ###

# Tags #    

startLatitude = Tag(
    tag='%sLat',
    name='startLatitude',
    regex=r'[-NSns]*?\d+(.\d*)',
    description="""
        Starting latitude expressed as a number between -90 and 90.
        Alternatively, a number between 0 and 90 preceeded by N or S.
    """,
    default='-90'
)

endLatitude = Tag(
    tag='%eLat',
    name='endLatitude',
    regex=r'[-NSns]*?\d+(.\d*)',
    description="""
        Starting latitude expressed as a number between -90 and 90.
        Alternatively, a number between 0 and 90 preceeded by N or S.
    """,
    default='90'
)

startLongitude = Tag(
    tag='%sLon',
    name='startLongitude',
    regex=r'[-EWew]*?\d+(.\d*)',
    description="""
        Starting latitude expressed as a number between -180 and -180.
        Alternatively, a number between 0 and 180 preceeded by E or W.
    """,
    default='-180'
)

endLongitude = Tag(
    tag='%eLon',
    name='endLongitude',
    regex=r'[-EWew]*?\d+(.\d*)',
    description="""
        Starting latitude expressed as a number between -180 and 180.
        Alternatively, a number between 0 and 90 preceeded by E or W.
    """,
    default='180'
)

orbitNumber = Tag(
    tag='%orb',
    name='orbitNumber',
    regex=r'\d+',
    description="""
        The numerical orbit designation.
    """
)

# General Relations #



# Specific Relations #


### Tag Use Functions ###

tags = [startYear, startMonth, startDay, startHour, startMinute, startSecond,
        endYear, endMonth, endDay, endHour, endMinute, endSecond,
        startLatitude, endLatitude, startLongitude, endLongitude, orbitNumber]

def parse(fmt_str, filename):
    """
    Parses filename using all available format tags.
    """
    temp = fmt_str
    for tag in tags:
        temp = temp.replace(tag.tag, tag.re)

    return re.search(temp, filename).groupdict()

def tag_table():
    """
    Builds a table containing documentation on all format tags.
    """ 
    table = '<center><table>'
    table += ''.join(['<tr><td>{}</td><td>{}</td><td>{}</td></tr>'.format(tag.tag, tag.name, tag.description) for tag in tags])
    table += '</table></center>'
    return table

