from datetime import *
import inspect
import sys


class ArgTypeMixin(object):
    """
    This class represents the common features of all types of extra arguments and provides a base class.
    """

    """
    Properties
    """
    common_head = ''
    # head content which only needs to be included once, even 
    # if more than one instance of the same type is being used
    
    """
    Methods
    """
    def __init__(self, label, description, default, head_content = '', label_loc='left'):
        self.label = label
        self.description = description
        self.default = default
        self.head_content = head_content
        self.label_location = label_loc
        
    def __unicode__(self):
        return self.label
        
    def validate(self, value):
        """
        Validates form field (not yet implimented).
        """
        return True
        
    def code(self, content, **kwargs):
        """
        Returns html code for argument input field.
        """
        fmt_dic = {
            'description': self.description,
            'label': self.label,
            'content': content
        }
        fmt_dic.update(kwargs)
        if self.label_location == 'left':
            html = r"""
                <table class="arg" style="width:100%;">
                    <tr title="{description}">
                        <td>
                            <b>{label}:</b>
                        </td>
                        <td>
                                {content}
                        </td>
                    </tr>
                </table>
            """.format(**fmt_dic)
        elif self.label_location =='top':
            html = r"""
                <table class="arg" style="width:100%;">
                    <tr title="{description}">
                        <tr><td>
                            <b>{label}:</b>
                        </td></tr>
                        <tr><td>
                                {content}
                        </td></tr>
                    </tr>
                </table>
            """.format(**fmt_dic)
        elif self.label_location =='none':
            html = r"""
                <table class="arg" style="width:100%;">
                    <tr title="{description}">
                        <td>
                                {content}
                        </td>
                    </tr>
                </table>
            """.format(**fmt_dic)
        
        return html
    
    def parse(self, request):
        """
        Pulls relevant values from POST request and returns a dict
        """
        temp_lab = self.label.replace(' ', '_')
        return {temp_lab: request.POST['_extra_'+templab]}
        
        
def build_head(args):
    """
    Compiles head content for the given 2D array of args into a block of js.
    """
    argtypes = []
    common_scripts = []
    instance_scripts = []
    
    for row in range(len(args)):
        for arg in args[row]:
            if not type(arg) in argtypes:
                argtypes.append(type(arg))
            instance_scripts.append(arg.head_content)

    common_scripts = [argtype.common_head for argtype in argtypes]
    return '\n\n'.join(common_scripts + instance_scripts)


def build_menu(args):
    """
    Compiles body content for the given 2D array of args into a block of html.
    """
    c = '<table class="wrapper" style="width:100%;">'
    for row in range(len(args)):
        c += r'''
            <tr>
                <td>
                    <table class="row" style="width:100%;">
                        <tr>
        '''
        for arg in args[row]:
            c += r'''
                            <td>
                                {}
                            </td>
            '''.format(arg.code)
        c += r'''
                        </tr>
                    </table>
                </td>
            </tr>
        '''
    c += '\n</table>'
    return c


def list_argtypes():
    """
    Compiles a list of available arg types.
    """
    current_module = sys.modules[__name__]
    test =  lambda member: inspect.isclass(member) and member.__module__ == __name__
    types = dict(inspect.getmembers(sys.modules[__name__], test))
    del types['ArgTypeMixin']
    return types
    

def doc_table():
    """
    Builds an html table containing documentation.
    """
    html = '''
        \n<p><table>
        <tr><td><b>Available types:</b></td></tr>
        '''
    for type, path in list_argtypes().items():
        initstring = '{}({})'.format(type, ', '.join(inspect.getargspec(path.__init__).args))
        html += '''
            \n<tr style="border-bottom: 2px solid gray;">
                <td>{}</td>
                <td style="width:30%;">{}</td>
                <td>{}</td>
            </tr>
        '''.format(type, path.__doc__, initstring)
    html += '\n</table></p>'
    return html
    
    
class IntegerArg(ArgTypeMixin):
    """
    This class represents a single integer value.
    """
    
    """
    Properties
    """
    
    """
    Methods
    """
       
    @property
    def code(self):
        fmt_dic = {
            'label': self.label.replace(' ', '_'),
            'default': self.default
            }
        content = """
            <input type="text" class="intarg" name="_extra_{label}" value="{default}"/>
            """.format(**fmt_dic)
        
        return super(IntegerArg, self).code(content)
        
        
class DecimalArg(ArgTypeMixin):
    """
    This class represents a single decimal number.
    """
    
    """
    Properties
    """
    
    """
    Methods
    """
    
    @property
    def code(self):
        fmt_dic = {
            'label': self.label.replace(' ', '_'),
            'default': self.default
            }
        content = """
            <input type="text" name="_extra_{label}" value="{default}"/>
            """.format(**fmt_dic)
        
        return super(DecimalArg, self).code(content)
        
        
class PercentArg(ArgTypeMixin):
    """
    This class represents a single percentage.
    """
    
    """
    Properties
    """
    
    """
    Methods
    """
    
    @property
    def code(self):
        fmt_dic = {
            'label': self.label.replace(' ', '_'),
            'default': self.default
            }
        content = """
            <input type="text" id="_extra_{label}" value="{default}"/> %
            """.format(**fmt_dic)
        
        return super(PercentArg, self).code(content)
        
        
class StringArg(ArgTypeMixin):
    """
    This class represents a single string argument.
    """
    
    """
    Properties
    """
    
    """
    Methods
    """
    
    @property
    def code(self):
        fmt_dic = {
            'label': self.label.replace(' ', '_'),
            'default': self.default
            }
        content = """
            <input type="text" name="_extra_{label}" value="{default}"/>
            """.format(**fmt_dic)
        
        return super(StringArg, self).code(content)
        
        
class GeoRegionArg(ArgTypeMixin):
    """
    This class represents a rectangular geographic region defined by latitude and longitude ranges.
    """
    
    """
    Properties
    """
    common_head = '''
        headvars['region_colors'] = ['#FFFF00', '#FF00FF', '#00FF00', '#0000FF', '#FF0000'];
        var regions;
        var map;

        $( function(){
            
            headvars['regions'] = {
                'new_rectangle': function(latstart, latend, lonstart, lonend){
                    var color = headvars.region_colors.pop();
                    var rect = {
                        'latstart': latstart,
                        'latend': latend,
                        'lonstart': lonstart,
                        'lonend': lonend,
                        'obj_settings': {
                            strokeColor: color,
                            strokeOpacity: 0.8,
                            strokeWeight: 2,
                            fillColor: color,
                            fillOpacity: 0.35,
                            map: map,
                            bounds: new google.maps.LatLngBounds(
                                new google.maps.LatLng(Number(latstart.val()), Number(lonstart.val())),
                                new google.maps.LatLng(Number(latend.val()), Number(lonend.val()))),
                            editable: true,
                            draggable: true
                            },
                            
                        'update': function(){
                            this.obj_settings.bounds = new google.maps.LatLngBounds(
                                new google.maps.LatLng(Number(latstart.val()), Number(lonstart.val())),
                                new google.maps.LatLng(Number(latend.val()), Number(lonend.val())))
                            if (this.map_object) this.map_object.setMap(null);
                            this.map_object = new google.maps.Rectangle(this.obj_settings);
                            this.map_object.setMap(headvars.map);
                            },
                            
                        'updatebounds': function(){
                            var ne = this.getBounds().getNorthEast();
                            var sw = this.getBounds().getSouthWest();
                            
                            latstart.val( sw.lat().toPrecision(8) );
                            latend.val( ne.lat().toPrecision(8) );
                            lonstart.val( sw.lng().toPrecision(8) );
                            lonend.val( ne.lng().toPrecision(8) );
                            },
                            
                        'redraw': function(){
                            if (this.map_object) this.map_object.setMap(null); 
                            this.map_object = new google.maps.Rectangle(this.obj_settings);
                            this.map_object.setMap(headvars.map);
                            google.maps.event.addListener(this.map_object, 'bounds_changed', this.updatebounds);
                        },
                    };
                    return rect
                }
            };
            $( ".map" ).first().prepend('<td colspan=4 title=""><div id="map-canvas"></div></td>');
            $( "#map-canvas" ).css("height", "500px");
            headvars['map'] = new google.maps.Map(document.getElementById('map-canvas'), {
                zoom: 2,
                center: new google.maps.LatLng(0, 0),
                streetViewControl: false,
                panControl: false
            });
        } );
    '''
    
    """
    Methods
    """
    
    def __init__(self, label, description, labels, defaults, **kwargs):
        self.subargs = [DecimalArg(labels[i], '', defaults[i], **kwargs) for i in range(4)]
        self.latmin, self.latmax, self.lonmin, self.lonmax = self.subargs
        super(GeoRegionArg, self).__init__(label, description, '', label_loc = 'none')
        self.head_content = '''
            $( function(){{
                headvars.regions['{label}'] = headvars.regions.new_rectangle($( "[name=_extra_{latstart}]" ), $( "[name=_extra_{latend}]" ), $( "[name=_extra_{lonstart}]" ), $( "[name=_extra_{lonend}]" ));
                headvars.regions.{label}.redraw();
                $( "[name=_extra_{latstart}]" ).attr('oninput', 'headvars.regions.{label}.update()')
                $( "[name=_extra_{latend}]" ).attr('oninput', 'headvars.regions.{label}.update()')
                $( "[name=_extra_{lonstart}]" ).attr('oninput', 'headvars.regions.{label}.update()')
                $( "[name=_extra_{lonend}]" ).attr('oninput', 'headvars.regions.{label}.update()')
            }});
        '''.format(
            **{key.replace(' ', '_') : val.replace(' ', '_') for (key, val) in {
                'label': label,
                'latstart': labels[0],
                'latend': labels[1],
                'lonstart': labels[2],
                'lonend': labels[3],
                }.items()
            })

        
    @property
    def code(self):
        fmt_dic = {
            'label': self.label.replace(' ', '_'),
            'default': self.default
            }
        content = '''
            <table style="width:100%;">
                <tr class="map"></tr>
                <tr>
        '''
        content += '\n'.join(['<td>{}</td>'.format(arg.code) for arg in self.subargs])
        content += '</tr></table>'
        return super(GeoRegionArg, self).code(content)
        
    def parse(self, request):
        vals = {}
        [vals.update(dic) for dic in [var.parse(request) for var in self.subargs]]
        return vals
        
        
class BooleanArg(ArgTypeMixin):
    """
    This class represents a single boolean value.
    """
    
    """
    Properties
    """
    
    """
    Methods
    """
    
    @property
    def code(self):
        fmt_dic = {
            'label': self.label.replace(' ', '_'),
            'default': self.default
            }
        content = """
            <input type="checkbox" name="_extra_{label}" value="{default}"/>
            """.format(**fmt_dic)
        
        return super(BooleanArg, self).code(content)
        
        
class DateArg(ArgTypeMixin):
    """
    This class represents a date value
    """
    
    """
    Properties
    """
    input_fmt = "%m/%d/%Y"
    output_fmt = "%Y%m%d"
    common_head = '''
            $( function(){
                $( ".dateinput" ).datepicker();
            });
        '''
    
    """
    Methods
    """
    
    @property
    def code(self):
        fmt_dic = {
            'label': self.label.replace(' ', '_'),
            'default': self.default
            }
        content = """
            <input class="dateinput" type="text" name="_extra_{label}" value="{default}"/>
            """.format(**fmt_dic)
        
        return super(DateArg, self).code(content)

        
    def parse(self, request, language):
        label = self.label.replace(' ', '_')
        rawdate = request.POST['_extra_'+label]
        vals = {self.label: date.strptime(input_fmt, rawdate).strftime(output_fmt)}
        return super(DateArg, self).parse(vals, language)
        
        
class TimeArg(ArgTypeMixin):
    """
    This class represents a time value.
    """
    
    """
    Properties
    """
    input_fmt = "%H:%M:%S"
    output_fmt = "%H%M%S"
    
    """
    Methods
    """
    
    @property
    def code(self):
        fmt_dic = {
            'label': self.label.replace(' ', '_'),
            'default': self.default
            }
        content = """
            <input type="text" id="_extra_{label}" value="{default}"/>
            """.format(**fmt_dic)
        
        return super(TimeArg, self).code(content)

        
    def parse(self, request, language):
        label = self.label.replace(' ', '_')
        rawtime = request.POST['_extra_'+label]
        vals = {self.label: time.strptime(self.input_fmt, rawtime).strftime(self.output_fmt)}
        return super(TimeArg, self).parse(vals, language)
        
        
class DatetimeArg(ArgTypeMixin):
    """
    This class represents the a combination of a date and a time value.
    """
    
    """
    Properties
    """
    output_fmt = DateArg.output_fmt + TimeArg.output_fmt
    common_head = DateArg.common_head
    
    """
    Methods
    """
    def __init__(self, label, description, defaults, **kwargs):
        s = label.replace(' ', '_')
        self.datearg = DateArg('_extra_{}_date'.format(s), description, defaults[0], label_loc='none')
        self.timearg = TimeArg('_extra_{}_time'.format(s), description, defaults[1], label_loc='none')
        self.subargs = [self.datearg, self.timearg]
        super(DatetimeArg, self).__init__(label, description, '', **kwargs)
        
    
    @property
    def code(self):
        content = '''
            <table>
                <tr>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
            </table>
        '''.format(self.datearg.code, self.timearg.code)
        return super(DatetimeArg, self).code(content)

        
    def parse(self, request):
        vals = {}
        [vals.update(dic) for dic in [var.parse(request) for var in [self.datearg, self.timearg]]]
        return vals
    
        
class SelectArg(ArgTypeMixin):
    """
    This class represents a list from which multiple values may be selected.
    """
    
    """
    Properties
    """
    max_height = '100px'
    common_head = '''
            $( function(){
                $( ".selectarg tr" ).hover( function(){$( this ).toggleClass( "ui-state-hover" )} );
                $( ".selectarg :checkbox").change( function(){$( this ).parent().parent().toggleClass( "ui-state-highlight" )} );
            });
    '''
    
    """
    Methods
    """
    
    def __init__(self, label, choices, description, default, **kwargs):
        self.choices = choices
        super(SelectArg, self).__init__(label, description, default, **kwargs)
        
        
    @property
    def code(self):
        content = '''
            <div style="height: {}; overflow: scroll; border-style: groove; resize: both;">
                <table class="selectarg ui-widget-header" style="width: 100%;">
        
        '''.format(self.max_height)
        for choice in self.choices:
            content += '''
                <tr>
                    <td><input type="checkbox" name="_extra_{}" value="{}" {}></td>
                    <td>{}</td>
                </tr>
            '''.format(
                self.label.replace(' ', '_'), 
                choice.replace(' ', '_'),
                'checked="true"' if choice in self.default else '',
                choice)
                
        content += '</table></div>'
        return super(SelectArg, self).code(content)

        
class PopupSelectArg(ArgTypeMixin):
    """
    This class represents a popup selection menu from which only one value may be selected.
    """
    
    """
    Properties
    """
    common_head = '''
            $( function(){
                $( "select" ).selectmenu();
            });
    '''
    
    """
    Methods
    """
    
    def __init__(self, label, choices, description, default, **kwargs):
        self.choices = choices
        super(PopupSelectArg, self).__init__(label, description, default, **kwargs)
        
        
    @property
    def code(self):
        content = '<select name="_extra_{}" style="width:80%;">'.format(self.label.replace(' ', '_'))
        for choice in self.choices:
            content += '''
                <option value="{}" {}>{}</option>
            '''.format(
                choice.replace(' ', '_'),
                'selected' if choice == self.default else '',
                choice)
                
        content += '</select>'
        return super(PopupSelectArg, self).code(content)
        
        
class RadioArg(ArgTypeMixin):
    """
    This class represents a list of radio buttons where only one value may be selected.
    """
    
    """
    Properties
    """
    max_height = '100px'
    common_head = '''
            $( function(){
                $( ".radioarg tr" ).hover( function(){$( this ).toggleClass( "ui-state-hover" )} );
                $( ".radioarg :checkbox").change( function(){$( this ).parent().parent().toggleClass( "ui-state-highlight" )} );
            });
    '''
    
    """
    Methods
    """
    
    def __init__(self, label, choices, description, default, **kwargs):
        self.choices = choices
        super(RadioArg, self).__init__(label, description, default, **kwargs)
        
        
    @property
    def code(self):
        content = '''
            <div style="height: {}; overflow: scroll; border-style: groove; resize: both;">
                <table class="radioarg ui-widget-header" style="width: 100%;">
        
        '''.format(self.max_height)
        for choice in self.choices:
            content += '''
                <tr>
                    <td><input type="radio" name="_extra_{}" id="_extra_{}_{}" value="{}" {}></td>
                    <td>{}</td>
                </tr>
            '''.format(
                self.label.replace(' ', '_'), 
                self.label.replace(' ', '_'),
                choice.replace(' ', '_'),
                choice.replace(' ', '_'),
                'checked="true"' if choice in self.default else '',
                choice)
                
        content += '</table></div>'
        return super(RadioArg, self).code(content)
        
        

    
    
    
    
    
    
    
        




#Copyright 2014-present lossofgenerality.com
#License: http://www.gnu.org/licenses/old-licenses/gpl-2.0.html