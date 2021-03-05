from pygrok import Grok


def test_one_pat():
    text = '1024'
    pat = '%{INT:test_int}'
    grok = Grok(pat)
    m = grok.match(text)
    assert m['test_int'] == '1024', 'grok match failed:%s, %s' % (text, pat, )

    text = '1024'
    pat = '%{NUMBER:test_num}'
    grok = Grok(pat)
    m = grok.match(text)
    assert m['test_num'] == '1024', 'grok match failed:%s, %s' % (text, pat, )

    text = 'garyelephant '
    pat = '%{WORD:name} '
    grok = Grok(pat)
    m = grok.match(text)
    assert m['name'] == text.strip(), 'grok match failed:%s, %s' % (text, pat, )

    text = '192.168.1.1'
    pat = '%{IP:ip}'
    grok = Grok(pat)
    m = grok.match(text)
    assert m['ip'] == text.strip(), 'grok match failed:%s, %s' % (text, pat, )

    text = 'github.com'
    pat = '%{HOSTNAME:website}'
    grok = Grok(pat)
    m = grok.match(text)
    assert m['website'] == text.strip(), 'grok match failed:%s, %s' % (text, pat, )

    text = '1989-11-04 05:33:02+0800'
    pat = '%{TIMESTAMP_ISO8601:ts}'
    grok = Grok(pat)
    m = grok.match(text)
    assert m['ts'] == text.strip(), 'grok match failed:%s, %s' % (text, pat, )

    text = 'github'
    pat = '%{WORD}'
    grok = Grok(pat)
    m = grok.match(text)
    assert m == {}, 'grok match failed:%s, %s' % (text, pat, )
    # you get nothing because variable name is not set, compare "%{WORD}" and "%{WORD:variable_name}"

    text = 'github'
    pat = '%{NUMBER:test_num}'
    grok = Grok(pat)
    m = grok.match(text)
    assert m is None, 'grok match failed:%s, %s' % (text, pat, )
    #not match

    text = '1989'
    pat = '%{NUMBER:birthyear:int}'
    grok = Grok(pat)
    m = grok.match(text)
    assert m == {'birthyear': 1989}, 'grok match failed:%s, %s' % (text, pat, )


def test_multiple_pats():
    text = 'gary 25 "never quit"'
    pat = '%{WORD:name} %{INT:age} %{QUOTEDSTRING:motto}'
    grok = Grok(pat)
    m = grok.match(text)
    assert m['name'] == 'gary' and m['age'] == '25' and m['motto'] == '"never quit"', \
        'grok match failed:%s, %s' % (text, pat, )

    # variable names are not set
    text = 'gary 25 "never quit"'
    pat = '%{WORD} %{INT} %{QUOTEDSTRING}'
    grok = Grok(pat)
    m = grok.match(text)
    assert m == {}, 'grok match failed:%s, %s' % (text, pat, )

    #"male" is not INT
    text = 'gary male "never quit"'
    pat = '%{WORD:name} %{INT:age} %{QUOTEDSTRING:motto}'
    grok = Grok(pat)
    m = grok.match(text)
    assert m is None, 'grok match failed:%s, %s' % (text, pat, )

    # nginx log
    text = 'edge.v.iask.com.edge.sinastorage.com 14.18.243.65 6.032s - [21/Jul/2014:16:00:02 +0800]' \
        + ' "GET /edge.v.iask.com/125880034.hlv HTTP/1.0" 200 70528990 "-"' \
        + ' "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)' \
        + ' Chrome/36.0.1985.125 Safari/537.36"'
    pat = '%{HOSTNAME:host} %{IP:client_ip} %{NUMBER:delay}s - \[%{DATA:time_stamp}\]' \
        + ' "%{WORD:verb} %{URIPATHPARAM:uri_path} HTTP/%{NUMBER:http_ver}" %{INT:http_status} %{INT:bytes} %{QS}' \
        + ' %{QS:client}'
    grok = Grok(pat)
    m = grok.match(text)
    assert m['host'] == 'edge.v.iask.com.edge.sinastorage.com' and m['client_ip'] == '14.18.243.65' \
        and m['delay'] == '6.032' and m['time_stamp'] == '21/Jul/2014:16:00:02 +0800' and m['verb'] == 'GET' \
        and m['uri_path'] == '/edge.v.iask.com/125880034.hlv' and m['http_ver'] == '1.0' \
        and m['http_status'] == '200' and m['bytes'] == '70528990' \
        and m['client'] == '"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)' \
        + ' Chrome/36.0.1985.125 Safari/537.36"', 'grok match failed:%s, %s' % (text, pat, )

    text = '1989/02/23'
    pat = '%{NUMBER:birthyear:int}/%{NUMBER:birthmonth:int}/%{NUMBER:birthday:int}'
    grok = Grok(pat)
    m = grok.match(text)
    assert m == {'birthyear': 1989, 'birthmonth': 2, 'birthday': 23}, 'grok match failed:%s, %s' % (text, pat, )

    text = 'load average: 1.88, 1.73, 1.49'
    pat = 'load average: %{NUMBER:load_1:float}, %{NUMBER:load_2:float}, %{NUMBER:load_3:float}'
    grok = Grok(pat)
    m = grok.match(text)
    assert m == {'load_1': 1.88, 'load_2': 1.73, 'load_3': 1.49}, 'grok match failed:%s, %s' % (text, pat, )


def test_custom_pats():
    custom_pats = {'ID': '%{WORD}-%{INT}'}
    text = 'Beijing-1104,gary 25 "never quit"'
    pat = '%{ID:user_id},%{WORD:name} %{INT:age} %{QUOTEDSTRING:motto}'
    grok = Grok(pat, custom_patterns=custom_pats)
    m = grok.match(text)
    assert m['user_id'] == 'Beijing-1104' and m['name'] == 'gary' and m['age'] == '25' \
        and m['motto'] == '"never quit"', 'grok match failed:%s, %s' % (text, pat, )


def test_custom_pat_files():
    import os.path
    pats_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_patterns')
    text = 'Beijing-1104,gary 25 "never quit"'
    # pattern "ID" is defined in ./test_patterns/pats
    pat = '%{ID:user_id},%{WORD:name} %{INT:age} %{QUOTEDSTRING:motto}'
    grok = Grok(pat, custom_patterns_dir=pats_dir)
    m = grok.match(text)
    assert m['user_id'] == 'Beijing-1104' and m['name'] == 'gary' and m['age'] == '25' \
        and m['motto'] == '"never quit"', 'grok match failed:%s, %s' % (text, pat, )


def test_hotloading_pats():
    text = 'github'
    pat = '%{WORD:test_word}'
    grok = Grok(pat)
    m = grok.match(text)
    assert m['test_word'] == 'github', 'grok match failed:%s, %s' % (text, pat, )
    # matches

    text = '1989'
    pat = '%{NUMBER:birthyear:int}'
    grok.set_search_pattern(pat)
    m = grok.match(text)
    assert m == {'birthyear': 1989}, 'grok match failed:%s, %s' % (text, pat, )

def test_arr_pats():
    custom_pats = {"POWER": "(?:%{NUMBER}|(-inf))", "HEX":"(?:(0[x,X])*(?:[0-9a-zA-Z]+))", "HEXENUM":"%{HEX:v}[ ]?", "HEXLINE":"%{HEXENUM:col:arr}\n?" }
    
    text = '0x1 0x2 0x3'
    pat = '%{HEXLINE:row}'
    grok = Grok(pat ,custom_patterns = custom_pats, fullmatch = False)
    m = grok.match(text)
    assert      (m['row'] == '0x1 0x2 0x3'
            and m['row_col']['_str'] == '0x1 0x2 0x3'
            and m['row_col'][0]["v"] == '0x1'
            and m['row_col'][1]["v"] == '0x2'
            and m['row_col'][2]["v"] == '0x3'
                 ), 'grok match failed:%s, %s' % (text, pat, )
    # matches

    text = '0x1 0x2 0x3\n0x4 0x5 0x6\n0x7 0x8 0x9'
    pat = '%{HEXLINE:row:arr}'
    grok.set_search_pattern(pat)
    m = grok.match(text)
    for i in range(2):
        for j in range(3):
            assert m['row'][i]['col'][j]['v'] == "0x"+ "%d"%(i*3 + j + 1), 'grok match failed:%s, %s' % (text, pat, )


def test_struct_pats():
    import json
    custom_pats = {"POWER": "(?:%{NUMBER}|(-inf))", "HEX": "(?:(0[x,X])*(?:[0-9a-zA-Z]+))", "HEXENUM": "%{HEX:v}[ ]?",
                   "HEXLINE": "%{HEXENUM:col:arr}\n?"}

    text = json.dumps({"a": {"c": {"d": 4}, "e": [1, 2, 3]}})
    custom_pats.update({"EA":"%{NUMBER:v:int}(,\s*)*"})
    custom_pats.update({"E":"(.*): \[%{EA:e:arr}\]"})
    grok = Grok("(.*): \[%{EA:e:arr}\]", custom_patterns = custom_pats, fullmatch = False)
    m = grok.match(text)
    assert m['e'][0]['v'] == 1, print(m['e'][0]['v'])
    assert m['e'][1]['v'] == 2, print(m['e'][1]['v'])
    assert m['e'][2]['v'] == 3, print(m['e'][2]['v'])

    custom_pats.update({"C":"{%{QS}: {%{QS}: %{NUMBER:d:int}}"})
    grok = Grok("%{C:c}", custom_patterns=custom_pats, fullmatch=False)
    m = grok.match(text)
    assert m['c_d'] == 4, print(m['c_d'])

    custom_pats.update({"A":"{(.*): %{C:c}, (.*): \[%{EA:e:arr}\]}"})

    grok = Grok("%{A:a}", custom_patterns = custom_pats, fullmatch = False)


    m = grok.match(text)
    assert m['a_c_d'] == 4, print(m['a_c_d'])
    assert m['a_e'][0]['v'] == 1, print(m['a_c_e'][0]['v'])
    assert m['a_e'][1]['v'] == 2, print(m['a_c_e'][1]['v'])
    assert m['a_e'][2]['v'] == 3, print(m['a_c_e'][2]['v'])
def test_arr_struct_pats():
    
    custom_pats = {"POWER": "(?:%{NUMBER}|(-inf))", "HEX":"(?:(0[x,X])*(?:[0-9a-zA-Z]+))", "HEXENUM":"%{HEX:v}[ ]?", "HEXLINE":"%{HEXENUM:col:arr}\n?" }
    
    text = """
Branch A
	  txPma                            : -inf,
	  txDpdPma                         : -inf,
	  txPmb                            : -inf,
	  txTorPmb                         : -inf,
	  rfPower                          : -inf[dBm],
	  avgIMpa0                         : 10[mAmp],
	  pmErrCounterTotal                : 1
	  pmErrCounterLast                 : 1
	  pmDpdIrqStat                     : 0x00000000

Branch B
	  txPma                            : -inf,
	  txDpdPma                         : -inf,
	  txPmb                            : -inf,
	  txTorPmb                         : -inf,
	  rfPower                          : -inf[dBm],
	  avgIMpa0                         : 10[mAmp],
	  pmErrCounterTotal                : 1
	  pmErrCounterLast                 : 1
	  pmDpdIrqStat                     : 0x00000000

Branch C
	  txPma                            : -inf,
	  txDpdPma                         : -inf,
	  txPmb                            : -inf,
	  txTorPmb                         : -0.00,
	  rfPower                          : 54.50[dBm],
	  avgIMpa0                         : 0[mAmp],
	  pmErrCounterTotal                : 0
	  pmErrCounterLast                 : 0
	  pmDpdIrqStat                     : 0x00000000

Branch D
	  txPma                            : -inf,
	  txDpdPma                         : -inf,
	  txPmb                            : -inf,
	  txTorPmb                         : -0.00,
	  rfPower                          : 51.50[dBm],
	  avgIMpa0                         : 0[mAmp],
	  pmErrCounterTotal                : 0
	  pmErrCounterLast                 : 0
	  pmDpdIrqStat                     : 0x00000000

Branch E
	  txPma                            : -inf,
	  txDpdPma                         : -inf,
	  txPmb                            : -inf,
	  txTorPmb                         : -inf,
	  rfPower                          : -inf[dBm],
	  avgIMpa0                         : 40[mAmp],
	  pmErrCounterTotal                : 1
	  pmErrCounterLast                 : 1
	  pmDpdIrqStat                     : 0x00000000

Branch F
	  txPma                            : -inf,
	  txDpdPma                         : -inf,
	  txPmb                            : -inf,
	  txTorPmb                         : -inf,
	  rfPower                          : -inf[dBm],
	  avgIMpa0                         : 0[mAmp],
	  pmErrCounterTotal                : 1
	  pmErrCounterLast                 : 1
	  pmDpdIrqStat                     : 0x00000000

Branch G
	  txPma                            : -inf,
	  txDpdPma                         : -inf,
	  txPmb                            : -inf,
	  txTorPmb                         : -40.58,
	  rfPower                          : 10.92[dBm],
	  avgIMpa0                         : 0[mAmp],
	  pmErrCounterTotal                : 0
	  pmErrCounterLast                 : 0
	  pmDpdIrqStat                     : 0x00000000

Branch H
	  txPma                            : -inf,
	  txDpdPma                         : -inf,
	  txPmb                            : -inf,
	  txTorPmb                         : -40.58,
	  rfPower                          : 13.92[dBm],
	  avgIMpa0                         : 0[mAmp],
	  pmErrCounterTotal                : 0
	  pmErrCounterLast                 : 0
	  pmDpdIrqStat                     : 0x00000000

Branch I
	  txPma                            : -inf,
	  txDpdPma                         : -inf,
	  txPmb                            : -inf,
	  txTorPmb                         : -inf,
	  rfPower                          : -inf[dBm],
	  avgIMpa0                         : 0[mAmp],
	  pmErrCounterTotal                : 1
	  pmErrCounterLast                 : 1
	  pmDpdIrqStat                     : 0x00000000

Branch J
	  txPma                            : -inf,
	  txDpdPma                         : -inf,
	  txPmb                            : -inf,
	  txTorPmb                         : -inf,
	  rfPower                          : -inf[dBm],
	  avgIMpa0                         : 0[mAmp],
	  pmErrCounterTotal                : 1
	  pmErrCounterLast                 : 1
	  pmDpdIrqStat                     : 0x00000000

Branch K
	  txPma                            : -inf,
	  txDpdPma                         : -inf,
	  txPmb                            : -inf,
	  txTorPmb                         : -1.33,
	  rfPower                          : 50.17[dBm],
	  avgIMpa0                         : 0[mAmp],
	  pmErrCounterTotal                : 0
	  pmErrCounterLast                 : 0
	  pmDpdIrqStat                     : 0x00000000

Branch L
	  txPma                            : -inf,
	  txDpdPma                         : -inf,
	  txPmb                            : -inf,
	  txTorPmb                         : -1.33,
	  rfPower                          : 53.17[dBm],
	  avgIMpa0                         : 0[mAmp],
	  pmErrCounterTotal                : 0
	  pmErrCounterLast                 : 0
	  pmDpdIrqStat                     : 0x00000000
"""
    custom_pats.update({"BRANCH": """
Branch %{WORD:brachid}
	  txPma                            : %{POWER:txPma},
	  txDpdPma                         : %{POWER:txDpdPma},
	  txPmb                            : %{POWER:txPmb},
	  txTorPmb                         : %{POWER:txTorPmb},
	  rfPower                          : %{POWER:rfPower}\[dBm\],
	  avgIMpa0                         : %{POWER:avgIMpa0}\[mAmp\],
	  pmErrCounterTotal                : %{POWER:pmErrCounterTotal}
	  pmErrCounterLast                 : %{POWER:pmErrCounterLast}
	  pmDpdIrqStat                     : %{HEX:pmDpdIrqStat}
"""})
    grok = Grok("%{BRANCH:branch:arr}\n", custom_patterns = custom_pats, fullmatch = False)
    m = grok.match(text)
    for i in range(10):
        assert (m['branch'][i]["brachid"] == chr(65 + i)), 'grok match failed:%s, %s' % (text, pat, )
    # matches

if __name__ == '__main__':

    #test_one_pat()
    #test_multiple_pats()
    #test_custom_pats()
    #test_custom_pat_files()
    #test_hotloading_pats()
    test_arr_pats()
