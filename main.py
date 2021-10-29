from lxml import etree
from io import StringIO
import verovio

tk = verovio.toolkit()
version = tk.getVersion()
print(version)

tk.loadFile('AWG_I_5_3rd_proof_MusicXMLausFinale.musicxml')
tk.setScale(100)
tk.redoLayout()
tk.renderToSVGFile( "page.svg", 65 )

result = tk.getMEI()

with open ('AWG_I_5_3rd_proof_MusicXMLausFinale.mei', 'w', encoding='utf-8') as output:  # add encoding to avoid unicode issues: https://stackoverflow.com/a/16347110
    output.write(result)


# file = ('AWG_I_5_3rd_proof_MusicXMLausFinale.musicxml')
# tree = etree.parse(file)
# processed = tree.xpath('//processing-instruction()')

# root = tree.getroot()
# print(root.tag)


# for note in root.iter('note'):
#     print(note.attrib)
#          # print(element.text)







