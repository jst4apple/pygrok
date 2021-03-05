try:
    import regex as re
except ImportError as e:
    # If you import re, grok_match can't handle regular expression containing atomic group(?>)
    import re
import codecs
import os
import pkg_resources
from functools import partial
DEFAULT_PATTERNS_DIRS = [pkg_resources.resource_filename(__name__, 'patterns')]


class Grok(object):
    
    def __init__(self, pattern, custom_patterns_dir=None, custom_patterns={}, fullmatch=True):
        self.pattern = pattern
        self.custom_patterns_dir = custom_patterns_dir
        self.predefined_patterns = _reload_patterns(DEFAULT_PATTERNS_DIRS)
        self.fullmatch = fullmatch

        custom_pats = {}
        if custom_patterns_dir is not None:
            custom_pats = _reload_patterns([custom_patterns_dir])

        for pat_name, regex_str in custom_patterns.items():
            custom_pats[pat_name] = Pattern(pat_name, regex_str)

        if len(custom_pats) > 0:
            self.predefined_patterns.update(custom_pats)
        
        #self._load_search_pattern()
    
    @staticmethod
    def _match(pattern, all_pattern, text, namespace, fullmatch):
        type_mapper = {}
        py_regex_pattern = Pattern.compile(pattern, all_pattern, namespace, type_mapper, False)
        #print(py_regex_pattern)
        regex_obj = re.compile(py_regex_pattern)
        
        match_obj = None
        if fullmatch:
            match_obj = regex_obj.fullmatch(text)
        else:
            match_obj = regex_obj.search(text)
    
        if match_obj == None:
            return None, None, None
            
        matches = match_obj.groupdict()
        output = {}
        for key, match in matches.items():
            itype, otype = type_mapper[key]
            output[key] = match
            try:
                if  otype == 'int':
                    output[key] = int(match)
              
                if otype == 'float':
                    output[key] = float(match)
            except (TypeError, KeyError) as e:
                pass
            
            if otype == 'arr':
                output[key] = {"_str": match}
                
                i = 0 
                _pattern = all_pattern[itype].regex_str
                _text = match
                _output, _end, _str = Grok._match(_pattern, all_pattern, _text, "", fullmatch)
                while _end and _text:
                    output[key][i] = _output
                    output[key][i].update({"__str":_str})
                    _text = _text[_end:]
                    _output, _end, _str = Grok._match(_pattern, all_pattern, _text, "", fullmatch)
                    if not _end:
                        output[key].update({"__len": i + 1})
                        break
                    i += 1
                       
            if key not in output:
                output[key] = match
                          
        return output, match_obj.end(), match_obj.group(0)
        
    def match(self, text):
        """If text is matched with pattern, return variable names specified(%{pattern:variable name})
        in pattern and their corresponding values.If not matched, return None.
        custom patterns can be passed in by custom_patterns(pattern name, pattern regular expression pair)
        or custom_patterns_dir.
        """
        output, _ , _ = self._match(self.pattern, self.predefined_patterns, text, "", self.fullmatch)
        return output
      

    def set_search_pattern(self, pattern=None):
        if type(pattern) is not str :
            raise ValueError("Please supply a valid pattern")    
        self.pattern = pattern
        #self._load_search_pattern()

    def _load_search_pattern(self):
        self.type_mapper = {}
        py_regex_pattern = Pattern.compile(self.pattern, self.predefined_patterns, "", self.type_mapper, False)
        self.regex_obj = re.compile(py_regex_pattern)

def _wrap_pattern_name(pat_name):
    return '%{' + pat_name + '}'

def _reload_patterns(patterns_dirs):
    """
    """
    all_patterns = {}
    for dir in patterns_dirs:
        if not os.path.exists(dir):
            print("_reload_patterns:warning file not exist", dir)
            continue
        for f in os.listdir(dir):
            patterns = _load_patterns_from_file(os.path.join(dir, f))
            all_patterns.update(patterns)

    return all_patterns


def _load_patterns_from_file(file):
    """
    """
    patterns = {}
    with codecs.open(file, 'r', encoding='utf-8') as f:
        for l in f:
            l = l.strip()
            if l == '' or l.startswith('#'):
                continue

            sep = l.find(' ')
            pat_name = l[:sep]
            regex_str = l[sep:].strip()
            pat = Pattern(pat_name, regex_str)
            patterns[pat.pattern_name] = pat
    return patterns


class Pattern(object):
    """
    """
    #ARR_RE = re.compile("^ARR\((?P<item>.*?)(,\s*(?P<index>(.*)))*\)$")

    def __init__(self, pattern_name, regex_str, sub_patterns = {}):
        self.pattern_name = pattern_name
        self.regex_str = regex_str
        self.sub_patterns = sub_patterns # sub_pattern name list
        #self.is_arr = False
        
        #arr = ARR_RE.match(regex_str)
        #if arr:
        #    self.is_arr = True
        #    self.regex_str  = "(?:%{" + arr["item"].strip() + "})+"
        #    if not arr["index"]:
        #        self.index    = lambda loopidx, citem: loopidx
        #    else:
        #        self.index    = eval("lambda loopidx, citem : " + arr["index"])
        
    def __str__(self):
        return '<Pattern:%s,  %s,  %s>' % (self.pattern_name, self.regex_str, self.sub_patterns)
    

    
    @staticmethod
    def compile(express, all_pattern, namespace, type_mapper, is_anonymous = False):
        def _reg_var(_n, tin, tout):
            n = namespace and "_".join([namespace, _n]) or _n
            type_mapper[n] = (tin, tout)
            return n
        
        _unnamed_replace =  lambda m: "".join(["(?:",   Pattern.compile(all_pattern[m.group(1)].regex_str, all_pattern, namespace, type_mapper, True),")"]) 
        _named_replace   =  lambda m, n: "".join(["(?P<", n, ">",  "(?:", Pattern.compile(all_pattern[m.group(1)].regex_str, all_pattern, n, type_mapper, False) ,")" , ")"])
        _array_replace   =  lambda m, n: "".join(["(?P<", n, ">", "(?:", _unnamed_replace(m), "+)", ")"])

        if is_anonymous:
            py_regex_pattern = re.sub(r'%{(\w+)(?::\w+)?}',
                _unnamed_replace,
                express)
        else:
            py_regex_pattern = re.sub(r'%{(\w+):(\w+):arr}',
                lambda m : _array_replace(m, _reg_var(m.group(2), m.group(1),  "arr")),
                express)
                
            py_regex_pattern = re.sub(r'%{(\w+):(\w+):(\w+)}',
                    lambda m : _named_replace(m, _reg_var(m.group(2), m.group(1), m.group(3))),
                    py_regex_pattern)

            py_regex_pattern = re.sub(r'%{(\w+):(\w+)}',
                    lambda m : _named_replace(m, _reg_var(m.group(2), m.group(1), None)),
                    py_regex_pattern)
                
            py_regex_pattern = re.sub(r'%{(\w+)}',
                    _unnamed_replace,
                    py_regex_pattern)
                
        return  py_regex_pattern