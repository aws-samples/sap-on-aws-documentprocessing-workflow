import boto3
import csv as _csv

import io
import os

s3         = boto3.resource('s3')
s3client   = boto3.client('s3')


def main(payload):
    print('parsing Document...')
# Key value mpa for FORM blocks
    key_map, value_map, block_map = get_kv_map(payload['Blocks'])
    kvs = get_kv_relationship(key_map, value_map, block_map)
# Get table data for Table Blocks
    table_datadict = get_table_results(payload['Blocks'])
    orderitems=[]
    salesorderitem={}
    ordernumber=''
    jsonln = io.StringIO()
    i=0
# Retrieve order number
    for key, value in kvs.items():
        if (key == "Sales Order Number"):
            ordernumber = value
    
    databucket = os.environ.get('DATA_BUCKET')

    if(search_orders(bucketname=databucket,order=ordernumber)):
    # check if order exists in the data lake
    # Order Details
        for item in table_datadict:
            i = i + 1
            salesorderitem["SalesOrder"] = ordernumber
            salesorderitem["SalesOrderItem"] = str(i * 10)
            salesorderitem["RequestedQuantity"] = str(item["Qty "]).replace(" ","")
            orderitems.append(salesorderitem.copy())
        
        return {
            "order": ordernumber,
            "orderitems": orderitems,
            "orderfound": "TRUE"
          }
    else:
        return {
            "order": ordernumber,
            "orderitems": orderitems,
            "orderfound": "FALSE"
        }


def search_orders(bucketname:str,order:str):
    bucket = s3.Bucket(bucketname)
    query_result = False
    for object_summary in bucket.objects.filter():
    #print(object_summary.key)
        resp = s3client.select_object_content(
            Bucket=bucket.name,
            Key=object_summary.key,
            Expression="'".join(["SELECT s.VBELN FROM s3object s where s.VBELN=",order,""]),
            ExpressionType='SQL',
            InputSerialization={'JSON': {'Type': 'Lines'}},
            OutputSerialization={'JSON': {}}
        )

        if query_result == True:
            break
        
        for event in resp['Payload']:
            if 'Records' in event:
                query_result = True
                print(query_result)

    return query_result

def get_kv_map(blocks):
    key_map = {}
    value_map = {}
    block_map = {}
    for block in blocks:
        block_id = block['Id']
        block_map[block_id] = block
        if block['BlockType'] == "KEY_VALUE_SET":
            if 'KEY' in block['EntityTypes']:
                key_map[block_id] = block
            else:
                value_map[block_id] = block
           
    return key_map, value_map, block_map

def get_kv_relationship(key_map, value_map, block_map):
    kvs = {}
    for block_id, key_block in key_map.items():
        value_block = find_value_block(key_block, value_map)
        key = get_text(key_block, block_map).strip()
        val = get_text(value_block, block_map).strip()
        if key[-1] == ':':
            key = key[:-1]
        
        kvs[key] = val
    return kvs
def find_value_block(key_block, value_map):
    for relationship in key_block['Relationships']:
        if relationship['Type'] == 'VALUE':
            for value_id in relationship['Ids']:
                value_block = value_map[value_id]
    return value_block
def get_text(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] == 'SELECTED':
                            text += 'X '    
    return text

def handler(event,context):
    result = main(payload=event)

    return result
 

def get_table_results(blocks):
    blocks_map = {}
    table_blocks = []
    for block in blocks:
        blocks_map[block['Id']] = block
        if block['BlockType'] == "TABLE":
            table_blocks.append(block)

    if len(table_blocks) <= 0:
        return "<b> NO Table FOUND </b>"

    table_data=[]
    for index, table in enumerate(table_blocks):
        if index == 1:
            table_data = generate_table_dict(table, blocks_map, index + 1)
            return table_data
def generate_table_dict(table_result, blocks_map, table_index):
    rows = get_rows_columns_map(table_result, blocks_map)

    table_id = 'Table_' + str(table_index)
    columns=[]
    data=[]
    output = io.StringIO()
    table_data=[]
    if table_index == 2:
        for row_index, cols in rows.items():
            columns.clear() 
            for col_index, text in cols.items():
                columns.append(text)
            row = "|".join(columns)
            data.append(row)
            
        csvdictreader = _csv.DictReader(data,delimiter='|')
   
        for records in csvdictreader:
            if (records["Material "] != "" ):
                table_data.append(records)
                
    return table_data
def get_rows_columns_map(table_result, blocks_map):
    rows = {}
    for relationship in table_result['Relationships']:
        if relationship['Type'] == 'CHILD':
            for child_id in relationship['Ids']:
                try:
                    cell = blocks_map[child_id]
                    if cell['BlockType'] == 'CELL':
                       
                        row_index = cell['RowIndex']
                        col_index = cell['ColumnIndex']
                        if row_index not in rows:
                            # create new row
                            rows[row_index] = {}
                        # get the text value
                        rows[row_index][col_index] = get_text(cell, blocks_map)
                except KeyError:
                    print("Error extracting Table data - {}:".format(KeyError))
                    pass
    return rows


