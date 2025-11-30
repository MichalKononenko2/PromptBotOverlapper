#!/usr/bin/env python3
import sys

def escape( str_xml: str ):
    str_xml = str_xml.replace("&", "&amp;")
    str_xml = str_xml.replace("<", "&lt;")
    str_xml = str_xml.replace(">", "&gt;")
    str_xml = str_xml.replace("\"", "&quot;")
    str_xml = str_xml.replace("'", "&apos;")
    return str_xml

if __name__ == '__main__':
    print("Enter what to write. Press Ctrl + D when done. : ")
    assignment = sys.stdin.readlines()
    print("Enter text. Press Ctrl + D when done. : ")
    response = sys.stdin.readlines()
    print(f'''
Your task is to determine whether a response string denoted by <response> in the XML schema
defintion below matches the assignment string denoted by <assignment>. Your output must be a
value <grade> between 0 and 1. The XML schemas for the input you will receive, and the output
you must produce are given below. Any response you give must comply with the XSD for a response.

```xml
<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="document">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="assignment" type="xs:string"/>
        <xs:element name="response" type="xs:string"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>
```

```xml
<?xml version="1.0"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="grade">
    <xs:simpleType>
      <xs:restriction base="xs:float">
        <xs:minInclusive value="0"/>
        <xs:maxInclusive value="1"/>
      </xs:restriction>
    </xs:simpleType>
  </xs:element>
</xs:schema>
```

Your input is below. What is your response?

```xml
<document>
  <assignment>{escape(''.join(assignment))}</assignment>
  <response>{escape(''.join(response))}</response>
</document>
```
'''
  )
