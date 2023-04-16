import subprocess
import sys
from collections import Counter

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


def main(input):
    for file in input:
        with open(file, 'r') as f:
            capp_dump = f.read()
            op = capp_dump.split('End ***')
            f.closed
        xmlfile = file + "_new.xml"
        with open(xmlfile, 'w+') as xmlfile:
            xmlfile.write(
                r'<?xml version="1.0" encoding="UTF-8"?>' + '\n' + r'<?xml-stylesheet type="text/xsl" href="capp.xsl"?>' + '\n' + '<cell>')
            counter = 0
            line = []
            for p in op:
                try:
                    if p != "":
                        # syskeyid
                        operation_number_index = p.find('Operation Number:')
                        report_date_index = p.find('Report Date:')
                        temp = p[operation_number_index:report_date_index]
                        temp = temp.split(' ')
                        while "" in temp:
                            temp.remove("")
                        syskeyid = temp[-1]
                        # print(syskeyid)

                        # description
                        description_number_index = p.find('Description')
                        plans_number_index = p.find('Plans')
                        temp = p[description_number_index:plans_number_index]
                        temp = temp.replace('\n', '')
                        temp = (' '.join(temp.split()))
                        description = temp.split('Description:')[-1].strip()
                        # print(description)

                        xmlfile.write('\n    <processStep syskeyid="' + syskeyid + '">')
                        xmlfile.write('\n        <description>')
                        xmlfile.write('\n            ' + description)
                        xmlfile.write('\n        </description>')

                        # special remarks: old instructions
                        sr_number_index = p.find('Special Remarks:')
                        description_index = p.find('Description:')
                        temp = p[sr_number_index:description_index]
                        temp = temp.replace('\n', '')
                        temp = (' '.join(temp.split()))
                        sr = temp.split('Special Remarks:')[-1].strip()
                        # print(sr)
                        xmlfile.write('\n' + '    <instructions>')
                        xmlfile.write('\n        <line>' + sr + '        </line>')
                        xmlfile.write('\n' + '    </instructions>')

                        # consumed items
                        consumed_items_index = p.find('Consumed Items:')
                        temp = p[consumed_items_index: len(p) - 1]
                        temp = temp.split('Consumed Items:')[1].strip().split('\n')
                        xmlfile.write('\n        <consumed>')
                        for item in temp:
                            data = item.strip()
                            if len(data) == 73:
                                print(data)
                                print(data.find('  REF'))
                                xmlfile.write('\n           <component>')
                                xmlfile.write(f"\n              <Trn></Trn>")
                                xmlfile.write(f"\n              <Line>{data[0:4]}</Line>")
                                xmlfile.write(f"\n              <Item>{data[8:16]}</Item>")
                                xmlfile.write(f"\n              <Item_Name>{data[17:30]}</Item_Name>")
                                xmlfile.write(f"\n              <Qty>{data[39:41].strip()}</Qty>")
                                xmlfile.write(f"\n              <UM>{data[42:45].strip()}</UM>")
                                xmlfile.write(f"\n              <SL_Ind>{data[47:50].strip()}</SL_Ind>")
                                xmlfile.write(f"\n              <Inv_Ctl>{data[51:53].strip()}</Inv_Ctl>")
                                xmlfile.write(f"\n              <Time_Acquir>{data[58:61].strip()}</Time_Acquir>")
                                xmlfile.write(f"\n              <Time_Offset></Time_Offset>")
                                xmlfile.write(f"\n              <Usg>{data[70:74].strip()}</Usg>")
                                xmlfile.write(f"\n              <Ctr_Cde></Ctr_Cde>")
                                xmlfile.write(f"\n              <Location_Bldg></Location_Bldg>")
                                xmlfile.write(f"\n              <Location_Bin></Location_Bin>")
                                xmlfile.write(f"\n              <SA_Ind></SA_Ind>")
                                xmlfile.write('\n           </component>')
                        xmlfile.write('\n        </consumed>')


                        xmlfile.write('\n' + '    </processStep>')
                        if counter == 0:
                            break
                        counter += 1
                except Exception as e:
                    print('ok')

            xmlfile.write('\n' + '</cell>')
            xmlfile.closed
            a = dict(Counter(line))
            print(a)



if __name__ == "__main__":
    input = sys.argv[1:]
    print('Using file', input)
    main(input)
