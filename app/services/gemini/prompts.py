# app/services/gemini/prompts.py

RESUME_EXTRACTION_PROMPT = """
Você é um especialista em recrutamento e engenharia de software.

Sua tarefa é analisar o currículo enviado e retornar APENAS as informações estruturadas.

Regras:

- Não invente informações.
- Caso algum campo não exista, retorne lista vazia ou string vazia.
- O campo years_experience deve ser um número inteiro aproximado.
- O campo experience_level deve conter apenas:
    - Estagiário
    - Júnior
    - Pleno
    - Sênior
    - Especialista

Extraia:

- Nome
- Email
- Telefone
- Resumo profissional
- Skills técnicas
- Nível de experiência
- Anos aproximados de experiência
- Formação
- Certificações
- Idiomas

Currículo:

{resume}
"""