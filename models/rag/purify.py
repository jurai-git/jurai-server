import re

def preprocess_acordao(acordao: str):
  acordao = acordao.lower().replace('\n', ' ').replace('\r', '')
  acordao = re.sub(r'\s+', ' ', acordao)

  # tirar elipses ([...] e (...))
  acordao = re.sub(r'\(\.\.\.\)', '', acordao)
  acordao = re.sub(r'\[\.\.\.\]', '', acordao)

  return acordao.strip()

def preprocess_ementa(ementa: str):
  ementa = ementa.lower().replace('\n', ' ').replace('\r', '')
  ementa = re.sub(r'\s+', ' ', ementa)

  # tirar - antes de ; (por exemplo: )
  ementa = re.sub(r'(^|\s)-\s+', r'\1; ', ementa)

  # substituir  - por ; (e.g. no comeco da ementa)
  ementa = ementa.replace(' - ', '; ')

  # tirar elipses ([...] e (...))
  ementa = re.sub(r'\(\.\.\.\)', '', ementa)
  ementa = re.sub(r'\[\.\.\.\]', '', ementa)

  return ementa.strip()

def preprocess_sumula(sumula: str):
  return sumula.lower().replace('\n', ' ').replace('\r', '')

def preprocess_semantic_search(semantic_search: str):
  return semantic_search.lower().replace('\n', ' ').replace('\r', '')