"""Only exact known questions, normalized for spacing/case/punctuation, share a cache."""
from .retrieval import normalize

FAQ = {
    'projects': {'en':['What has Diana built?'], 'fr':['Quels projets Diana a-t-elle réalisés ?'], 'es':['¿Qué proyectos ha creado Diana?']},
    'ai': {'en':['How does she use AI?'], 'fr':['Comment utilise-t-elle l’IA ?'], 'es':['¿Cómo utiliza la IA?']},
    'art': {'en':['Tell me about her artistic side.'], 'fr':['Parle-moi de son côté artistique.'], 'es':['Cuéntame sobre su lado artístico.']},
    'languages': {'en':['What languages does Diana speak?'], 'fr':['Quelles langues parle Diana ?', 'Quelles sont les langues parlées par Diana ?'], 'es':['¿Qué idiomas habla Diana?']},
    'career': {'en':['Tell me about Diana’s experience.'], 'fr':['Quel est le parcours de Diana ?'], 'es':['¿Cuál es la experiencia de Diana?']},
    'certifications': {'en':['What certifications does Diana have?'], 'fr':['Quelles certifications possède Diana ?'], 'es':['¿Qué certificaciones tiene Diana?']},
    'education': {'en':['What did Diana study?'], 'fr':['Quelles études a fait Diana ?'], 'es':['¿Qué estudió Diana?']},
    'covea': {'en':['What technologies did Diana use at Covéa?'], 'fr':['Quelles technologies Diana a-t-elle utilisées chez Covéa ?'], 'es':['¿Qué tecnologías utilizó Diana en Covéa?']},
}


def match_faq(request):
    if request.history:
        return None
    for id, translations in FAQ.items():
        for question in translations[request.locale]:
            if normalize(question) == normalize(request.message):
                return id, translations[request.locale][0]
    return None
