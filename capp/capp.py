import sys


def main(input):
    for file in input:
        with open(file, 'r') as f:
            capp_dump = f.read()
            op = capp_dump.split('End ***')
            f.closed
        xmlfile = file + ".xml"
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

                        # description
                        description_number_index = p.find('Description')
                        plans_number_index = p.find('Plans')
                        temp = p[description_number_index:plans_number_index]
                        temp = temp.replace('\n', '')
                        temp = (' '.join(temp.split()))
                        description = temp.split('Description:')[-1].strip().replace('&', '&amp;')
                        xmlfile.write('\n    <processStep syskeyid="' + syskeyid + '">')
                        xmlfile.write('\n       <description>')
                        xmlfile.write('\n           ' + description)
                        xmlfile.write('\n       </description>')

                        # special remarks: old instructions
                        sr_number_index = p.find('Special Remarks:')
                        description_index = p.find('Description:')
                        temp = p[sr_number_index:description_index]
                        temp = temp.replace('\n', '')
                        temp = (' '.join(temp.split()))
                        sr = temp.split('Special Remarks:')[-1].strip().replace('&', '&amp;')
                        xmlfile.write('\n' + '       <instructions>')
                        xmlfile.write('\n           <line>' + sr + '</line>')
                        xmlfile.write('\n' + '       </instructions>')

                        # consumed items
                        consumed_items_index = p.find('Consumed Items:')
                        used_item_index = p.find('Used Items:')
                        if used_item_index == -1:
                            temp = p[consumed_items_index: len(p) - 1]
                        else:
                            temp = p[consumed_items_index: used_item_index]
                        temp = temp.split('Consumed Items:')[1].strip().split('\n')
                        for ind, item in enumerate(temp):

                            item = item.replace("<--  assumed  -->", "")
                            item = item.strip()
                            if item == "" or " PC " not in item:
                                continue

                            if len(item) == 70:
                                item = "   " + item
                            if len(item) == 71:
                                item = "  " + item
                            if len(item) == 72:
                                item = " " + item
                            if len(item) == 92:
                                item = "  " + item
                            if len(item) == 91:
                                item = "   " + item
                            if len(item) == 93:
                                item = " " + item

                            line.append(len(item))
                            counter += 1

                            if len(item) == 73:
                                xmlfile.write('\n       <consumed>')
                                xmlfile.write('\n           <component>')
                                xmlfile.write(f"\n               <Trn></Trn>")
                                xmlfile.write(f"\n               <Line>{item[0:4].strip().replace('&', '&amp;')}</Line>")
                                xmlfile.write(f"\n               <Item>{item[8:16].strip().replace('&', '&amp;')}</Item>")
                                xmlfile.write(f"\n               <Item_Name>{item[17:38].strip().replace('&', '&amp;')}</Item_Name>")
                                xmlfile.write(f"\n               <Qty>{item[39:41].strip().replace('&', '&amp;')}</Qty>")
                                xmlfile.write(f"\n               <UM>{item[42:45].strip().replace('&', '&amp;')}</UM>")
                                xmlfile.write(f"\n               <SL_Ind>{item[47:50].strip().replace('&', '&amp;')}</SL_Ind>")
                                xmlfile.write(f"\n               <Inv_Ctl>{item[51:53].strip().replace('&', '&amp;')}</Inv_Ctl>")
                                xmlfile.write(f"\n               <Time_Acquir>{item[58:61].strip().replace('&', '&amp;')}</Time_Acquir>")
                                xmlfile.write(f"\n               <Time_Offset></Time_Offset>")
                                xmlfile.write(f"\n               <Usg>{item[70:74].strip().replace('&', '&amp;')}</Usg>")
                                xmlfile.write(f"\n               <Ctr_Cde></Ctr_Cde>")
                                xmlfile.write(f"\n               <Location_Bldg></Location_Bldg>")
                                xmlfile.write(f"\n               <Location_Bin></Location_Bin>")
                                xmlfile.write(f"\n               <SA_Ind></SA_Ind>")
                                if len(temp[ind+1].strip()) < 30:
                                    xmlfile.write(f"\n               <note>{temp[ind+1].strip().replace('&', '&amp;')}</note>")
                                else:
                                    xmlfile.write(f"\n               <note></note>")
                                xmlfile.write('\n           </component>')
                                xmlfile.write('\n       </consumed>')
                            if len(item) == 94:
                                xmlfile.write('\n       <consumed>')
                                xmlfile.write('\n           <component>')
                                xmlfile.write(f"\n               <Trn></Trn>")
                                xmlfile.write(f"\n               <Line>{item[0:4].strip().replace('&', '&amp;')}</Line>")
                                xmlfile.write(f"\n               <Item>{item[8:16].strip().replace('&', '&amp;')}</Item>")
                                xmlfile.write(f"\n               <Item_Name>{item[17:38].strip().replace('&', '&amp;')}</Item_Name>")
                                xmlfile.write(f"\n               <Qty>{item[39:41].strip().replace('&', '&amp;')}</Qty>")
                                xmlfile.write(f"\n               <UM>{item[42:45].strip().replace('&', '&amp;')}</UM>")
                                xmlfile.write(f"\n               <SL_Ind>{item[47:50].strip().replace('&', '&amp;')}</SL_Ind>")
                                xmlfile.write(f"\n               <Inv_Ctl>{item[51:53].strip().replace('&', '&amp;')}</Inv_Ctl>")
                                xmlfile.write(f"\n               <Time_Acquir>{item[58:61].strip().replace('&', '&amp;')}</Time_Acquir>")
                                xmlfile.write(f"\n               <Time_Offset></Time_Offset>")
                                xmlfile.write(f"\n               <Usg>{item[70:74].strip().replace('&', '&amp;')}</Usg>")
                                xmlfile.write(f"\n               <Ctr_Cde>{item[74:79].strip().replace('&', '&amp;')}</Ctr_Cde>")
                                xmlfile.write(f"\n               <Location_Bldg>{item[79:86].strip().replace('&', '&amp;')}</Location_Bldg>")
                                xmlfile.write(
                                    f"\n               <Location_Bin>{item[86:len(item) - 1].strip().replace('&', '&amp;')}</Location_Bin>")
                                xmlfile.write(f"\n               <SA_Ind></SA_Ind>")
                                if len(temp[ind + 1].strip()) < 30:
                                    xmlfile.write(f"\n               <note>{temp[ind + 1].strip().replace('&', '&amp;')}</note>")
                                else:
                                    xmlfile.write(f"\n               <note></note>")
                                xmlfile.write('\n           </component>')
                                xmlfile.write('\n       </consumed>')

                        # used items
                        temp = p.split('Used Items:')
                        if len(temp) > 1:
                            temp = temp[1].strip().split('\n')
                            for item in temp:
                                item = item.strip()
                                if len(item) == 69:
                                    xmlfile.write('\n       <used>')
                                    xmlfile.write('\n           <component>')
                                    xmlfile.write(f"\n               <Trn></Trn>")
                                    xmlfile.write(f"\n               <Item>{item[0:15].strip().replace('&', '&amp;')}</Item>")
                                    xmlfile.write(f"\n               <Item_Name>{item[16:33].strip().replace('&', '&amp;')}</Item_Name>")
                                    xmlfile.write(f"\n               <Item_type>{item[35:47].strip().replace('&', '&amp;')}</Item_type>")
                                    xmlfile.write(f"\n               <Qty_opt>{item[49:54].strip().replace('&', '&amp;')}</Qty_opt>")
                                    xmlfile.write(f"\n               <UM>{item[54:58].strip().replace('&', '&amp;')}</UM>")
                                    xmlfile.write(f"\n               <Cnsm_Pct>{item[58:64].strip().replace('&', '&amp;')}</Cnsm_Pct>")
                                    xmlfile.write(f"\n               <Inv_Ctl>{item[64:68].strip().replace('&', '&amp;')}</Inv_Ctl>")
                                    xmlfile.write(f"\n               <Time_Acquir></Time_Acquir>")
                                    xmlfile.write(f"\n               <Time_Offset></Time_Offset>")
                                    xmlfile.write('\n           </component>')
                                    xmlfile.write('\n       </used>')

                        xmlfile.write('\n' + '   </processStep>')
                except Exception as e:
                    continue

            xmlfile.write('\n' + '</cell>')
            xmlfile.closed


if __name__ == "__main__":
    input = sys.argv[1:]
    print('Using file', input)
    main(input)
    print(f"Successfully generate output file")
