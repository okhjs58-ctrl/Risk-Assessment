import zipfile, os

SKILL = "C:/Users/okhjs/AppData/Roaming/Claude/local-agent-mode-sessions/skills-plugin/12e2784c-a698-4706-837f-0845af54230a/0f260110-086c-4859-aaad-eeb4a00af798/skills/hwpx"
OUT_DIR = "C:/Users/okhjs/돌봄위험성평가/test_hwpx"

# base header.xml 읽기
with open(f"{SKILL}/templates/base/Contents/header.xml", 'r', encoding='utf-8') as f:
    header = f.read()

# binDataList를 </hh:styles> 바로 뒤, </hh:refList> 바로 앞에 삽입
bin_data_xml = '<hh:binDataList itemCnt="1"><hh:binData id="BIN0001" format="png" compress="0" access="EMBEDDING" href="BinData/sig0.png"/></hh:binDataList>'

if '</hh:styles>' in header:
    header = header.replace('</hh:styles>', '</hh:styles>\n  ' + bin_data_xml)
    print("binDataList inserted after </hh:styles>")
else:
    print("ERROR: </hh:styles> not found in header!")
    print(header[-500:])

with open(f"{OUT_DIR}/header_test.xml", 'w', encoding='utf-8') as f:
    f.write(header)

# section0.xml, PNG 읽기
with open(f"{OUT_DIR}/section0_test.xml", 'r', encoding='utf-8') as f:
    section0 = f.read()
with open(f"{OUT_DIR}/sig0.png", 'rb') as f:
    png_data = f.read()

# base 템플릿 파일들
base_files = {}
base_root = f"{SKILL}/templates/base"
for root, dirs, files in os.walk(base_root):
    for fname in files:
        fpath = os.path.join(root, fname)
        rel = os.path.relpath(fpath, base_root).replace(os.sep, '/')
        with open(fpath, 'rb') as f:
            base_files[rel] = f.read()

# HWPX ZIP 생성
out_path = f"{OUT_DIR}/test_sig.hwpx"
with zipfile.ZipFile(out_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
    # mimetype must be first, STORED
    zi_mt = zipfile.ZipInfo('mimetype')
    zi_mt.compress_type = zipfile.ZIP_STORED
    zf.writestr(zi_mt, b'application/hwp+zip')

    # base 파일들 (mimetype, header.xml, section0.xml 제외)
    for rel, data in base_files.items():
        if rel in ('mimetype', 'Contents/header.xml', 'Contents/section0.xml'):
            continue
        zf.writestr(rel, data)

    # 수정된 header.xml
    zf.writestr('Contents/header.xml', header.encode('utf-8'))
    # 새 section0.xml
    zf.writestr('Contents/section0.xml', section0.encode('utf-8'))
    # PNG (STORED - compress="0" 에 맞춰)
    zi = zipfile.ZipInfo('BinData/sig0.png')
    zi.compress_type = zipfile.ZIP_STORED
    zf.writestr(zi, png_data)

print(f"HWPX written: {out_path}")
print(f"Size: {os.path.getsize(out_path)} bytes")

# ZIP 내용 확인
with zipfile.ZipFile(out_path) as zf:
    print("\nZIP contents:")
    for info in zf.infolist():
        ctype = "STORED" if info.compress_type == 0 else "DEFLATED"
        print(f"  [{ctype}] {info.filename} ({info.file_size} bytes)")
