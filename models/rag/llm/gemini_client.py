from ast import literal_eval
from typing import List

from google import genai
from app.main.model.dto.semantic_search_dto import SemanticSearchDTO
from google.genai import types


class GeminiContext:

    def __init__(self, search_dto: SemanticSearchDTO, relevance: float):
        self.search_dto = search_dto
        self.relevance = relevance

    def to_prompt(self, index):
        return f"Documento {index}: \tEMENTA: {self.search_dto.ementa}\n\tACÓRDÃO: {self.search_dto.acordao}\n\tSÚMULA: {self.search_dto.sumula}\n\tRELEVÂNCIA: {self.relevance}"

class GeminiClient:

    def __init__(self, gemini_api_key):
        self.gemini_api_key = gemini_api_key
        self.client = genai.Client(api_key=gemini_api_key)

    def rewrite_query_for_retrieval(self, query) -> str:

        prompt = f"""
            Você é um assistente jurídico especialista na jurisprudência brasileira.
            
            Para responder às questões a seguir, você fará uma busca em um banco de dados vetorial com jurisprudência do TJMG. Isso faz parte de um sistema RAG (Retrieval-Augmented Generation).
            
            Sua tarefa é transformar a consulta do usuário em um texto **curto, conciso e informativo**, no estilo de uma ementa do TJMG. A consulta deve conter **no máximo 30 palavras**, preferencialmente entre 10 e 20, e **sem linguagem coloquial ou explicações adicionais**.
            
            Exemplos:
            Consulta ruim: 'Oi, estou com um caso em que meu cliente foi negativado indevidamente por uma operadora de telecomunicações - mais especificamente a Vivo -, e queria saber quais são os argumentos mais comuns que os juízes do TJMG costumam aceitar para conceder danos morais?'
            Consulta boa: 'Negativação indevida por operadora de telecomunicações, operadora X'
            Você deve responder **apenas** com a consulta refinada, **sem aspas, sem pontuação extra e sem qualquer texto antes ou depois**. A resposta será usada diretamente por uma API.
        """

        response = self.client.models.generate_content(
            model='gemini-2.0-flash-lite',
            contents=query,
            config=types.GenerateContentConfig(
                system_instruction=prompt,
                max_output_tokens=30,
                temperature=0.4
            )
        )

        print(f"REFINED QUERY: {response.text}")

        return response.text


    def rate_ementa_relevances(self, ementas: List[str], initial_user_query: str) -> List[float]:
        prompt = f"""
        Você é um assistente jurídico especialista em jurisprudência brasileira.

        Você receberá vários conjuntos de documentos (ementa) do TJMG.

        Sua tarefa é avaliar, para cada conjunto, o quão relevante ele é para a consulta jurídica do usuário, explicitada abaixo.

        A relevância deve ser dada como um valor numérico contínuo entre 0 e 1, onde:

        0 significa totalmente irrelevante ou não relacionado;

        1 significa totalmente relevante e diretamente aplicável;

        valores intermediários indicam graus variados de relevância.

        Exemplos de respostas válidas: [0.0, 0.37, 0.85, 1.0]

        Não utilize apenas valores fixos pré-definidos. Seja preciso na avaliação e escolha a nota que melhor representa a relevância.

        Não escreva textos adicionais, apenas a lista no estilo Python com os valores para cada conjunto, na ordem em que foram apresentados.

        Conjuntos de documentos:

        {self._ementas_to_prompt(ementas)}

        [responda somente com uma lista numérica, exemplo: [0.92, 0.45, 0.0], SEM aspas, sem formatação extra, sem ``` (backticks), sem explicações.]
        """

        response = self.client.models.generate_content(
            model='gemini-2.0-flash',
            contents=initial_user_query,
            config=types.GenerateContentConfig(
                system_instruction=prompt,
                max_output_tokens=100,
                temperature=0.1
            )
        )

        print(f"EMENTA RELEVANCES: {response.text}")

        return literal_eval(response.text)

    def generate_answer_from_context(self, query: str, contexts: List[GeminiContext]) -> str:
        prompt = f"""
            Você é um assistente jurídico especialista em jurisprudência brasileira. Você receberá uma pergunta de um advogado sobre jurisprudência, junto com uma lista de documentos legais contendo Súmula, Ementa, Acórdão e um score de relevância para cada documento.
            
            Utilize as informações mais relevantes desses documentos para fundamentar sua resposta, mas também combine com seu conhecimento jurídico consolidado para elaborar uma resposta clara, completa e atualizada, que reflita a prática jurídica brasileira atual. A resposta deve ser precisa, profissional e contextualizada, explicando conceitos essenciais mesmo que não estejam explicitamente detalhados nos documentos, desde que estejam em consonância com o entendimento jurídico vigente.
            
            Não mencione nem insinue que a resposta foi gerada com base em documentos específicos ou em qualquer sistema de recuperação de informações. Forneça a resposta de forma genérica, preservando a confidencialidade e mantendo o foco no conteúdo útil para o advogado.
            
            Documentos:
            {self._contexts_to_prompt(contexts)}
        """

        response = self.client.models.generate_content(
            model='gemini-2.5-flash-preview-05-20',
            contents=query,
            config=types.GenerateContentConfig(
                system_instruction=prompt,
                max_output_tokens=16384,
                temperature=0.2
            )
        )

        return response.text

    def _ementa_to_prompt(self, ementa: str, index: int):
        return f'Ementa {index}: {ementa}\n'

    def _ementas_to_prompt(self, ementas: List[str]):
        return '\n'.join(self._ementa_to_prompt(ementa, i) for i, ementa in enumerate(ementas)) + '\n'

    def _contexts_to_prompt(self, contexts: List[GeminiContext]):
        return '\n'.join(context.to_prompt(i + 1) for i, context in enumerate(contexts)) + '\n'
