# JS 코드가 생성하는 것과 동일한 구조로 HWPX 생성 (검증용)
import zipfile, os, struct, zlib

SKILL = "C:/Users/okhjs/AppData/Roaming/Claude/local-agent-mode-sessions/skills-plugin/12e2784c-a698-4706-837f-0845af54230a/0f260110-086c-4859-aaad-eeb4a00af798/skills/hwpx"
OUT_DIR = "C:/Users/okhjs/돌봄위험성평가/test_hwpx"

# PNG 생성 (서명 시뮬레이션: 420x180 빨간 이미지)
def make_png(w=420, h=180):
    def chunk(name, data):
        c = struct.pack('>I', len(data)) + name + data
        return c + struct.pack('>I', zlib.crc32(c[4:]) & 0xffffffff)
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    rows = b''
    for _ in range(h):
        rows += b'\x00' + b'\xff\x00\x00' * w
    idat = zlib.compress(rows)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', idat)
    png += chunk(b'IEND', b'')
    return png

png_data = make_png()

# JS 코드와 동일한 XML 생성
container_xml = """<?xml version='1.0' encoding='UTF-8'?><ocf:container xmlns:ocf="urn:oasis:names:tc:opendocument:xmlns:container" xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf"><ocf:rootfiles><ocf:rootfile full-path="Contents/content.hpf" media-type="application/hwpml-package+xml"/><ocf:rootfile full-path="Preview/PrvText.txt" media-type="text/plain"/><ocf:rootfile full-path="META-INF/container.rdf" media-type="application/rdf+xml"/></ocf:rootfiles></ocf:container>"""

container_rdf = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about=""><ns0:hasPart xmlns:ns0="http://www.hancom.co.kr/hwpml/2016/meta/pkg#" rdf:resource="Contents/header.xml"/></rdf:Description><rdf:Description rdf:about="Contents/header.xml"><rdf:type rdf:resource="http://www.hancom.co.kr/hwpml/2016/meta/pkg#HeaderFile"/></rdf:Description><rdf:Description rdf:about=""><ns0:hasPart xmlns:ns0="http://www.hancom.co.kr/hwpml/2016/meta/pkg#" rdf:resource="Contents/section0.xml"/></rdf:Description><rdf:Description rdf:about="Contents/section0.xml"><rdf:type rdf:resource="http://www.hancom.co.kr/hwpml/2016/meta/pkg#SectionFile"/></rdf:Description><rdf:Description rdf:about=""><rdf:type rdf:resource="http://www.hancom.co.kr/hwpml/2016/meta/pkg#Document"/></rdf:Description></rdf:RDF>"""

content_hpf = """<?xml version='1.0' encoding='UTF-8'?><opf:package xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph" xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core" xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf/" version="" unique-identifier="" id=""><opf:metadata><opf:title>테스트 위험성평가</opf:title><opf:language>ko</opf:language><opf:meta name="creator" content="홍길동"/><opf:meta name="subject" content="text"/><opf:meta name="description" content="text"/><opf:meta name="lastsaveby" content="text"/><opf:meta name="CreatedDate" content="2026-05-18"/><opf:meta name="ModifiedDate" content="text"/><opf:meta name="date" content="text"/><opf:meta name="keyword" content="text"/></opf:metadata><opf:manifest><opf:item id="header" href="Contents/header.xml" media-type="application/xml"/><opf:item id="section0" href="Contents/section0.xml" media-type="application/xml"/><opf:item id="settings" href="settings.xml" media-type="application/xml"/></opf:manifest><opf:spine><opf:itemref idref="header" linear="yes"/><opf:itemref idref="section0" linear="yes"/></opf:spine></opf:package>"""

version_xml = """<?xml version='1.0' encoding='UTF-8'?><hv:HCFVersion xmlns:hv="http://www.hancom.co.kr/hwpml/2011/version" tagetApplication="WORDPROCESSOR" major="5" minor="1" micro="1" buildNumber="0" os="1" xmlVersion="1.5" application="Hancom Office Hangul" appVersion="13, 0, 0, 1408 WIN32LEWindows_10"/>"""

settings_xml = """<?xml version='1.0' encoding='UTF-8'?><ha:HWPApplicationSetting xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0"><ha:CaretPosition listIDRef="0" paraIDRef="0" pos="0"/></ha:HWPApplicationSetting>"""

manifest_xml = """<?xml version='1.0' encoding='UTF-8'?><odf:manifest xmlns:odf="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"/>"""

prv_text = "문화재돌봄 작업 위험성 평가표\n문화재명: 테스트\n작업일자: 2026-05-18\n작업자명: 홍길동"

# header.xml: base + binDataList
with open(f"{SKILL}/templates/base/Contents/header.xml", 'r', encoding='utf-8') as f:
    header = f.read()
bin_data_xml = '<hh:binDataList itemCnt="1"><hh:binData id="BIN0001" format="png" compress="0" access="EMBEDDING" href="BinData/sig0.png"/></hh:binDataList>'
header = header.replace('</hh:styles>', '</hh:styles>\n  ' + bin_data_xml)

# section0.xml: hp:pic 포함 (JS 코드와 동일한 구조)
img_w = 12000
img_h = int(img_w * 180 / 420)
section0 = f"""<?xml version='1.0' encoding='UTF-8'?>
<hs:sec xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph"
        xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section"
        xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core"
        xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head">
<hp:p id="1000000001" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
  <hp:run charPrIDRef="0">
    <hp:secPr id="" textDirection="HORIZONTAL" spaceColumns="1134" tabStop="8000" tabStopVal="4000" tabStopUnit="HWPUNIT" outlineShapeIDRef="1" memoShapeIDRef="0" textVerticalWidthHead="0" masterPageCnt="0">
      <hp:grid lineGrid="0" charGrid="0" wonggojiFormat="0"/>
      <hp:startNum pageStartsOn="BOTH" page="0" pic="0" tbl="0" equation="0"/>
      <hp:visibility hideFirstHeader="0" hideFirstFooter="0" hideFirstMasterPage="0" border="SHOW_ALL" fill="SHOW_ALL" hideFirstPageNum="0" hideFirstEmptyLine="0" showLineNumber="0"/>
      <hp:lineNumberShape restartType="0" countBy="0" distance="0" startNumber="0"/>
      <hp:pagePr landscape="WIDELY" width="59528" height="84186" gutterType="LEFT_ONLY">
        <hp:margin header="4252" footer="4252" gutter="0" left="8504" right="8504" top="5668" bottom="4252"/>
      </hp:pagePr>
      <hp:footNotePr>
        <hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/>
        <hp:noteLine length="-1" type="SOLID" width="0.12 mm" color="#000000"/>
        <hp:noteSpacing betweenNotes="283" belowLine="567" aboveLine="850"/>
        <hp:numbering type="CONTINUOUS" newNum="1"/>
        <hp:placement place="EACH_COLUMN" beneathText="0"/>
      </hp:footNotePr>
      <hp:endNotePr>
        <hp:autoNumFormat type="DIGIT" userChar="" prefixChar="" suffixChar=")" supscript="0"/>
        <hp:noteLine length="14692344" type="SOLID" width="0.12 mm" color="#000000"/>
        <hp:noteSpacing betweenNotes="0" belowLine="567" aboveLine="850"/>
        <hp:numbering type="CONTINUOUS" newNum="1"/>
        <hp:placement place="END_OF_DOCUMENT" beneathText="0"/>
      </hp:endNotePr>
      <hp:pageBorderFill type="BOTH" borderFillIDRef="1" textBorder="PAPER" headerInside="0" footerInside="0" fillArea="PAPER">
        <hp:offset left="1417" right="1417" top="1417" bottom="1417"/>
      </hp:pageBorderFill>
    </hp:secPr>
    <hp:ctrl>
      <hp:colPr id="" type="NEWSPAPER" layout="LEFT" colCount="1" sameSz="1" sameGap="0"/>
    </hp:ctrl>
  </hp:run>
  <hp:run charPrIDRef="0"><hp:t/></hp:run>
</hp:p>
<hp:p id="1000000002" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
  <hp:run charPrIDRef="0"><hp:t>홍길동 서명:</hp:t></hp:run>
</hp:p>
<hp:p id="1000000003" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
  <hp:run charPrIDRef="0"><hp:pic id="1000000004" name="그림 1" zOrder="1" numberingType="PICTURE" textWrap="TOP_AND_BOTTOM" textFlow="BOTH_SIDES" lock="0" dropcapstyle="None"><hp:inst binData="BIN0001" flip="NONE"><hp:img imgContourCheck="0" imgEditType="REALPATH" imgEditEffect="0"/></hp:inst><hp:sz width="{img_w}" height="{img_h}" protect="0"/><hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/><hp:outMargin left="0" right="0" top="0" bottom="0"/><hp:caption><hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" textWidth="{img_w}" textHeight="0" hasTextRef="0" hasNumRef="0"><hp:p id="1000000005" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0"><hp:run charPrIDRef="0"><hp:t/></hp:run></hp:p></hp:subList><hp:sz width="{img_w}" height="0" protect="0"/><hp:pos treatAsChar="1" affectLSpacing="0" flowWithText="1" allowOverlap="0" holdAnchorAndSO="0" vertRelTo="PARA" horzRelTo="COLUMN" vertAlign="TOP" horzAlign="LEFT" vertOffset="0" horzOffset="0"/><hp:outMargin left="0" right="0" top="0" bottom="0"/><hp:captionAttr side="BOTTOM" fullSz="0" lineGap="850" indentSz="0" maxSz="0"/></hp:caption></hp:pic></hp:run>
</hp:p>
<hp:p id="1000000006" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">
  <hp:run charPrIDRef="0"><hp:t/></hp:run>
</hp:p>
</hs:sec>"""

# HWPX ZIP 생성
out_path = f"{OUT_DIR}/test_js_equiv.hwpx"
with zipfile.ZipFile(out_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
    # mimetype STORED first
    zi_mt = zipfile.ZipInfo('mimetype')
    zi_mt.compress_type = zipfile.ZIP_STORED
    zf.writestr(zi_mt, b'application/hwp+zip')

    zf.writestr('META-INF/container.xml', container_xml.encode('utf-8'))
    zf.writestr('META-INF/container.rdf', container_rdf.encode('utf-8'))
    zf.writestr('META-INF/manifest.xml', manifest_xml.encode('utf-8'))
    zf.writestr('version.xml', version_xml.encode('utf-8'))
    zf.writestr('settings.xml', settings_xml.encode('utf-8'))
    zf.writestr('Contents/content.hpf', content_hpf.encode('utf-8'))
    zf.writestr('Contents/header.xml', header.encode('utf-8'))
    zf.writestr('Contents/section0.xml', section0.encode('utf-8'))
    # PNG STORED
    zi = zipfile.ZipInfo('BinData/sig0.png')
    zi.compress_type = zipfile.ZIP_STORED
    zf.writestr(zi, png_data)
    zf.writestr('Preview/PrvText.txt', prv_text.encode('utf-8'))

print(f"Written: {out_path} ({os.path.getsize(out_path)} bytes)")

with zipfile.ZipFile(out_path) as zf:
    print("\nZIP contents:")
    for info in zf.infolist():
        ctype = "STORED" if info.compress_type == 0 else "DEFLATED"
        print(f"  [{ctype}] {info.filename} ({info.file_size} bytes)")
