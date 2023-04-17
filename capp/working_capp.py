""" magic box to transform capp+ dump to usable text """
import sys


def main(input):
    for file in input:
        with open(file, 'r') as f:
            capp_dump = f.read()
            op = capp_dump.split('End ***                                        \n1\n')
            f.closed
        xmlfile = file + ".xml"
        print(xmlfile)
        with open(xmlfile, 'w+') as xmlfile:
            xmlfile.write(
                r'<?xml version="1.0" encoding="UTF-8"?>' + '\n' + r'<?xml-stylesheet type="text/xsl" href="capp.xsl"?>' + '\n' + '<cell>')
            for p in op:
                if p != "":

                    syskeyid = p[429:450].strip()
                    print(syskeyid, 'begins processing')
                    description = p[1340:1470].strip()
                    description = description.replace('&', '&amp;')
                    xmlfile.write('\n    <processStep syskeyid="' + syskeyid + '">')
                    xmlfile.write('\n        <description>')
                    xmlfile.write('\n            ' + description)
                    xmlfile.write('\n        </description>')
                    xmlfile.write(instructions(p, syskeyid))
                    xmlfile.write(consumed_items(p, syskeyid))
                    xmlfile.write(used_items(p, syskeyid))
                    xmlfile.write(visual(p, syskeyid))
                    xmlfile.write('\n' + '    </processStep>')

            xmlfile.write('\n' + '</cell>')
            xmlfile.closed


def syskey(i, syskeyid):
    s = i[429:450].strip()
    return str(s)


def one_liner(i, syskeyid):
    i = i[1340:1470].strip()
    i = i.replace('&', '&amp;')
    return i


def instructions(i, syskeyid):
    # get where description ends
    desc_start = i.find('Description:') + 134  # get where description begins (actually the line after)
    plan_start = i.find('Plans:') - 134  # get where plans begins (actually the line before)
    descript = i[desc_start:plan_start].splitlines()  # get everything between "Description:" and "Plans:"
    excel_descript = ''
    for d in descript:
        d = d.strip()  # drop whitespace
        d = d.replace('&', '&amp;')
        # d = d.lower() #make fake sentance case
        # d = d.capitalize() #make fake sentance case
        excel_descript = excel_descript + '\n            <line>' + d + '</line>'  # Build description with breaks <br> for export to excel via html
    # excel_descript = '\n        <instructions>\n            <![CDATA[' +excel_descript +']]>\n        </instructions>'
    excel_descript = '\n        <instructions>' + excel_descript + '\n        </instructions>'
    return excel_descript


def consumed_items(i, syskeyid):
    if i.find('Consumed Items:') == -1:
        consumed = ''
        print(syskeyid, 'has no Consumed Items:')
    else:
        c_start = i.find('Consumed Items:')  # +535 #find consumed to start from Then pass by all the header info.
        c_end = i.find('Used Items:')
        if c_end != -1:
            c_end = c_end - 134
        c = i[c_start:c_end]  # get everything after "Consumed Items:" but before "Used Items:" or end of file
        continued = c.find('Continued ***')
        # print (continued)
        # print ('outer')
        while continued != -1:
            c = c[:(continued - 84)] + c[(continued + 1388):]
            continued = c.find('Continued ***')
            print(syskeyid, 'consumed items is continued')
        exceptions = c.find('FRACS/SOAC Exceptions:')  # clean out exceptions
        while exceptions != -1:
            # print (c[exceptions -134:exceptions +533])
            c = c[:exceptions] + c[(exceptions + 665):]
            exceptions = c.find('FRACS/SOAC Exceptions:')
        effect = c.find('                       Effectivity')  # clean out effectivities
        # print (effect)
        while effect != -1:
            # print (c[effect -134:effect +533])
            c = c[:(effect - 134)] + c[(effect + 533):]
            effect = c.find('                       Effectivity')
            print(syskeyid, ' has multiple effectivities in consumed')
        # print (c)
        c = c.splitlines()
        consumed = ''
        note = 0
        # print (c)
        for con in c:
            # print (con[0:40])
            if con[17] == '-':
                if con[16] == '-':
                    dash = 1  # basically skip this line
                else:
                    params = {  # use a dictionary
                        'Trn': con[1:3].strip(),
                        'Line': con[6:9].strip(),
                        'Item': con[11:22].strip(),
                        'Item_Name': con[23:38].strip(),
                        'Qty': con[41:46].strip(),
                        'UM': con[47:50].strip(),
                        'SL_Ind': con[52:54].strip(),
                        'Inv_Ctl': con[56:58].strip(),
                        'Time_Acquir': con[61:66].strip(),
                        'Time_Offset': con[68:73].strip(),
                        'Usg': con[76:79].strip(),
                        'Ctr_Cde': con[80:82].strip(),
                        'Location_Bldg': con[85:90].strip(),
                        'Location_Bin': con[92:100].strip(),
                        'SA_Ind': con[129:131].strip()
                    }
                    # make sure item name doesn't contain "&"
                    params["Item_Name"] = params["Item_Name"].replace('&', '&amp;')
                    # if con[112:119] != 'assumed':
                    # params['Next_Level'] = con[102:109].strip()
                    # params['Attach'] = con[111:118].strip()
                    # params['Top_Level'] = con[120:127].strip()
                    #
                    # not sure exactly how/what these fields do so have chosen not to extract
                    #
                    consumed = consumed + '\n            <component>'
                    for k, v in params.items():
                        consumed = consumed + '\n                <' + k + '>' + v + '</' + k + '>'
                    consumed = consumed + '\n            </component>'
                    note_count = 0
                    note = 1  # allows to check if next line is a note not a consumed item
            elif con[18] == '-':
                if con[16] == '-':
                    dash = 1  # basically skip this line
                else:
                    params = {  # use a dictionary
                        'Trn': con[2:4].strip(),
                        'Line': con[7:10].strip(),
                        'Item': con[12:23].strip(),
                        'Item_Name': con[24:39].strip(),
                        'Qty': con[42:47].strip(),
                        'UM': con[48:51].strip(),
                        'SL_Ind': con[53:55].strip(),
                        'Inv_Ctl': con[57:59].strip(),
                        'Time_Acquir': con[62:67].strip(),
                        'Time_Offset': con[69:74].strip(),
                        'Usg': con[77:80].strip(),
                        'Ctr_Cde': con[81:83].strip(),
                        'Location_Bldg': con[86:91].strip(),
                        'Location_Bin': con[93:101].strip(),
                        'SA_Ind': con[130:132].strip()
                    }
                    # make sure item name doesn't contain "&"
                    params["Item_Name"] = params["Item_Name"].replace('&', '&amp;')
                    # if con[112:119] != 'assumed':
                    # params['Next_Level'] = con[102:109].strip()
                    # params['Attach'] = con[111:118].strip()
                    # params['Top_Level'] = con[120:127].strip()
                    #
                    # not sure exactly how/what these fields do so have chosen not to extract
                    #
                    consumed = consumed + '\n            <component>'
                    for k, v in params.items():
                        consumed = consumed + '\n                <' + k + '>' + v + '</' + k + '>'
                    consumed = consumed + '\n            </component>'
                    note_count = 0
                    note = 1  # allows to check if next line is a note not a consumed item
            elif note == 1:
                # note = 0
                if con[21] != " ":
                    note_count = note_count + 1
                    con = con.replace('"', 'INCH')  # xml problems if there is a " in this string possibly others?
                    con = con.replace('&', '&amp;')
                    consumed = consumed[:-25] + '\n                <note>' + con.strip() + '</note>' + consumed[
                                                                                                       -25:]  # squeeze the note in before the previous "/>"
                    # print (consumed)
            else:
                note = 0
                note_count = 0
                # print ('not partnumber or note')
    consumed = '\n        <consumed>' + consumed + '\n        </consumed>'
    return consumed


def used_items(i, syskeyid):
    if i.find('Used Items:') == -1:
        used = '\n        <used>'
        print(syskeyid, 'has no used items')
    else:
        # cleanup input
        # get rid of used items header
        used = '\n        <used>'
        u_start = i.find('Used Items:')  # find used to start from input complete process
        u = i[u_start:]  # truncate to only used items to end of process
        u_start = u.find('Used Items:')  # find used to start from from truncated
        while u_start != -1:
            u = u[:(u_start)] + u[(u_start + 531):]
            u_start = u.find('Used Items:')
        # get rid of continued
        continued = u.find('Continued ***')
        while continued != -1:
            u_end = u.find('(Continued)')
            if u_end != -1:
                u_end = u_end + 131
                u = u[:(continued - 84)] + u[(u_end):]
            else:
                u = u[:(continued - 84)] + u[(continued + 586):]
            continued = u.find('Continued ***')
            print(syskeyid, ' used items is continued')
        # get rid of effectivity blocks
        effect = u.find('                       Effectivity')
        while effect != -1:
            u = u[:(effect - 134)] + u[(effect + 533):]
            effect = u.find('                       Effectivity')
            print(syskeyid, ' has multiple effectivities in used')
            dbltest = u.find('Consumed Items:')
            if dbltest != -1:
                used = consumed_items(u[dbltest:], syskeyid) + used
                print(syskeyid, 'MULTIPLE SETS OF CONSUMED ITEMS DUE TO MULTIPLE EFFECTIVITIES')
                # print (u[dbltest:])
        # print (u)
        u = u.splitlines()
        note = 0
        for use in u:
            # print ('-' +use +'-')
            if use.strip() == '' or use[12] == '-':
                skip = 1
            else:
                if use[12] != ' ':
                    # print (use)
                    params = {  # use a dictionary
                        'Trn': use[1:3].strip(),
                        'Item': use[11:21].strip(),
                        'Item_Name': use[28:43].strip(),
                        'Item_type': use[46:50].strip(),
                        'Qty_opt': use[52:61].strip(),
                        'UM': use[64:67].strip(),
                        'Cnsm_Pct': use[70:73].strip(),
                        'Inv_Ctl': use[78:80].strip(),
                        'Time_Acquir': use[84:90].strip(),
                        'Time_Offset': use[92:97].strip()
                    }
                    used = used + '\n            <component>'
                    for k, v in params.items():
                        used = used + '\n                <' + k + '>' + v + '</' + k + '>'
                    used = used + '\n            </component>'
                else:
                    skip = 1
    used = used + '\n        </used>'
    return used


def visual(i,
           syskeyid):  # the first part is copied and pasted from consumed materials then will find the lines that "start" with PVA
    if i.find('Consumed Items:') == -1:
        visual = ''
        print(syskeyid, 'has no Visuals')
    else:
        c_start = i.find('Consumed Items:') + 535  # find consumed to start from Then pass by all the header info.
        c_end = i.find('Used Items:')
        if c_end != -1:
            c_end = c_end - 134
        c = i[c_start:c_end]  # get everything after "Consumed Items:" but before "Used Items:" or end of file
        continued = c.find('Continued ***')
        # print (continued)
        # print ('outer')
        while continued != -1:
            c = c[:(continued - 84)] + c[(continued + 1388):]
            continued = c.find('Continued ***')
            print(syskeyid, 'consumed items is continued')
        exceptions = c.find('FRACS/SOAC Exceptions:')  # clean out exceptions
        while exceptions != -1:
            # print (c[exceptions -134:exceptions +533])
            c = c[:exceptions] + c[(exceptions + 665):]
            exceptions = c.find('FRACS/SOAC Exceptions:')
        effect = c.find('                       Effectivity')  # clean out effectivities
        # print (effect)
        while effect != -1:
            # print (c[effect -134:effect +533])
            c = c[:(effect - 134)] + c[(effect + 533):]
            effect = c.find('                       Effectivity')
            print(syskeyid, ' has multiple effectivities in consumed')
        # print (c)
        c = c.splitlines()
        visual = ''
        note = 0
        # print (c)
        for pva in c:
            pva = pva.strip()
            if pva[0:3] == 'PVA':
                visual = visual + '\n        <visual>' + pva[3:].strip() + '</visual>'
    return visual


if __name__ == "__main__":
    input = sys.argv[1:]
    print('Using file', input)
    main(input)