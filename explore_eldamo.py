"""
explore_eldamo2.py — Explora a estrutura do XML principal para encontrar
os word entries do Sindarin com glosas em inglês.
"""
import xml.etree.ElementTree as ET

tree = ET.parse("eldamo-data.xml")
root = tree.getroot()

# Os word-entries no Eldamo provavelmente são filhos diretos de 'language'
# Vamos encontrar o elemento language para Sindarin
for elem in root.iter("language"):
    lang_id = elem.get("id", "")
    lang_name = elem.get("name", "")
    if "sindarin" in lang_name.lower() or lang_id == "s":
        print(f"LANGUAGE: id={lang_id!r} name={lang_name!r}")
        children = list(elem)
        print(f"  Filhos: {len(children)}")
        # Mostrar primeiros filhos
        for i, child in enumerate(children[:5]):
            print(f"  child {i}: tag={child.tag} attrib={child.attrib}")
            for subchild in list(child)[:4]:
                print(f"    subchild: {subchild.tag} | {subchild.attrib} | text={subchild.text!r}")
        break

# Também verificar estrutura geral de 'ref' elements que têm l=s
print("\n--- ref elements with l=s ---")
for i, elem in enumerate(root.iter("ref")):
    if elem.get("l") == "s":
        parent = None
        for p in root.iter():
            if elem in list(p):
                parent = p
                break
        print(f"ref: {elem.attrib} parent_tag={parent.tag if parent else '?'} parent_attrib={parent.attrib if parent else '?'}")
        if i > 3:
            break
