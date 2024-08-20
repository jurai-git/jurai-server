import re

# Padrões para o Regex
pattern_list = [r'^.*?EMENTA:', r'(?<=\n)\d+(?=\n)', r'Tribunal de Justiça de Minas Gerais\n']

def get_ementa(doc_text):
    value = re.sub('|'.join(pattern_list), '', doc_text, flags=re.DOTALL)

    # Encontra a ementa e separa as estrofes
    menu_text = re.sub(r'(.*?)A\s+C\s+Ó\s+R\s+D\s+Ã\s+O.*', r'\1', value, flags=re.DOTALL)
    split = menu_text.split('\n\n')

    # Retira, caso tenha mais de uma estrofe, informações dispensáveis
    menu_text = ' '.join(split[:-1]) if len(split) != 1 else menu_text.join(split)
    return menu_text2