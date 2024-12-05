# AF360 Bank Portal

Portal de redirecionamento para os sistemas internos do AF360 Bank.

## Descrição

Este projeto é um portal web desenvolvido em Flask que serve como ponto central de acesso para os diferentes sistemas do AF360 Bank:
- Sistema de Comissões (comissoes.af360bank.online)
- Sistema Financeiro (financeiro.af360bank.online)

## Tecnologias Utilizadas

- Python 3.8+
- Flask 2.3.3
- HTML5/CSS3
- Gunicorn (para deploy)

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITORIO]
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
python app.py
```

## Deploy

A aplicação está configurada para deploy na plataforma Render, com redirecionamento automático para os subdomínios específicos de cada sistema.

## Estrutura do Projeto

```
.
├── app.py              # Aplicação principal Flask
├── requirements.txt    # Dependências do projeto
└── templates/         
    └── index.html     # Template da página principal
```
